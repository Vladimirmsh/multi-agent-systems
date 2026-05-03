from agents.utils import create_agent, fetch_prompt
from schemas import ResearchPlan

def get_planner_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,
        system_prompt=fetch_prompt("planner_prompt"), # Динамічне завантаження
        response_format=ResearchPlan,
    )