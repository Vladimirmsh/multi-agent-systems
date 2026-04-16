from agents.utils import create_agent
from config import CRITIC_PROMPT
from schemas import CritiqueResult

def get_critic_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,  # Підключаємо інструменти з MCP
        system_prompt=CRITIC_PROMPT,
        response_format=CritiqueResult,
    )