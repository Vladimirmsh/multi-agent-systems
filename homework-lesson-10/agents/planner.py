from agents.utils import create_agent
from config import PLANNER_PROMPT
from schemas import ResearchPlan

def get_planner_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,  # Підключаємо інструменти з MCP
        system_prompt=PLANNER_PROMPT,
        response_format=ResearchPlan,
    )