"""
TaskHive — Task Planning Tools
Intent parsing and task decomposition for the Planner Agent.
"""

import re
from typing import Any


# ─── Intent Keywords ──────────────────────────────────────────────────────────

TASK_CATEGORIES = {
    "movies": ["movie", "film", "ticket", "cinema", "show", "pvr", "inox", "bookmyshow"],
    "flights": ["flight", "plane", "airline", "fly", "airport", "travel"],
    "hotels": ["hotel", "stay", "room", "accommodation", "resort", "hostel"],
    "food": ["food", "order", "restaurant", "delivery", "zomato", "swiggy", "eat"],
    "bills": ["bill", "electricity", "internet", "recharge", "mobile", "broadband", "dth"],
    "shopping": ["buy", "purchase", "shop", "amazon", "flipkart", "order"],
    "trains": ["train", "railway", "irctc", "station", "rail"],
}

DAY_MAP = {
    "today": "Today",
    "tomorrow": "Tomorrow",
    "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
    "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday",
    "sunday": "Sunday",
    "this weekend": "Saturday/Sunday",
    "weekend": "Saturday/Sunday",
}

TIME_MAP = {
    "morning": "morning", "afternoon": "afternoon",
    "evening": "evening", "night": "night",
    "late night": "night", "early morning": "morning",
}

PLAN_TEMPLATES = {
    "movies": [
        "Parse user preferences (movie name, date, time, quantity, budget)",
        "Search for available booking websites (BookMyShow, PVR, INOX)",
        "Run security validation on each website URL",
        "Extract available show listings matching preferences",
        "Select best show based on constraints (timing, budget, seat availability)",
        "Navigate to seat selection and choose optimal seats",
        "Fill in booking details form with user information",
        "Present summary for user approval",
        "Simulate payment and generate booking confirmation",
    ],
    "bills": [
        "Parse bill payment details (provider, account number, amount)",
        "Identify trusted payment platforms (Paytm, PhonePe, GPay)",
        "Run security validation on payment platform URL",
        "Navigate to bill payment section",
        "Look up account and verify bill amount",
        "Present bill summary for user approval",
        "Simulate payment and generate receipt",
    ],
    "food": [
        "Parse order details (restaurant/cuisine, items, delivery address)",
        "Search Zomato and Swiggy for matching restaurants",
        "Run security validation on delivery platform URLs",
        "Select best restaurant matching preferences",
        "Add items to cart",
        "Verify order total and delivery time",
        "Present order summary for user approval",
        "Simulate payment and generate order confirmation",
    ],
    "default": [
        "Parse and understand user task requirements",
        "Identify relevant websites and platforms",
        "Run security validation on all URLs",
        "Navigate to appropriate page and extract required information",
        "Select best option matching user constraints",
        "Present details for user approval",
        "Execute task and generate confirmation",
    ],
}


# ─── Tool Functions ────────────────────────────────────────────────────────────

def parse_user_intent(raw_text: str) -> dict[str, Any]:
    """Parses raw user input text to extract structured task intent.

    Identifies task category, key entities (movie name, date, count, budget),
    and user preferences from natural language.

    Args:
        raw_text: The raw user input string (e.g. 'Book 2 MI tickets Sunday evening under 800').
    """
    text = raw_text.lower().strip()

    # Detect category
    detected_category = "default"
    category_scores: dict[str, int] = {}
    for category, keywords in TASK_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            category_scores[category] = score
    if category_scores:
        detected_category = max(category_scores, key=lambda k: category_scores[k])

    # Extract quantity (e.g. "2 tickets", "3 seats", "2 pizzas", "4 items")
    quantity_match = re.search(
        r"\b(\d+)\s*(?:ticket|seat|person|people|head|pax|pizza|burger|item|order|piece|plate|room|night|adult|passenger)s?\b",
        text,
    )
    if not quantity_match:
        # Fallback: number directly after action verbs (order 2, book 3, buy 4)
        quantity_match = re.search(r"(?:order|book|buy|get|want|need)\s+(\d+)\b", text)
    quantity = int(quantity_match.group(1)) if quantity_match else 1

    # Extract budget (e.g. "under 800", "₹500", "less than 1000")
    budget_match = re.search(
        r"(?:under|below|less than|max|upto|up to|within)?\s*[₹rs.]?\s*(\d{2,5})", text
    )
    budget = int(budget_match.group(1)) if budget_match else None

    # Extract preferred date/day
    preferred_date = None
    for key, val in DAY_MAP.items():
        if key in text:
            preferred_date = val
            break

    # Extract preferred time
    preferred_time = None
    for key, val in TIME_MAP.items():
        if key in text:
            preferred_time = val
            break

    # Extract movie/item name — find the phrase between "for" and constraint words
    name_match = re.search(
        r"\bfor\s+(?:\d+\s+(?:tickets?|seats?|persons?)\s+(?:for|of)\s+)?([a-z0-9:'\-\s]+?)(?:\s+(?:on|this|at|in|tickets?|show|film|movie)\b)",
        text,
    )
    if not name_match:
        # Fallback: grab longest capitalised-looking sequence
        name_match = re.search(r"(?:for|watch|see)\s+([a-z0-9:'\-\s]{3,40})", text)
    raw_name = name_match.group(1).strip() if name_match else raw_text
    # Remove leading standalone digits (e.g. "2 " leftover)
    item_name = re.sub(r"^\d+\s+", "", raw_name).strip()

    # Build structured intent
    intent = {
        "raw_input": raw_text,
        "category": detected_category,
        "quantity": quantity,
        "budget_inr": budget,
        "preferred_date": preferred_date or "This Weekend",
        "preferred_time": preferred_time or "evening",
        "item_name": item_name.title(),
        "constraints": [],
    }

    if budget:
        intent["constraints"].append(f"Total cost must be under ₹{budget}")
    if preferred_time:
        intent["constraints"].append(f"Show must be in the {preferred_time}")
    if preferred_date:
        intent["constraints"].append(f"Date: {preferred_date}")
    if quantity > 1:
        intent["constraints"].append(f"Need {quantity} tickets")

    return intent


def create_task_plan(intent: dict[str, Any]) -> dict[str, Any]:
    """Creates an ordered execution plan from a parsed intent.

    Returns a detailed step-by-step plan for the agent swarm to execute.

    Args:
        intent: The structured intent dict returned by parse_user_intent.
    """
    category = intent.get("category", "default")
    steps = PLAN_TEMPLATES.get(category, PLAN_TEMPLATES["default"])

    item_name = intent.get("item_name", "item")
    quantity = intent.get("quantity", 1)
    budget = intent.get("budget_inr")
    date = intent.get("preferred_date")
    time_pref = intent.get("preferred_time")

    # Build a human-readable plan title
    if category == "movies":
        title = f"Book {quantity} ticket(s) for '{item_name}'"
        if date:
            title += f" on {date}"
        if time_pref:
            title += f" ({time_pref})"
        if budget:
            title += f" within ₹{budget}"
    else:
        title = f"Complete {category} task: {intent.get('raw_input', '')[:60]}"

    numbered_steps = [
        {"step": i + 1, "description": step, "agent": _assign_agent(i, step), "status": "pending"}
        for i, step in enumerate(steps)
    ]

    return {
        "plan_title": title,
        "category": category,
        "total_steps": len(numbered_steps),
        "steps": numbered_steps,
        "agents_involved": ["Planner", "Security", "Web Navigator", "Decision", "Payment"],
        "estimated_time_seconds": len(steps) * 3,
        "constraints": intent.get("constraints", []),
        "message": f"Plan created with {len(steps)} steps for: {title}",
    }


def _assign_agent(step_index: int, step_description: str) -> str:
    """Assigns the appropriate agent to a step based on its description."""
    desc = step_description.lower()
    if "security" in desc or "validat" in desc or "safe" in desc:
        return "Security Agent"
    if "payment" in desc or "receipt" in desc or "confirm" in desc and "booking" in desc:
        return "Payment Agent"
    if "user approval" in desc or "present" in desc or "summary" in desc:
        return "Decision Agent"
    if "navigate" in desc or "search" in desc or "extract" in desc or "fill" in desc:
        return "Web Nav Agent"
    if step_index == 0:
        return "Planner Agent"
    return "Orchestrator"
