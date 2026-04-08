import httpx
import asyncio
import json
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from agents.utils import create_agent, HumanInTheLoopMiddleware
from config import SUPERVISOR_PROMPT, settings
from fastmcp.client import Client as FastMCPClient

report_mcp_client = FastMCPClient(settings.REPORT_MCP_URL)

def _call_acp_agent_sync(agent_name: str, payload: str) -> str:
    """Виклик ACP через HTTP з детальним логуванням."""
    data = {
        "agent_name": agent_name,
        "input": [{"role": "user", "parts": [{"content": payload}]}],
        "mode": "sync"
    }
    print(f"\n[Supervisor] 📨 Відправка до ACP-агента '{agent_name}'...")
    try:
        with httpx.Client(timeout=180.0) as client:
            res = client.post(f"{settings.ACP_URL}/runs", json=data)
            res.raise_for_status()
            result = res.json()
            
            # Робастне витягнення тексту
            # ACP може повертати або в parts[].content, або в parts[].text
            parts = result["output"][-1]["parts"][-1]
            content = parts.get("content") or parts.get("text") or str(parts)
            
            print(f"[Supervisor] 📩 Отримано відповідь від '{agent_name}' (довжина: {len(content)})")
            return content
    except Exception as e:
        error_msg = f"❌ Помилка ACP {agent_name}: {str(e)}"
        print(error_msg)
        return error_msg

@tool
def delegate_to_planner(request: str) -> str:
    """Декомпозує запит користувача у план дослідження."""
    return _call_acp_agent_sync("planner", request)

@tool
def delegate_to_researcher(plan_or_feedback: str) -> str:
    """Виконує дослідження."""
    return _call_acp_agent_sync("researcher", plan_or_feedback)

@tool
def delegate_to_critic(findings: str) -> str:
    """Оцінює знахідки."""
    return _call_acp_agent_sync("critic", findings)

@tool
def save_report(filename: str, content: str) -> str:
    """Зберігає Markdown-звіт. ПОТРЕБУЄ ЗАТВЕРДЖЕННЯ."""
    action = interrupt({"tool": "save_report", "filename": filename, "content": content})
    decision = action.get("decisions", [{}])[0]
    
    if decision.get("type") == "approve":
        async def execute():
            async with report_mcp_client:
                res = await report_mcp_client.call_tool("save_report", {"filename": filename, "content": content})
                return res.data if hasattr(res, 'data') else str(res)
        return asyncio.run(execute())
    return f"Дія {decision.get('type')}: {decision.get('message', 'Без коментарів')}"

supervisor = create_agent(
    model="gemini-3.1-flash-lite-preview",
    tools=[delegate_to_planner, delegate_to_researcher, delegate_to_critic, save_report],
    system_prompt=SUPERVISOR_PROMPT,
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"save_report": True})],
    checkpointer=InMemorySaver()
)