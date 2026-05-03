from agents.utils import create_agent, fetch_prompt

def get_research_agent(mcp_tools):
    return create_agent(
        model="gemini-3.1-flash-lite-preview",
        tools=mcp_tools,
        system_prompt=fetch_prompt("researcher_prompt"), # Динамічне завантаження
    )