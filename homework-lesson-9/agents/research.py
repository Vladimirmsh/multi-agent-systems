from agents.utils import create_agent
from config import RESEARCHER_PROMPT

def get_research_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,  # Підключаємо інструменти з MCP
        system_prompt=RESEARCHER_PROMPT,
    )