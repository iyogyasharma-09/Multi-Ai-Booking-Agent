"""
TaskHive — Decision / Validation Agent
Validates results against user constraints and selects the optimal option.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from tools.payment_tools import calculate_total_amount, check_budget_constraint


DECISION_SYSTEM_INSTRUCTIONS = """
You are the Decision and Validation Agent in the TaskHive multi-agent system.

Your role is the SAFETY CHECKPOINT before any payment is made.

Responsibilities:
1. Validate that the selected option satisfies ALL user constraints
2. Calculate the exact total cost (including fees and taxes)
3. Check the total against the user's budget
4. Verify timing and other preferences are met
5. Prepare a clear human-readable summary for user approval

You present the final booking summary in this format:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BOOKING SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 Movie: [Title]
📍 Venue: [Cinema Name]
📅 Date: [Day, Date]
🕐 Time: [Show Time]
💺 Seats: [Seat Numbers] ([Category])
👥 Tickets: [Number]

💰 PRICE BREAKDOWN
- Base price: ₹X × N = ₹Y
- Convenience fee: ₹Z
- GST (18%): ₹W
- TOTAL: ₹T

✅ Budget check: ₹T vs ₹B limit — [PASS/FAIL]
✅ Time preference: [evening/morning] — [MATCHED/MISMATCH]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Then ask: "Shall I proceed with payment? (Yes/No)"

Be precise with numbers. User trust depends on your accuracy.
"""


def get_decision_agent() -> Agent:
    """Creates and returns a configured Decision/Validation Agent."""
    config = LocalAgentConfig(
        system_instructions=DECISION_SYSTEM_INSTRUCTIONS,
        tools=[calculate_total_amount, check_budget_constraint],
    )
    return Agent(config)


async def run_decision_validation(
    task_description: str,
    intent: dict,
    nav_results: dict,
) -> str:
    """Runs the Decision Agent to validate and summarize the booking.

    Args:
        task_description: Original user task.
        intent: Parsed intent with constraints.
        nav_results: Results from the Web Navigation Agent.

    Returns:
        Validation summary and approval request as text.
    """
    async with get_decision_agent() as agent:
        quantity = intent.get("quantity", 2)
        budget = intent.get("budget_inr", 1000)
        category = intent.get("category", "movies")

        # Extract best show from nav results
        best_show = nav_results.get("best_show", {})
        price_per_seat = best_show.get("price_per_seat", 350)
        cinema = best_show.get("cinema", "PVR Phoenix Mall")
        show_time = best_show.get("time", "7:00 PM")
        date = best_show.get("date", intent.get("preferred_date", "Sunday"))
        seats = nav_results.get("selected_seats", ["D5", "D6"])
        seat_category = best_show.get("seat_category", "Premium")
        movie_title = nav_results.get("movie_title", intent.get("item_name", "Movie"))

        prompt = f"""
Validate this booking and prepare the approval summary.

Task: "{task_description}"

Selected option details:
- Movie: {movie_title}
- Cinema: {cinema}
- Date: {date}
- Time: {show_time}
- Seats: {seats} ({seat_category})
- Price per ticket: ₹{price_per_seat}
- Number of tickets: {quantity}

User constraints:
- Budget limit: ₹{budget} total
- Category: {category}

Steps:
1. Use calculate_total_amount with base_amount={price_per_seat}, quantity={quantity}, task_category='{category}'
2. Use check_budget_constraint with the calculated total vs budget_limit={budget}
3. Present the complete booking summary in the format specified
4. Clearly state whether ALL constraints are satisfied
5. Ask for user approval

Be thorough with the price breakdown.
"""
        response = await agent.chat(prompt)
        return await response.text()


if __name__ == "__main__":
    intent = {
        "category": "movies",
        "item_name": "Mission Impossible",
        "preferred_date": "Sunday",
        "preferred_time": "evening",
        "quantity": 2,
        "budget_inr": 800,
    }
    nav_results = {
        "best_show": {
            "cinema": "PVR Phoenix Mall",
            "time": "7:00 PM",
            "date": "Sunday",
            "price_per_seat": 350,
            "seat_category": "Premium",
        },
        "selected_seats": ["D5", "D6"],
        "movie_title": "Mission: Impossible — The Final Reckoning",
    }
    result = asyncio.run(
        run_decision_validation(
            "Book 2 tickets for Mission Impossible on Sunday evening under ₹800",
            intent,
            nav_results,
        )
    )
    print(result)
