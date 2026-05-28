# TaskHive: NVIDIA NIM Client
# Replaces Google Antigravity SDK with NVIDIA NIM's OpenAI-compatible API.
# Supports agentic reasoning with automatic rate-limit retries.
# Default model : meta/llama-3.3-70b-instruct (free tier)
# Endpoint      : https://integrate.api.nvidia.com/v1

import asyncio
import inspect
import json
import os
import re
from typing import Any, Callable
from openai import RateLimitError

from openai import AsyncOpenAI

# ── NIM Configuration ──────────────────────────────────────────────────────────
NIM_BASE_URL    = "https://integrate.api.nvidia.com/v1"
NIM_MODEL       = "meta/llama-3.3-70b-instruct"   # Free model with strong function-call support
MAX_TOOL_ROUNDS = 4                                # Max tool-call rounds (keeps API usage low)
MAX_RETRIES     = 3                                # Retries on 429 rate-limit
RETRY_BASE_WAIT = 20                               # Base wait seconds: 20s → 40s → 80s


# ── Type → JSON Schema helper ──────────────────────────────────────────────────
def _annotation_to_schema(annotation: Any) -> dict:
    """Convert a Python type annotation to a JSON Schema type dict."""
    if annotation in (str, inspect.Parameter.empty):
        return {"type": "string"}
    if annotation == int:
        return {"type": "integer"}
    if annotation == float:
        return {"type": "number"}
    if annotation == bool:
        return {"type": "boolean"}
    if annotation in (list, "list"):
        return {"type": "array", "items": {"type": "string"}}
    if annotation in (dict, "dict"):
        return {"type": "object"}
    # Handle Optional[X] / list[X] style annotations via string repr
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        return {"type": "array", "items": {"type": "string"}}
    if origin is dict:
        return {"type": "object"}
    return {"type": "string"}


def _parse_docstring_args(docstring: str) -> dict[str, str]:
    """Extract arg descriptions from a Google-style docstring Args: section."""
    arg_descs: dict[str, str] = {}
    if not docstring:
        return arg_descs

    in_args = False
    for line in docstring.splitlines():
        stripped = line.strip()
        if stripped == "Args:":
            in_args = True
            continue
        if in_args:
            if stripped.startswith(("Returns:", "Raises:", "Yields:", "Note:", "Example")):
                break
            # Match "arg_name: description" or "arg_name (type): description"
            m = re.match(r"^(\w+)(?:\s*\([^)]*\))?\s*:\s*(.+)$", stripped)
            if m:
                arg_descs[m.group(1)] = m.group(2).strip()

    return arg_descs


def function_to_tool_schema(fn: Callable) -> dict:
    """
    Convert a Python function to an OpenAI-compatible tool schema.

    Reads the function signature and Google-style docstring to produce
    the full JSON Schema description NIM needs.
    """
    sig = inspect.signature(fn)
    raw_doc = inspect.getdoc(fn) or fn.__name__
    description = raw_doc.splitlines()[0].strip()
    arg_descs = _parse_docstring_args(raw_doc)

    properties: dict[str, dict] = {}
    required: list[str] = []

    for name, param in sig.parameters.items():
        if name in ("self", "ctx", "context"):
            continue
        prop = _annotation_to_schema(param.annotation)
        prop["description"] = arg_descs.get(name, f"The {name} parameter.")
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# ── NIM Agent ──────────────────────────────────────────────────────────────────
class NIMAgent:
    """NIM-backed agent with function-call loop and retry logic."""

    def __init__(
        self,
        api_key: str,
        system_instructions: str,
        tools: list[Callable] | None = None,
        model: str = NIM_MODEL,
    ):
        self.client = AsyncOpenAI(
            base_url=NIM_BASE_URL,
            api_key=api_key,
        )
        self.model = model
        self.system_instructions = system_instructions

        # Build tool schemas and callable map
        self._tools: list[Callable] = tools or []
        self._tool_schemas: list[dict] = [
            function_to_tool_schema(fn) for fn in self._tools
        ]
        self._tool_map: dict[str, Callable] = {fn.__name__: fn for fn in self._tools}

    def _call_tool(self, name: str, args: dict) -> str:
        """Execute a tool function and return its result as a JSON string."""
        fn = self._tool_map.get(name)
        if not fn:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            result = fn(**args)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def run(self, user_prompt: str) -> str:
        """Send prompt to NIM, run function-call loop, return final text response."""
        messages: list[dict] = [
            {"role": "system", "content": self.system_instructions},
            {"role": "user",   "content": user_prompt},
        ]

        for _round in range(MAX_TOOL_ROUNDS):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 2048,
                "temperature": 0.2,
            }
            if self._tool_schemas:
                kwargs["tools"] = self._tool_schemas
                kwargs["tool_choice"] = "auto"

            # ── NIM API call with exponential-backoff retry (handles 429) ──────
            response = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = await self.client.chat.completions.create(**kwargs)
                    break  # success — exit retry loop
                except RateLimitError as rle:
                    if attempt == MAX_RETRIES:
                        # Re-raise as a plain Exception so orchestrator fallback can detect '429'
                        raise Exception(f"Error code: 429 - rate limit exhausted after {MAX_RETRIES} retries") from rle
                    wait = RETRY_BASE_WAIT * (2 ** (attempt - 1))
                    print(f"[NIM] Rate limit hit (attempt {attempt}/{MAX_RETRIES}). Retrying in {wait}s…")
                    await asyncio.sleep(wait)
            choice = response.choices[0]
            message = choice.message


            # No more tool calls → return the text
            if not message.tool_calls:
                return message.content or ""

            # Append assistant's tool-call message
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool call and append results
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result_str = self._call_tool(tc.function.name, args)
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_str,
                })

        # Exceeded max rounds — ask for a plain summary
        messages.append({
            "role": "user",
            "content": "Please summarise your findings so far in a clear, concise response.",
        })
        try:
            final = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.2,
            )
            return final.choices[0].message.content or ""
        except RateLimitError as rle:
            raise Exception("Error code: 429 - rate limit on summary call") from rle


def get_nim_client(api_key: str | None = None) -> AsyncOpenAI:
    """Return a raw OpenAI client pointed at NVIDIA NIM (for simple calls)."""
    key = api_key or os.environ.get("NVIDIA_API_KEY", "")
    return AsyncOpenAI(base_url=NIM_BASE_URL, api_key=key)
