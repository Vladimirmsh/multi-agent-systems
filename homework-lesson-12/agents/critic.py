from agents.utils import create_agent, fetch_prompt
from schemas import CritiqueResult

def get_critic_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,
        system_prompt=fetch_prompt("critic_prompt"), # Динамічне завантаження
        response_format=CritiqueResult,
    )