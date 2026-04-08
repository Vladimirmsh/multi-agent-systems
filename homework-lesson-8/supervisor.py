from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from agents.utils import create_agent, HumanInTheLoopMiddleware
from config import SUPERVISOR_PROMPT
from tools import save_report
from agents.planner import planner_agent
from agents.research import research_agent
from agents.critic import critic_agent

@tool
def plan(request: str) -> str:
    """Декомпозує запит користувача у план дослідження. Завжди викликай це першим."""
    res = planner_agent.invoke({"messages": [("user", request)]})
    return str(res["messages"][-1].content)

@tool
def research(plan_or_feedback: str) -> str:
    """Виконує дослідження за планом або виправляє звіт за фідбеком критика."""
    res = research_agent.invoke({"messages": [("user", plan_or_feedback)]})
    return str(res["messages"][-1].content)

@tool
def critique(findings: str) -> str:
    """Оцінює знахідки. Викликай після завершення research."""
    res = critic_agent.invoke({"messages": [("user", findings)]})
    return str(res["messages"][-1].content)

supervisor = create_agent(
    model="gemini-3.1-flash-lite-preview",
    tools=[plan, research, critique, save_report],
    system_prompt=SUPERVISOR_PROMPT,
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"save_report": True}),
    ],
    checkpointer=InMemorySaver()
)