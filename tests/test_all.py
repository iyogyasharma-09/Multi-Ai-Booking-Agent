"""
TaskHive — Comprehensive Test Suite
Run with: python3 tests/test_all.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.security_tools import (
    check_url_safety, verify_payment_page,
    check_domain_reputation, scan_page_content_for_threats,
)
from tools.task_tools import parse_user_intent, create_task_plan
from tools.web_tools import (
    search_booking_websites, extract_movie_listings,
    navigate_to_seat_selection, fill_booking_form,
)
from tools.payment_tools import (
    calculate_total_amount, check_budget_constraint,
    simulate_payment, generate_booking_reference,
)

# ── Assertion helpers ──────────────────────────────────────────
def assert_true(v, msg=""):
    if not v:
        raise AssertionError(msg or f"Expected True, got {v!r}")

def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(msg or f"Expected {b!r}, got {a!r}")

def assert_in(needle, haystack, msg=""):
    if needle not in haystack:
        raise AssertionError(msg or f"{needle!r} not found in {haystack!r}")

# ── Test runner ────────────────────────────────────────────────
passed = 0
failed = 0
failures = []

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAIL  {name}")
        print(f"           → {e}")
        failed += 1
        failures.append((name, str(e)))


# ══════════════════════════════════════════════════════════════
# SECURITY TOOLS
# ══════════════════════════════════════════════════════════════
print("\n📦 MODULE: tools/security_tools.py")

def t_https_safe():
    r = check_url_safety("https://bookmyshow.com")
    assert_true(r["trust_score"] >= 80, f"Score was {r['trust_score']}")
    assert_eq(r["verdict"], "SAFE")
    assert_true(r["https"])

def t_http_penalty():
    r = check_url_safety("http://bookmyshow.com")
    assert_true(r["trust_score"] < 100, "HTTP should lose points")
    assert_true(not r["https"])

def t_phishing_url():
    r = check_url_safety("http://free-tickets-win.fake-bookmyshow.xyz")
    assert_true(r["trust_score"] < 60, f"Phishing URL scored {r['trust_score']}")
    assert_eq(r["verdict"], "DANGEROUS")

def t_typosquatting():
    r = check_url_safety("https://paypa1.com/checkout")
    assert_true(r["trust_score"] < 60, f"Typosquatting scored {r['trust_score']}")

def t_domain_rep_known():
    r = check_domain_reputation("bookmyshow.com")
    assert_true(r["reputation_score"] >= 80)
    assert_eq(r["status"], "Established")

def t_domain_rep_unknown():
    r = check_domain_reputation("xyz-random-abc123.com")
    assert_true(r["reputation_score"] < 80)

def t_payment_page_mismatch():
    r = verify_payment_page("https://evil-site.com/payment", "bookmyshow.com")
    assert_true(not r["is_safe"])
    assert_true(not r["domain_match"])

def t_payment_page_match():
    r = verify_payment_page("https://bookmyshow.com/checkout", "bookmyshow.com")
    assert_true(r["domain_match"])
    assert_true(r["is_safe"])

def t_clean_content():
    r = scan_page_content_for_threats("Welcome to BookMyShow. Select your seats below.")
    assert_eq(r["risk_level"], "LOW")
    assert_true(r["is_safe"])

def t_phishing_content():
    r = scan_page_content_for_threats(
        "Your account will be suspended. Act now. You have won a free gift. Claim your prize."
    )
    assert_true(r["total_threat_signals"] > 0)
    assert_true(r["risk_level"] in ("MEDIUM", "HIGH"))

test("HTTPS URL scores SAFE (≥80)", t_https_safe)
test("HTTP URL penalised", t_http_penalty)
test("Phishing URL flagged DANGEROUS (<60)", t_phishing_url)
test("Typosquatting URL flagged DANGEROUS (<60)", t_typosquatting)
test("Known domain has high reputation + Established", t_domain_rep_known)
test("Unknown domain has lower reputation", t_domain_rep_unknown)
test("Payment page domain mismatch → not safe", t_payment_page_mismatch)
test("Legitimate payment page → safe", t_payment_page_match)
test("Clean page content → LOW risk", t_clean_content)
test("Phishing page content → threats detected", t_phishing_content)


# ══════════════════════════════════════════════════════════════
# TASK PLANNING TOOLS
# ══════════════════════════════════════════════════════════════
print("\n📦 MODULE: tools/task_tools.py")

def t_parse_movie():
    r = parse_user_intent("Book 2 tickets for Mission Impossible on Sunday evening under 800")
    assert_eq(r["category"], "movies")
    assert_true("mission impossible" in r["item_name"].lower(), f"Item: {r['item_name']}")
    assert_eq(r["quantity"], 2)
    assert_eq(r["budget_inr"], 800)
    assert_eq(r["preferred_date"], "Sunday")
    assert_eq(r["preferred_time"], "evening")

def t_parse_bill():
    r = parse_user_intent("Pay my Airtel broadband bill")
    assert_eq(r["category"], "bills")

def t_parse_food():
    r = parse_user_intent("Order 2 pizzas from Zomato under 600")
    assert_eq(r["category"], "food")
    assert_eq(r["quantity"], 2)
    assert_eq(r["budget_inr"], 600)

def t_parse_flight():
    r = parse_user_intent("Book a flight to Bangalore tomorrow morning")
    assert_eq(r["category"], "flights")
    assert_eq(r["preferred_time"], "morning")

def t_plan_steps():
    intent = parse_user_intent("Book 2 tickets for Mission Impossible on Sunday evening under 800")
    plan = create_task_plan(intent)
    assert_true(plan["total_steps"] >= 5)
    assert_eq(len(plan["steps"]), plan["total_steps"])
    for step in plan["steps"]:
        assert_true("agent" in step, f"Step missing agent: {step}")
        assert_true("description" in step)

def t_plan_constraints():
    intent = parse_user_intent("Book 2 tickets for Kalki on Saturday under 1000")
    plan = create_task_plan(intent)
    assert_true(len(plan["constraints"]) >= 2, f"Only {len(plan['constraints'])} constraints")

def t_plan_title():
    intent = parse_user_intent("Book 2 tickets for Stree on Friday evening under 700")
    plan = create_task_plan(intent)
    assert_true("Stree" in plan["plan_title"] or "stree" in plan["plan_title"].lower())

test("Parse movie: category, item, qty=2, budget=800, Sunday evening", t_parse_movie)
test("Parse bill payment: category=bills", t_parse_bill)
test("Parse food order: qty=2 extracted correctly", t_parse_food)
test("Parse flight: category=flights, morning time", t_parse_flight)
test("Plan has ≥5 steps each with agent + description", t_plan_steps)
test("Plan captures ≥2 constraints (budget + date)", t_plan_constraints)
test("Plan title includes movie name", t_plan_title)


# ══════════════════════════════════════════════════════════════
# WEB NAVIGATION TOOLS
# ══════════════════════════════════════════════════════════════
print("\n📦 MODULE: tools/web_tools.py")

def t_search_movies():
    r = search_booking_websites("Mission Impossible tickets Mumbai", "movies")
    assert_true(r["sites_found"] >= 2)
    urls = [s["url"] for s in r["results"]]
    assert_true(any("bookmyshow" in u for u in urls), f"BookMyShow not found in {urls}")

def t_search_bills():
    r = search_booking_websites("pay electricity bill", "bills")
    urls = [s["url"] for s in r["results"]]
    assert_true(any("paytm" in u for u in urls))

def t_search_food():
    r = search_booking_websites("order food online", "food")
    urls = [s["url"] for s in r["results"]]
    assert_true(any("zomato" in u or "swiggy" in u for u in urls))

def t_extract_listings():
    r = extract_movie_listings(
        "https://bookmyshow.com", "Mission Impossible", "Sunday", "evening", "Mumbai"
    )
    assert_true(r["total_shows_found"] > 0)
    assert_true("Mission" in r["movie"]["title"])
    for show in r["shows"]:
        assert_true("price_per_seat" in show)
        assert_true("cinema" in show)
        assert_true("time" in show)

def t_shows_sorted_by_price():
    r = extract_movie_listings(
        "https://bookmyshow.com", "Kalki", "Saturday", "night", "Delhi"
    )
    prices = [s["price_per_seat"] for s in r["shows"]]
    assert_eq(prices, sorted(prices), "Shows not sorted by price ascending")

def t_seat_selection_count():
    r = navigate_to_seat_selection("https://bookmyshow.com", "show-xyz-789", "PVR Phoenix", 2)
    assert_eq(len(r["selected_seats"]), 2)
    assert_true(r["ready_for_checkout"])

def t_seat_selection_single():
    r = navigate_to_seat_selection("https://pvrinemas.com", "show-abc-111", "INOX Garuda", 1)
    assert_eq(len(r["selected_seats"]), 1)

def t_form_valid():
    r = fill_booking_form("Test User", "test@taskhive.ai", "9876543210", 2, ["D5", "D6"])
    assert_true(r["success"])
    assert_true(r["ready_for_payment"])
    assert_eq(len(r["steps_completed"]), 5)

def t_form_bad_email():
    r = fill_booking_form("Test User", "not-an-email", "9876543210", 2, ["D5"])
    assert_true(not r["success"])
    assert_true(any("email" in e.lower() for e in r["errors"]))

def t_form_bad_phone():
    r = fill_booking_form("Test User", "a@b.com", "123", 2, ["D5"])
    assert_true(not r["success"])

def t_form_bad_name():
    r = fill_booking_form("X", "a@b.com", "9876543210", 2, ["D5"])
    assert_true(not r["success"])

test("Movie search returns ≥2 sites including BookMyShow", t_search_movies)
test("Bill search returns Paytm", t_search_bills)
test("Food search returns Zomato or Swiggy", t_search_food)
test("Extract listings returns shows with price/cinema/time", t_extract_listings)
test("Shows sorted by price ascending", t_shows_sorted_by_price)
test("Seat selection for 2 → 2 seats, ready_for_checkout", t_seat_selection_count)
test("Seat selection for 1 → 1 seat", t_seat_selection_single)
test("Valid form fill → success + 5 steps completed", t_form_valid)
test("Invalid email → rejected with email error", t_form_bad_email)
test("Invalid phone → rejected", t_form_bad_phone)
test("Name too short → rejected", t_form_bad_name)


# ══════════════════════════════════════════════════════════════
# PAYMENT TOOLS
# ══════════════════════════════════════════════════════════════
print("\n📦 MODULE: tools/payment_tools.py")

def t_total_math():
    r = calculate_total_amount(350, 2, "movies")
    assert_eq(r["subtotal"], 700)
    assert_eq(r["convenience_fee"], 30)
    expected = round(700 + 30 + (730 * 0.18), 2)
    assert_eq(r["total_payable"], expected)
    assert_eq(r["currency"], "INR")

def t_total_no_fee():
    r = calculate_total_amount(350, 2, "movies", apply_convenience_fee=False)
    assert_eq(r["convenience_fee"], 0)

def t_total_food_lower_gst():
    r = calculate_total_amount(200, 1, "food")
    assert_eq(r["gst_rate_percent"], 5)  # food has 5% GST

def t_budget_pass():
    r = check_budget_constraint(748.0, 800.0)
    assert_true(r["within_budget"])
    assert_true(r["savings"] > 0)
    assert_eq(r["overage"], 0)

def t_budget_fail():
    r = check_budget_constraint(900.0, 800.0)
    assert_true(not r["within_budget"])
    assert_eq(r["overage"], 100.0)
    assert_eq(r["savings"], 0)

def t_budget_exact():
    r = check_budget_constraint(800.0, 800.0)
    assert_true(r["within_budget"])
    assert_eq(r["savings"], 0.0)

def t_payment_success():
    details = {"category": "movies", "provider": "BMS", "seats": ["D5", "D6"], "quantity": 2}
    r = simulate_payment(details, 748.0, "UPI")
    assert_eq(r["status"], "SUCCESS")
    assert_eq(r["amount_paid"], 748.0)
    assert_true(r["booking_reference"].startswith("BMS-"))
    assert_true(len(r["simulation_steps"]) >= 5)
    assert_true("OTP" in " ".join(r["simulation_steps"]))

def t_payment_demo_note():
    r = simulate_payment({}, 100.0)
    assert_true("DEMO" in r["demo_note"] or "demo" in r["demo_note"].lower())

def t_booking_ref_format():
    ref = generate_booking_reference("movies", "BMS")
    parts = ref.split("-")
    assert_eq(len(parts), 3)
    assert_eq(parts[0], "BMS")
    assert_eq(len(parts[1]), 4)   # year
    assert_eq(len(parts[2]), 6)   # random hex

def t_booking_ref_flight():
    ref = generate_booking_reference("flights", "ANY")
    assert_true(ref.startswith("FLT-"))

test("Total math: subtotal + fee + 18% GST", t_total_math)
test("No fee when apply_convenience_fee=False", t_total_no_fee)
test("Food category uses 5% GST", t_total_food_lower_gst)
test("Budget PASS: ₹748 ≤ ₹800, savings > 0", t_budget_pass)
test("Budget FAIL: ₹900 > ₹800, overage=₹100", t_budget_fail)
test("Budget PASS at exact limit: ₹800 = ₹800", t_budget_exact)
test("Payment simulation: SUCCESS + BMS ref + OTP step", t_payment_success)
test("Payment simulation includes DEMO note", t_payment_demo_note)
test("Booking ref: BMS-YYYY-XXXXXX format", t_booking_ref_format)
test("Flight booking ref starts with FLT-", t_booking_ref_flight)


# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
total = passed + failed
print()
print("=" * 60)
print(f"  RESULTS:  {passed}/{total} passed  |  {failed} failed")
print("=" * 60)

if failures:
    print()
    print("  Failed tests:")
    for name, err in failures:
        print(f"   • {name}")
        print(f"     {err}")

if failed == 0:
    print("  🎉  ALL TESTS PASSED — TaskHive is production-ready!")
else:
    print(f"  ⚠️   {failed} test(s) need attention")
    sys.exit(1)
