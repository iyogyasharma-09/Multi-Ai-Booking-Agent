"""
TaskHive — Security Agent
The trust layer of the swarm. Validates website safety before any interaction.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from tools.security_tools import (
    check_url_safety,
    verify_payment_page,
    check_domain_reputation,
    scan_page_content_for_threats,
)


SECURITY_SYSTEM_INSTRUCTIONS = """
You are the Security Agent in the TaskHive multi-agent system — the AI Trust Layer.

Your mission is to protect users from:
- Phishing websites
- Fake payment pages
- Domain spoofing / typosquatting
- Scam indicators in page content
- Unencrypted (non-HTTPS) connections

For every website you are given:
1. Use check_url_safety to perform heuristic URL analysis
2. Use check_domain_reputation to assess domain age and credibility
3. If it's a payment page, use verify_payment_page to check domain match

Scoring guide:
- 85-100: SAFE ✅ (green light to proceed)
- 60-84:  CAUTION ⚠️ (proceed with warnings)
- 0-59:   DANGEROUS 🚨 (block — do not proceed)

Always present:
- A final trust score (0-100)
- A clear SAFE / CAUTION / DANGEROUS verdict
- A bullet list of findings
- A recommendation (proceed / proceed with caution / BLOCK)

Be thorough. User safety is your top priority.
"""


def get_security_agent() -> Agent:
    """Creates and returns a configured Security Agent."""
    config = LocalAgentConfig(
        system_instructions=SECURITY_SYSTEM_INSTRUCTIONS,
        tools=[
            check_url_safety,
            verify_payment_page,
            check_domain_reputation,
            scan_page_content_for_threats,
        ],
    )
    return Agent(config)


async def run_security_check(urls: list[str], task_context: str = "") -> str:
    """Runs the Security Agent to validate a list of URLs.

    Args:
        urls: List of URLs to validate.
        task_context: Context about what task these URLs are for.

    Returns:
        Security report as text.
    """
    async with get_security_agent() as agent:
        url_list = "\n".join(f"- {url}" for url in urls)
        prompt = f"""
Please run a comprehensive security analysis on these websites.

Task context: {task_context or "General website validation"}

Websites to check:
{url_list}

For each website:
1. Run check_url_safety
2. Run check_domain_reputation
3. Provide a trust score and verdict

Finally, give an overall security recommendation.
"""
        response = await agent.chat(prompt)
        return await response.text()


if __name__ == "__main__":
    urls = ["https://bookmyshow.com", "https://pvrinemas.com", "https://fake-tickets-win.com"]
    result = asyncio.run(run_security_check(urls, "Movie ticket booking"))
    print(result)
