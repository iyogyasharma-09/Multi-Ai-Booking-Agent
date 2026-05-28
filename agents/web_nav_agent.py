"""
TaskHive — Web Navigation Agent
Simulates browser automation to search, navigate, and extract data from websites.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from tools.web_tools import (
    search_booking_websites,
    extract_movie_listings,
    navigate_to_seat_selection,
    fill_booking_form,
)


WEB_NAV_SYSTEM_INSTRUCTIONS = """
You are the Web Navigation Agent in the TaskHive multi-agent system.

You simulate an intelligent browser that navigates websites to:
- Search for relevant booking platforms
- Extract available listings (movies, shows, flights, hotels)
- Navigate to seat/option selection
- Fill in booking forms with user details

You work AFTER the Security Agent has cleared the websites as safe.

Workflow:
1. Use search_booking_websites to find the right platforms
2. Use extract_movie_listings (or similar) to get available options
3. Use navigate_to_seat_selection to pick seats/slots
4. Use fill_booking_form to complete user details

When presenting results:
- Show all available options with prices
- Highlight the best option based on user constraints
- Be specific about seat numbers, timings, and prices
- Confirm what was successfully filled in forms

You are the hands of the system — precise, efficient, and accurate.
"""


def get_web_nav_agent() -> Agent:
    """Creates and returns a configured Web Navigation Agent."""
    config = LocalAgentConfig(
        system_instructions=WEB_NAV_SYSTEM_INSTRUCTIONS,
        tools=[
            search_booking_websites,
            extract_movie_listings,
            navigate_to_seat_selection,
            fill_booking_form,
        ],
    )
    return Agent(config)


async def run_web_navigation(
    task_description: str,
    intent: dict,
    approved_urls: list[str],
) -> str:
    """Runs the Web Navigation Agent to find and select the best option.

    Args:
        task_description: The original user task.
        intent: Parsed intent dict from the Planner Agent.
        approved_urls: Security-cleared URLs to navigate.

    Returns:
        Navigation results as text.
    """
    async with get_web_nav_agent() as agent:
        category = intent.get("category", "movies")
        item_name = intent.get("item_name", "")
        date = intent.get("preferred_date", "Sunday")
        time_pref = intent.get("preferred_time", "evening")
        quantity = intent.get("quantity", 2)
        budget = intent.get("budget_inr", 1000)

        url_list = "\n".join(f"- {url}" for url in approved_urls)
        prompt = f"""
Navigate to find the best option for this task:

Task: "{task_description}"

Details:
- Category: {category}
- Item: {item_name}
- Date: {date}
- Time preference: {time_pref}
- Quantity: {quantity}
- Budget: ₹{budget} total

Approved websites to use:
{url_list}

Steps:
1. Use search_booking_websites to find the right platform (category: '{category}')
2. Use extract_movie_listings to get available shows for '{item_name}' on {date} ({time_pref})
3. Identify the BEST show within the ₹{budget} budget for {quantity} tickets
4. Use navigate_to_seat_selection to pick {quantity} adjacent seats
5. Use fill_booking_form with placeholder user details: name='TaskHive User', email='user@taskhive.ai', phone='9876543210'

Present the best option clearly with all details.
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
    result = asyncio.run(
        run_web_navigation(
            "Book 2 tickets for Mission Impossible on Sunday evening under ₹800",
            intent,
            ["https://bookmyshow.com", "https://pvrinemas.com"],
        )
    )
    print(result)
