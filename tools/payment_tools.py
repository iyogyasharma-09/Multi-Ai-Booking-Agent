"""
TaskHive — Payment Tools
Safe, simulated payment processing for the Payment Agent.
No real transactions are made. Stops safely before OTP/2FA.
"""

import uuid
import random
import hashlib
from datetime import datetime
from typing import Any


# ─── Simulated Payment Gateways ───────────────────────────────────────────────

PAYMENT_GATEWAYS = [
    {"name": "Razorpay", "logo": "💳", "fee_percent": 0},
    {"name": "PayU", "logo": "💳", "fee_percent": 0},
    {"name": "CCAvenue", "logo": "💳", "fee_percent": 0},
    {"name": "Paytm PG", "logo": "💳", "fee_percent": 0},
]

CONVENIENCE_FEES = {
    "movies": {"flat": 30, "gst_percent": 18},
    "flights": {"flat": 150, "gst_percent": 18},
    "hotels": {"flat": 50, "gst_percent": 18},
    "food": {"flat": 15, "gst_percent": 5},
    "bills": {"flat": 5, "gst_percent": 18},
    "default": {"flat": 20, "gst_percent": 18},
}


# ─── Tool Functions ────────────────────────────────────────────────────────────

def calculate_total_amount(
    base_amount: float,
    quantity: int,
    task_category: str = "movies",
    apply_convenience_fee: bool = True,
) -> dict[str, Any]:
    """Calculates the full payable amount including fees and taxes.

    Args:
        base_amount: Base price per unit (e.g. price per ticket in INR).
        quantity: Number of units (e.g. number of tickets).
        task_category: Category of task for fee calculation.
        apply_convenience_fee: Whether to apply booking convenience fee.
    """
    subtotal = base_amount * quantity
    fee_config = CONVENIENCE_FEES.get(task_category, CONVENIENCE_FEES["default"])

    convenience_fee = fee_config["flat"] if apply_convenience_fee else 0
    gst_rate = fee_config["gst_percent"] / 100
    gst_amount = round((subtotal + convenience_fee) * gst_rate, 2)
    total = round(subtotal + convenience_fee + gst_amount, 2)

    return {
        "base_amount_per_unit": base_amount,
        "quantity": quantity,
        "subtotal": subtotal,
        "convenience_fee": convenience_fee,
        "gst_amount": gst_amount,
        "gst_rate_percent": fee_config["gst_percent"],
        "total_payable": total,
        "currency": "INR",
        "breakdown": [
            f"Base price: ₹{base_amount} × {quantity} = ₹{subtotal}",
            f"Convenience fee: ₹{convenience_fee}",
            f"GST ({fee_config['gst_percent']}%): ₹{gst_amount}",
            f"Total: ₹{total}",
        ],
    }


def generate_booking_reference(
    task_category: str = "movies",
    cinema_or_provider: str = "BMS",
) -> str:
    """Generates a realistic booking reference number.

    Args:
        task_category: Type of booking (movies, flights, etc.).
        cinema_or_provider: Short name of the provider (e.g. 'BMS', 'PVR', 'MYT').
    """
    prefix_map = {
        "movies": cinema_or_provider.upper()[:3],
        "flights": "FLT",
        "hotels": "HTL",
        "food": "FDD",
        "bills": "BIL",
        "default": "TXN",
    }
    prefix = prefix_map.get(task_category, "TXN")
    year = datetime.now().year
    unique_id = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{year}-{unique_id}"


def simulate_payment(
    booking_details: dict[str, Any],
    total_amount: float,
    payment_method: str = "UPI",
) -> dict[str, Any]:
    """Simulates the payment flow safely — stops before OTP/2FA step.

    This is a DEMO-SAFE simulation. No real money is transferred.
    The function simulates all payment steps up to the OTP entry point,
    then marks the payment as 'pending OTP confirmation' and returns
    a mock booking confirmation.

    Args:
        booking_details: Dict containing booking info (show, seats, user details).
        total_amount: Total amount to be paid in INR.
        payment_method: Payment method — 'UPI', 'NetBanking', 'Card', 'Wallet'.
    """
    gateway = random.choice(PAYMENT_GATEWAYS)
    ref = generate_booking_reference(
        task_category=booking_details.get("category", "movies"),
        cinema_or_provider=booking_details.get("provider", "BMS"),
    )
    transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    simulation_steps = [
        f"✅ Redirected to {gateway['name']} payment gateway",
        f"✅ Payment method selected: {payment_method}",
        f"✅ Amount confirmed: ₹{total_amount}",
        f"✅ Transaction ID generated: {transaction_id}",
        f"⏸️  OTP sent to registered mobile — awaiting confirmation (DEMO: auto-approved)",
        f"✅ OTP verified (simulated)",
        f"✅ Payment of ₹{total_amount} processed successfully",
    ]

    # Build confirmation
    confirmation = {
        "status": "SUCCESS",
        "booking_reference": ref,
        "transaction_id": transaction_id,
        "amount_paid": total_amount,
        "currency": "INR",
        "payment_method": payment_method,
        "gateway": gateway["name"],
        "timestamp": timestamp,
        "simulation_steps": simulation_steps,
        "booking_details": booking_details,
        "confirmation_message": (
            f"🎉 Booking Confirmed!\n"
            f"Reference: {ref}\n"
            f"Amount Paid: ₹{total_amount}\n"
            f"Payment via {payment_method} through {gateway['name']}\n"
            f"Confirmation will be sent to your registered email & phone."
        ),
        "demo_note": (
            "⚠️ DEMO MODE: This is a simulated payment. "
            "No real transaction was made. In production, "
            "this would complete the actual payment flow."
        ),
    }

    return confirmation


def check_budget_constraint(
    total_amount: float,
    budget_limit: float,
) -> dict[str, Any]:
    """Checks if the total amount is within the user's specified budget.

    Args:
        total_amount: The calculated total amount to pay in INR.
        budget_limit: The user's maximum budget in INR.
    """
    within_budget = total_amount <= budget_limit
    savings = round(budget_limit - total_amount, 2) if within_budget else 0
    overage = round(total_amount - budget_limit, 2) if not within_budget else 0

    return {
        "total_amount": total_amount,
        "budget_limit": budget_limit,
        "within_budget": within_budget,
        "savings": savings,
        "overage": overage,
        "verdict": "✅ Within budget" if within_budget else f"❌ Exceeds budget by ₹{overage}",
        "message": (
            f"Total ₹{total_amount} is {'within' if within_budget else 'over'} "
            f"the ₹{budget_limit} budget"
            + (f" by ₹{overage}" if not within_budget else f". Saving ₹{savings}!")
        ),
    }
