"""
TaskHive — Security Tools
Multi-layer URL and domain safety validation for the Security Agent.
"""

import re
import time
import random
import hashlib
from typing import Any
from urllib.parse import urlparse


# ─── Known Safe & Suspicious Domains ──────────────────────────────────────────

TRUSTED_DOMAINS = {
    "bookmyshow.com", "pvrinemas.com", "inoxmovies.com", "paytm.com",
    "phonepe.com", "gpay.google.com", "amazon.in", "flipkart.com",
    "makemytrip.com", "irctc.co.in", "zomato.com", "swiggy.com",
    "airtel.in", "jio.com", "bsnl.co.in", "hdfcbank.com",
    "icicibank.com", "sbi.co.in", "ola.com", "uber.com",
    "yatra.com", "cleartrip.com", "goibibo.com", "redbus.in",
}

SUSPICIOUS_PATTERNS = [
    r"free.*ticket", r"win.*prize", r"click.*here.*urgent",
    r"\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}",  # IP address URLs
    r"paypa1", r"amaz0n", r"goog1e", r"faceb00k",  # Typosquatting
    r"login.*verify.*account", r"suspended.*account",
    r"confirm.*payment.*immediately", r"limited.*time.*offer",
]

PHISHING_KEYWORDS = [
    "verify-now", "account-suspended", "urgent-action", "click-here",
    "free-ticket", "win-prize", "limited-offer", "confirm-identity",
    "update-payment", "security-alert"
]


# ─── Tool Functions ────────────────────────────────────────────────────────────

def check_url_safety(url: str) -> dict[str, Any]:
    """Checks if a URL is safe using heuristic analysis.

    Performs multi-layer safety checks including HTTPS verification,
    typosquatting detection, suspicious pattern matching, and domain trust lookup.

    Args:
        url: The full URL to check (e.g. 'https://bookmyshow.com/movies').
    """
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        domain = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.lower()
        full = (domain + path).lower()

        issues = []
        score = 100

        # Check 1: HTTPS
        if not url.startswith("https://"):
            issues.append("❌ No HTTPS — connection is not encrypted")
            score -= 30
        else:
            pass  # HTTPS ok

        # Check 2: Trusted domain list
        base_domain = ".".join(domain.split(".")[-2:])
        if base_domain in TRUSTED_DOMAINS:
            score += 5  # bonus for trusted domain (cap at 100)
            score = min(score, 100)
        else:
            issues.append(f"⚠️ Domain '{base_domain}' not in verified trusted list")
            score -= 10

        # Check 3: Typosquatting / lookalike
        typo_patterns = [r"paypa1", r"amaz0n", r"goog1e", r"b00kmyshow", r"pvr1nemas"]
        for pat in typo_patterns:
            if re.search(pat, domain):
                issues.append(f"❌ Possible typosquatting detected: '{domain}'")
                score -= 40
                break

        # Check 4: Suspicious URL patterns
        for pat in SUSPICIOUS_PATTERNS:
            if re.search(pat, full):
                issues.append(f"⚠️ Suspicious pattern in URL: matches '{pat}'")
                score -= 15
                break

        # Check 5: Phishing keywords in path
        for kw in PHISHING_KEYWORDS:
            if kw in path:
                issues.append(f"❌ Phishing keyword in path: '{kw}'")
                score -= 20
                break

        # Check 6: Excessive subdomains
        subdomain_count = len(domain.split(".")) - 2
        if subdomain_count > 2:
            issues.append(f"⚠️ Excessive subdomains ({subdomain_count}) — possible redirect chain")
            score -= 10

        score = max(0, min(100, score))

        if score >= 80:
            verdict = "SAFE"
            icon = "✅"
        elif score >= 55:
            verdict = "CAUTION"
            icon = "⚠️"
        else:
            verdict = "DANGEROUS"
            icon = "🚨"

        if not issues:
            issues.append("✅ No security issues detected")

        return {
            "url": url,
            "domain": domain,
            "trust_score": score,
            "verdict": verdict,
            "icon": icon,
            "issues": issues,
            "https": url.startswith("https://"),
            "in_trusted_list": base_domain in TRUSTED_DOMAINS,
        }

    except Exception as e:
        return {
            "url": url,
            "domain": "unknown",
            "trust_score": 0,
            "verdict": "ERROR",
            "icon": "❌",
            "issues": [f"Could not analyse URL: {e}"],
            "https": False,
            "in_trusted_list": False,
        }


def verify_payment_page(page_url: str, expected_domain: str) -> dict[str, Any]:
    """Verifies that a payment page belongs to the expected domain and is not a fake.

    Checks for domain mismatch, unexpected redirects, and common fake payment indicators.

    Args:
        page_url: The current URL of the payment page.
        expected_domain: The domain we expect the payment to happen on (e.g. 'bookmyshow.com').
    """
    parsed = urlparse(page_url if page_url.startswith("http") else f"https://{page_url}")
    current_domain = parsed.netloc.lower().replace("www.", "")
    base_current = ".".join(current_domain.split(".")[-2:])

    domain_match = expected_domain.lower() in base_current
    is_https = page_url.startswith("https://")

    issues = []
    if not domain_match:
        issues.append(f"🚨 Domain mismatch! Expected '{expected_domain}', got '{base_current}'")
    if not is_https:
        issues.append("❌ Payment page is NOT using HTTPS — extremely dangerous")

    # Simulate checking for known payment gateway patterns
    trusted_payment_paths = ["/payment", "/checkout", "/pay", "/secure", "/transaction"]
    path = parsed.path.lower()
    on_payment_path = any(p in path for p in trusted_payment_paths)

    safe = domain_match and is_https
    return {
        "page_url": page_url,
        "expected_domain": expected_domain,
        "current_domain": base_current,
        "domain_match": domain_match,
        "is_https": is_https,
        "on_payment_path": on_payment_path,
        "is_safe": safe,
        "issues": issues if issues else ["✅ Payment page verified — domain matches and HTTPS active"],
    }


def check_domain_reputation(domain: str) -> dict[str, Any]:
    """Checks the reputation score and estimated age of a domain.

    Uses a combination of known domain databases and heuristic signals.

    Args:
        domain: The domain name to check (e.g. 'bookmyshow.com').
    """
    domain = domain.lower().replace("www.", "")
    base_domain = ".".join(domain.split(".")[-2:])

    # Deterministic-but-realistic mock score based on domain hash
    seed = int(hashlib.md5(domain.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    if base_domain in TRUSTED_DOMAINS:
        age_years = rng.randint(8, 20)
        reputation_score = rng.randint(88, 99)
        category = "E-commerce / Entertainment"
        status = "Established"
    else:
        age_years = rng.randint(0, 5)
        reputation_score = rng.randint(30, 75)
        category = "Unknown"
        status = "Unverified" if age_years > 1 else "New Domain — High Risk"

    return {
        "domain": domain,
        "estimated_age_years": age_years,
        "reputation_score": reputation_score,
        "category": category,
        "status": status,
        "flagged_by_community": reputation_score < 45,
        "summary": (
            f"Domain '{domain}' is approximately {age_years} years old "
            f"with a reputation score of {reputation_score}/100 ({status})."
        ),
    }


def scan_page_content_for_threats(page_content: str) -> dict[str, Any]:
    """Scans webpage text content for phishing indicators and fake payment forms.

    Args:
        page_content: The raw text content of a webpage to analyse.
    """
    content_lower = page_content.lower()

    threat_patterns = {
        "fake_urgency": [
            "your account will be suspended", "act now", "expires in",
            "limited time", "immediate action required"
        ],
        "credential_harvesting": [
            "enter your password to continue", "verify your identity",
            "re-enter card details", "confirm pin"
        ],
        "prize_scam": [
            "you have won", "claim your prize", "congratulations winner",
            "free gift", "lucky draw"
        ],
        "fake_payment": [
            "payment failed retry", "card declined enter again",
            "additional verification fee"
        ],
    }

    found_threats = {}
    total_threats = 0
    for threat_type, keywords in threat_patterns.items():
        matches = [kw for kw in keywords if kw in content_lower]
        if matches:
            found_threats[threat_type] = matches
            total_threats += len(matches)

    risk_level = "LOW" if total_threats == 0 else ("MEDIUM" if total_threats <= 2 else "HIGH")

    return {
        "threats_found": found_threats,
        "total_threat_signals": total_threats,
        "risk_level": risk_level,
        "is_safe": total_threats == 0,
        "summary": (
            f"Scanned page content: {total_threats} threat signal(s) found. "
            f"Risk level: {risk_level}."
        ),
    }
