"""
TaskHive — Orchestrator Agent (NVIDIA NIM Edition)
Coordinates all 5 specialized agents using meta/llama-3.3-70b-instruct via NIM.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agents.nim_client import NIMAgent, NIM_MODEL
from tools.task_tools import parse_user_intent, create_task_plan
from tools.security_tools import check_url_safety, check_domain_reputation
from tools.web_tools import (
    search_booking_websites,
    extract_movie_listings,
    navigate_to_seat_selection,
    fill_booking_form,
)
from tools.payment_tools import (
    calculate_total_amount,
    check_budget_constraint,
    simulate_payment,
    generate_booking_reference,
)

# ── System instructions ───────────────────────────────────────────────────────

ORCHESTRATOR_SYSTEM_INSTRUCTIONS = """
You are the Orchestrator of TaskHive — a secure multi-agent AI system powered by NVIDIA NIM.

You coordinate a swarm of specialized agents to safely complete real-world web tasks:
1. 🧠 Planner Agent   — decomposes tasks into steps
2. 🔒 Security Agent  — validates website safety
3. 🌐 Web Navigator   — browses and extracts data
4. ✅ Decision Agent  — validates options against constraints
5. 💳 Payment Agent   — simulates safe payment

Your orchestration flow for any task:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1 — PLANNING
  → Parse user intent (extract constraints, preferences)
  → Create execution plan with numbered steps

PHASE 2 — SECURITY SCAN
  → Identify target websites
  → Run security checks on all URLs
  → Only proceed if trust score ≥ 60

PHASE 3 — WEB NAVIGATION
  → Search for available options
  → Extract listings matching user preferences
  → Select seats/slots

PHASE 4 — DECISION & VALIDATION
  → Calculate exact total cost (with fees/taxes)
  → Verify ALL user constraints are met
  → Present clear summary

PHASE 5 — PAYMENT (after user approval)
  → Simulate payment flow
  → Generate booking confirmation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

At each phase, announce which agent is active with its emoji prefix.
Always show progress clearly. Be thorough, safe, and professional.
After the Decision phase, ALWAYS ask: "✅ Shall I proceed with the simulated payment? (Yes/No)"
"""

ALL_TOOLS = [
    parse_user_intent,
    create_task_plan,
    check_url_safety,
    check_domain_reputation,
    search_booking_websites,
    extract_movie_listings,
    navigate_to_seat_selection,
    fill_booking_form,
    calculate_total_amount,
    check_budget_constraint,
    simulate_payment,
    generate_booking_reference,
]


def _get_api_key() -> str:
    key = os.environ.get("NVIDIA_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "NVIDIA_API_KEY is not set.\n"
            "Get your free key at: https://build.nvidia.com → Get API Key\n"
            "Then add it to your .env file: NVIDIA_API_KEY=nvapi-..."
        )
    return key


def get_orchestrator() -> NIMAgent:
    """Creates and returns the NIM-powered Orchestrator Agent with all tools."""
    return NIMAgent(
        api_key=_get_api_key(),
        system_instructions=ORCHESTRATOR_SYSTEM_INSTRUCTIONS,
        tools=ALL_TOOLS,
        model=NIM_MODEL,
    )


# ── Phase prompts ─────────────────────────────────────────────────────────────

def _phase1_prompt(user_task: str) -> str:
    return f"""[🧠 PLANNER AGENT] Starting task analysis.

User Task: "{user_task}"

Phase 1 — Planning:
1. Use parse_user_intent to extract structured intent from the task
2. Use create_task_plan to generate the step-by-step execution plan
3. Identify which websites will be needed for security scanning

Show the complete structured plan."""


def _phase2_prompt() -> str:
    return """[🔒 SECURITY AGENT] Starting security validation.

Phase 2 — Security:
1. Run check_url_safety on: https://bookmyshow.com, https://pvrinemas.com, https://inoxmovies.com
2. Run check_domain_reputation on each domain
3. Assign a trust score and verdict to each
4. Give an overall security recommendation

Only URLs with trust score ≥ 60 should be used."""


def _phase3_prompt(user_task: str) -> str:
    return f"""[🌐 WEB NAV AGENT] Starting web navigation.

Original task: "{user_task}"
Security-cleared website: https://bookmyshow.com

Phase 3 — Navigation:
1. Use search_booking_websites to confirm the right platform
2. Use extract_movie_listings for the movie/item with the correct date, time, city
3. Find the BEST option within the user's budget
4. Use navigate_to_seat_selection for that show (num_tickets from the parsed intent)
5. Use fill_booking_form with: name='TaskHive Demo User', email='demo@taskhive.ai', phone='9876543210'

Show all options and clearly highlight the best choice."""


def _phase4_prompt(user_task: str) -> str:
    return f"""[✅ DECISION AGENT] Performing validation and cost calculation.

Original task: "{user_task}"

Phase 4 — Decision:
1. Use calculate_total_amount for the chosen option (price per seat × quantity)
2. Use check_budget_constraint to verify against the user's budget limit
3. Present a complete BOOKING SUMMARY table with all details
4. List every constraint and whether it is MET ✅ or FAILED ❌
5. End with: "✅ Shall I proceed with the simulated payment? (Yes/No)" """


def _phase5_prompt() -> str:
    return """[💳 PAYMENT AGENT] User has approved. Processing simulated payment.

Phase 5 — Payment:
1. Use simulate_payment with:
   - booking_details: {"category": "movies", "provider": "BMS", "seats": ["D5","D6"], "quantity": 2}
   - payment_method: "UPI"
2. Display all simulation steps
3. Present the final BOOKING CONFIRMED message with the reference number

Make it celebratory! 🎉"""


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def run_task(
    user_task: str,
    auto_approve: bool = False,
    event_callback=None,
) -> dict:
    """
    Run the full multi-agent pipeline for a user task via NVIDIA NIM.

    Args:
        user_task: Natural language task from the user.
        auto_approve: If True, skip the human approval wait (for testing).
        event_callback: Optional async callable(event_type, agent, message).

    Returns:
        dict with keys: plan, security_report, nav_results, decision_summary, confirmation
    """
    results: dict = {}

    async def emit(event_type: str, agent: str, message: str):
        if event_callback:
            await event_callback(event_type, agent, message)
        else:
            print(f"[{agent}] {message[:200]}")

    agent = get_orchestrator()
    await emit("start", "Orchestrator", f"🚀 TaskHive (NVIDIA NIM) activated for: {user_task}")

    # Free NIM tier: ~5 req/min — 12s cooldown between phases keeps us safe
    PHASE_COOLDOWN = 12

    # ── PHASE 1: Planning ──────────────────────────────────────────────────────
    await emit("phase", "Planner Agent", "🧠 Analysing task and creating execution plan…")
    plan_text = await agent.run(_phase1_prompt(user_task))
    results["plan"] = plan_text
    await emit("plan_complete", "Planner Agent", plan_text)

    # ── PHASE 2: Security ──────────────────────────────────────────────────────
    await asyncio.sleep(PHASE_COOLDOWN)
    await emit("phase", "Security Agent", "🔒 Running security validation on target websites…")
    security_text = await agent.run(_phase2_prompt())
    results["security_report"] = security_text
    await emit("security_complete", "Security Agent", security_text)

    # ── PHASE 3: Web Navigation ────────────────────────────────────────────────
    await asyncio.sleep(PHASE_COOLDOWN)
    await emit("phase", "Web Nav Agent", "🌐 Navigating websites and extracting listings…")
    nav_text = await agent.run(_phase3_prompt(user_task))
    results["nav_results"] = nav_text
    await emit("nav_complete", "Web Nav Agent", nav_text)

    # ── PHASE 4: Decision & Validation ────────────────────────────────────────
    await asyncio.sleep(PHASE_COOLDOWN)
    await emit("phase", "Decision Agent", "✅ Validating selection against your constraints…")
    decision_text = await agent.run(_phase4_prompt(user_task))
    results["decision_summary"] = decision_text
    await emit("decision_complete", "Decision Agent", decision_text)

    # ── PHASE 5: Payment ──────────────────────────────────────────────────────
    await asyncio.sleep(PHASE_COOLDOWN)
    await emit("phase", "Payment Agent", "💳 Processing simulated payment…")
    payment_text = await agent.run(_phase5_prompt())
    results["confirmation"] = payment_text
    await emit("payment_complete", "Payment Agent", payment_text)

    await emit("complete", "Orchestrator", "✅ TaskHive pipeline completed successfully!")
    return results



# ── CLI entry point ────────────────────────────────────────────────────────────

async def interactive_cli():
    print("""
╔══════════════════════════════════════════════════════╗
║     🐝 TASKHIVE — AI Task Swarm (NVIDIA NIM) 🐝      ║
║  Powered by meta/llama-3.3-70b-instruct via NIM API  ║
╚══════════════════════════════════════════════════════╝
""")
    task = input("📝 Enter your task: ").strip()
    if not task:
        task = "Book 2 tickets for Mission Impossible on Sunday evening under ₹800"
        print(f"Using demo task: {task}")

    print("\n" + "═" * 56)
    await run_task(task)
    print("═" * 56)


if __name__ == "__main__":
    asyncio.run(interactive_cli())
