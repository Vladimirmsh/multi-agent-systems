import typing
import uvicorn.config

# Патч для сумісності з uvicorn
if not hasattr(uvicorn.config, 'LoopSetupType'):
    uvicorn.config.LoopSetupType = typing.Any  

# Патч для SSL (якщо acp-sdk передає порожні шляхи)
if hasattr(uvicorn.config, 'create_ssl_context'):
    original_ssl = uvicorn.config.create_ssl_context
    def safe_ssl(*args, **kwargs):
        try: return original_ssl(*args, **kwargs)
        except Exception: return None
    uvicorn.config.create_ssl_context = safe_ssl

import asyncio
from acp_sdk.server import Server as ACPServer
from acp_sdk.models import Message, MessagePart
from fastmcp.client import Client as FastMCPClient
from mcp_utils import mcp_tools_to_langchain
from agents.planner import get_planner_agent
from agents.research import get_research_agent
from agents.critic import get_critic_agent
from config import settings

server = ACPServer()

print("🔌 Підключення до SearchMCP...")
search_mcp_client = FastMCPClient(settings.SEARCH_MCP_URL)
mcp_tools = mcp_tools_to_langchain(search_mcp_client)

print("🤖 Ініціалізація агентів...")
planner_agent = get_planner_agent(mcp_tools)
research_agent = get_research_agent(mcp_tools)
critic_agent = get_critic_agent(mcp_tools)

def extract_text(input_msgs: list[Message]) -> str:
    try: return input_msgs[-1].parts[-1].content
    except Exception: return str(input_msgs)

@server.agent("planner")
async def planner(input: list[Message]):
    text = extract_text(input)
    print(f"\n[ACP] 🧠 Planner отримав запит: {text[:100]}...")
    res = await asyncio.to_thread(planner_agent.invoke, {"messages": [("user", text)]})
    content = str(res["messages"][-1].content)
    print(f"[ACP] ✅ Planner завершив. Результат: {content[:50]}...")
    yield Message(role="agent", parts=[MessagePart(content=content)])

@server.agent("researcher")
async def researcher(input: list[Message]):
    text = extract_text(input)
    print(f"\n[ACP] 🔍 Researcher почав дослідження...")
    res = await asyncio.to_thread(research_agent.invoke, {"messages": [("user", text)]})
    print(f"[ACP] ✅ Researcher завершив.")
    yield Message(role="agent", parts=[MessagePart(content=str(res["messages"][-1].content))])

@server.agent("critic")
async def critic(input: list[Message]):
    text = extract_text(input)
    print(f"\n[ACP] ⚖️ Critic перевіряє дані...")
    res = await asyncio.to_thread(critic_agent.invoke, {"messages": [("user", text)]})
    print(f"[ACP] ✅ Critic надав вердикт.")
    yield Message(role="agent", parts=[MessagePart(content=str(res["messages"][-1].content))])

if __name__ == "__main__":
    print(f"🚀 ACP Server запущено на порту {settings.ACP_PORT}")
    server.run(port=settings.ACP_PORT)