"""
TaskHive — Payment Agent
Handles the safe, simulated payment flow. Stops before real OTP/2FA.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from tools.payment_tools import (
    simulate_payment,
    calculate_total_amount,
    generate_booking_reference,
)


PAYMENT_SYSTEM_INSTRUCTIONS = """
You are the Payment Agent in the TaskHive multi-agent system.

IMPORTANT: This is a HACKATHON DEMO. You simulate payment flows safely.
You NEVER process real transactions. You ALWAYS stop before OTP/2FA.

Your responsibilities:
1. Accept the approved booking details from the user
2. Use simulate_payment to run the mock payment flow
3. Generate a realistic booking confirmation

Payment simulation steps you execute:
✅ Redirect to payment gateway
✅ Select payment method (UPI/Card/NetBanking)
✅ Display amount for confirmation
✅ Send OTP to phone (simulated)
✅ Auto-approve OTP in demo mode
✅ Generate booking reference
✅ Send confirmation to email/phone (simulated)

Present the final confirmation in this format:

🎉 BOOKING CONFIRMED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Booking Reference: [REF]
💳 Transaction ID: [TXN]
💰 Amount Paid: ₹[AMOUNT]
💳 Payment Method: [METHOD]
🏦 Gateway: [GATEWAY]
⏰ Time: [TIMESTAMP]

📧 Confirmation sent to: user@taskhive.ai
📱 SMS sent to: ****3210

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[DEMO NOTE: Simulated payment — no real transaction]

Always be celebratory and clear. This is the happy ending of the agent workflow!
"""


def get_payment_agent() -> Agent:
    """Creates and returns a configured Payment Agent."""
    config = LocalAgentConfig(
        system_instructions=PAYMENT_SYSTEM_INSTRUCTIONS,
        tools=[simulate_payment, calculate_total_amount, generate_booking_reference],
    )
    return Agent(config)


async def run_payment(
    booking_details: dict,
    total_amount: float,
    payment_method: str = "UPI",
) -> str:
    """Runs the Payment Agent to simulate the payment flow.

    Args:
        booking_details: Full booking context dict.
        total_amount: The final amount to pay in INR.
        payment_method: Chosen payment method.

    Returns:
        Payment confirmation as text.
    """
    async with get_payment_agent() as agent:
        prompt = f"""
Process this approved booking payment.

Booking details:
- Movie: {booking_details.get('movie_title', 'Movie')}
- Cinema: {booking_details.get('cinema', 'Cinema')}
- Seats: {booking_details.get('seats', [])}
- Quantity: {booking_details.get('quantity', 2)}
- Category: {booking_details.get('category', 'movies')}
- Provider: {booking_details.get('provider', 'BMS')}

Payment:
- Total Amount: ₹{total_amount}
- Payment Method: {payment_method}

Use simulate_payment with:
- booking_details: the details above as a dict
- total_amount: {total_amount}
- payment_method: '{payment_method}'

Then present the full booking confirmation with celebration!
"""
        response = await agent.chat(prompt)
        return await response.text()


if __name__ == "__main__":
    booking = {
        "movie_title": "Mission: Impossible — The Final Reckoning",
        "cinema": "PVR Phoenix Mall",
        "seats": ["D5", "D6"],
        "quantity": 2,
        "category": "movies",
        "provider": "PVR",
    }
    result = asyncio.run(run_payment(booking, 760.0, "UPI"))
    print(result)
