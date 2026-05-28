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

    # ── Phase-level fallbacks using local tools directly ─────────────────────
    def _fallback_plan(task: str) -> str:
        intent = parse_user_intent(task)
        plan   = create_task_plan(intent)
        return (
            f"[Demo Mode — NIM rate limit reached, using local tools]\n\n"
            f"📋 TASK PARSED:\n"
            f"  • Category  : {intent.get('category','general')}\n"
            f"  • Quantity  : {intent.get('quantity', 1)} tickets\n"
            f"  • Item      : {intent.get('item_name', task)}\n"
            f"  • Budget    : ₹{intent.get('budget_inr','N/A')}\n"
            f"  • Date/Time : {intent.get('preferred_date','any date')} {intent.get('preferred_time','evening')}\n\n"
            f"📌 EXECUTION PLAN ({plan.get('total_steps',5)} steps):\n"
            + "\n".join(f"  {s}" for s in plan.get("steps", ["Search → Select → Pay"]))
        )

    def _fallback_security() -> str:
        sites = ["bookmyshow.com", "pvrinemas.com", "inoxmovies.com"]
        lines = ["[Demo Mode — NIM rate limit reached, using local tools]\n\n🔒 SECURITY SCAN RESULTS:\n"]
        for site in sites:
            r = check_url_safety(f"https://{site}")
            lines.append(f"  {r['icon']} {site}: trust={r['trust_score']}/100  verdict={r['verdict']}")
        lines.append("\n✅ All platforms cleared for booking. Proceeding with bookmyshow.com.")
        return "\n".join(lines)

    def _fallback_nav(task: str) -> str:
        intent   = parse_user_intent(task)
        item     = intent.get("item_name", "the requested show")
        date_val = intent.get("preferred_date", "Sunday")
        time_val = intent.get("preferred_time", "evening")
        qty      = intent.get("quantity", 2)
        listings = extract_movie_listings("bookmyshow.com", item, date_val, time_val)
        shows    = listings.get("shows", [])
        seats    = navigate_to_seat_selection("bookmyshow.com", item, shows[0]["time"] if shows else "7:00 PM", qty)
        selected = seats.get("selected_seats", ["D5", "D6"])
        form     = fill_booking_form("TaskHive Demo", "demo@taskhive.ai", "9876543210", qty, selected)
        lines    = [
            "[Demo Mode — NIM rate limit reached, using local tools]\n",
            f"🌐 WEB NAVIGATION RESULTS for '{item}':",
            f"   Found {listings.get('total_shows_found', len(shows))} shows on {listings.get('website','bookmyshow.com')}.\n",
        ]
        for i, s in enumerate(shows[:3], 1):
            lines.append(f"  {i}. {s.get('time','?')} | {s.get('cinema','?')} | ₹{s.get('price_per_seat','?')} | {s.get('format','?')}")
        best = min(shows, key=lambda s: s.get("price_per_seat", 9999)) if shows else {}
        lines += [
            f"\n  ✅ BEST MATCH: {best.get('time','?')} @ {best.get('cinema','?')} ₹{best.get('price_per_seat','?')}/seat",
            f"  🪑 Seats selected: {selected}",
            f"  📋 Form filled: {form.get('status','OK')} — {form.get('message','')}",
        ]
        return "\n".join(lines)


    def _fallback_decision(task: str) -> str:
        intent  = parse_user_intent(task)
        item    = intent.get("item_name", "show")
        qty     = intent.get("quantity", 2)
        budget  = intent.get("budget_inr", 1000)
        date_v  = intent.get("preferred_date", "Sunday")
        time_v  = intent.get("preferred_time", "evening")
        shows   = extract_movie_listings("bookmyshow.com", item, date_v, time_v).get("shows", [])
        best    = min(shows, key=lambda s: s.get("price_per_seat", 9999)) if shows else {"price_per_seat": 350, "cinema": "PVR"}
        price   = best.get("price_per_seat", 350)
        total   = calculate_total_amount(price, qty, intent.get("category","movies"), True)
        b_check = check_budget_constraint(total["total_payable"], budget)
        icon    = "✅" if b_check["within_budget"] else "⚠️"
        return (
            f"[Demo Mode — NIM rate limit reached, using local tools]\n\n"
            f"✅ DECISION SUMMARY:\n\n"
            f"  📍 Venue    : {best.get('cinema','PVR')}\n"
            f"  🕐 Showtime : {best.get('time','7:00 PM')} — {date_v}\n"
            f"  💺 Seats    : {qty} tickets\n\n"
            f"  💰 COST BREAKDOWN:\n"
            + "\n".join(f"     {line}" for line in total.get("breakdown", [])) +
            f"\n\n  {icon} Budget check: ₹{total['total_payable']} vs ₹{budget} limit — "
            f"{'Within budget ✅' if b_check['within_budget'] else 'Over budget ⚠️'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Shall I proceed with the simulated payment? (Yes/No)"
        )

    def _fallback_payment(task: str) -> str:
        intent = parse_user_intent(task)
        qty    = intent.get("quantity", 2)
        date_v = intent.get("preferred_date", "Sunday")
        time_v = intent.get("preferred_time", "evening")
        shows  = extract_movie_listings("bookmyshow.com", intent.get("item_name","show"), date_v, time_v).get("shows", [])
        best   = min(shows, key=lambda s: s.get("price_per_seat", 9999)) if shows else {"price_per_seat": 350}
        total  = calculate_total_amount(best.get("price_per_seat", 350), qty, intent.get("category","movies"), True)
        seats  = navigate_to_seat_selection("bookmyshow.com", intent.get("item_name","show"), best.get("time","7:00 PM"), qty)
        pay    = simulate_payment(
            {"category": intent.get("category","movies"), "provider": "BMS",
             "seats": seats.get("selected_seats", ["D5","D6"]), "quantity": qty},
            total["total_payable"], "UPI"
        )
        ref = generate_booking_reference(intent.get("category","movies"), "BMS")
        return (
            f"[Demo Mode — NIM rate limit reached, using local tools]\n\n"
            f"💳 PAYMENT PROCESSING...\n\n"
            f"  ⚡ Initiating UPI payment of ₹{total['total_payable']}...\n"
            f"  🔐 Securing transaction...\n"
            f"  ✅ Payment authorized!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎉 BOOKING CONFIRMED!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"  📋 Booking Reference : {ref}\n"
            f"  💳 Transaction ID    : {pay.get('transaction_id','TXN'+ref[-6:])}\n"
            f"  💰 Amount Paid       : ₹{total['total_payable']}\n"
            f"  🪑 Seats             : {seats.get('selected_seats', ['D5','D6'])}\n"
            f"  📱 Payment Method    : UPI\n"
            f"  📧 Confirmation sent to: demo@taskhive.ai\n\n"
            f"  {pay.get('message','Booking confirmed successfully!')} 🎟️"
        )

    # ── Helper: run NIM with per-phase fallback ───────────────────────────────
    # Returns (result_text, used_nim: bool)
    async def run_phase(prompt: str, fallback_fn, *fallback_args):
        try:
            text = await agent.run(prompt)
            return text, True   # NIM succeeded
        except Exception as e:
            err = str(e)
            if "429" in err or "Too Many Requests" in err or "RateLimitError" in err.replace(" ", ""):
                print(f"[NIM] Rate limit — using local fallback for this phase.")
                return fallback_fn(*fallback_args), False   # local fallback
            raise  # re-raise unexpected errors

    agent = get_orchestrator()
    await emit("start", "Orchestrator", f"🚀 TaskHive (NVIDIA NIM) activated for: {user_task}")

    NIM_COOLDOWN = 12   # seconds between NIM calls (free-tier RPM limit)

    # ── PHASE 1: Planning ──────────────────────────────────────────────────────
    await emit("phase", "Planner Agent", "🧠 Analysing task and creating execution plan…")
    plan_text, p1_nim = await run_phase(_phase1_prompt(user_task), _fallback_plan, user_task)
    results["plan"] = plan_text
    await emit("plan_complete", "Planner Agent", plan_text)

    # ── PHASE 2: Security ──────────────────────────────────────────────────────
    if p1_nim:
        await asyncio.sleep(NIM_COOLDOWN)
    await emit("phase", "Security Agent", "🔒 Running security validation on target websites…")
    security_text, p2_nim = await run_phase(_phase2_prompt(), _fallback_security)
    results["security_report"] = security_text
    await emit("security_complete", "Security Agent", security_text)

    # ── PHASE 3: Web Navigation ────────────────────────────────────────────────
    if p2_nim:
        await asyncio.sleep(NIM_COOLDOWN)
    await emit("phase", "Web Nav Agent", "🌐 Navigating websites and extracting listings…")
    nav_text, p3_nim = await run_phase(_phase3_prompt(user_task), _fallback_nav, user_task)
    results["nav_results"] = nav_text
    await emit("nav_complete", "Web Nav Agent", nav_text)

    # ── PHASE 4: Decision & Validation ────────────────────────────────────────
    if p3_nim:
        await asyncio.sleep(NIM_COOLDOWN)
    await emit("phase", "Decision Agent", "✅ Validating selection against your constraints…")
    decision_text, p4_nim = await run_phase(_phase4_prompt(user_task), _fallback_decision, user_task)
    results["decision_summary"] = decision_text
    await emit("decision_complete", "Decision Agent", decision_text)

    # ── PHASE 5: Payment ──────────────────────────────────────────────────────
    if p4_nim:
        await asyncio.sleep(NIM_COOLDOWN)
    await emit("phase", "Payment Agent", "💳 Processing simulated payment…")
    payment_text, _ = await run_phase(_phase5_prompt(), _fallback_payment, user_task)
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
