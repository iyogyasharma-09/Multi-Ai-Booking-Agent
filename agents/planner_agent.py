"""
TaskHive — Planner Agent
Decomposes user tasks into structured step-by-step execution plans.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from tools.task_tools import parse_user_intent, create_task_plan


PLANNER_SYSTEM_INSTRUCTIONS = """
You are the Planner Agent in the TaskHive multi-agent system.

Your role is to:
1. Understand the user's task request precisely
2. Use the parse_user_intent tool to extract structured information
3. Use the create_task_plan tool to generate an ordered execution plan
4. Return a clear, structured plan with steps assigned to appropriate agents

Always:
- Extract ALL constraints (budget, timing, quantity, preferences)
- Be specific about which booking websites to target
- Assign each step to the right specialized agent
- Output the plan in a clear, readable format

You are the BRAIN of the system. Think carefully before planning.
"""


def get_planner_agent() -> Agent:
    """Creates and returns a configured Planner Agent."""
    config = LocalAgentConfig(
        system_instructions=PLANNER_SYSTEM_INSTRUCTIONS,
        tools=[parse_user_intent, create_task_plan],
    )
    return Agent(config)


async def run_planner(task_description: str) -> str:
    """Runs the Planner Agent on a task description.
    
    Args:
        task_description: Natural language task from the user.
    
    Returns:
        Structured plan as text.
    """
    async with get_planner_agent() as agent:
        prompt = f"""
Please plan this task for our agent swarm:

USER TASK: "{task_description}"

Steps:
1. Use parse_user_intent to extract structured intent from the task
2. Use create_task_plan to generate the execution plan
3. Present the complete plan clearly, listing each step with its assigned agent

Be thorough and identify all constraints the user mentioned.
"""
        response = await agent.chat(prompt)
        return await response.text()


if __name__ == "__main__":
    task = "Book 2 tickets for Mission Impossible on Sunday evening under ₹800"
    result = asyncio.run(run_planner(task))
    print(result)
