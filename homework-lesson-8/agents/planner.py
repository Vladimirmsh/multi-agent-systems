from agents.utils import create_agent
from tools import web_search, knowledge_search
from config import PLANNER_PROMPT
from schemas import ResearchPlan

planner_agent = create_agent(
    model="gemini-3.1-flash-lite-preview",
    tools=[web_search, knowledge_search],
    system_prompt=PLANNER_PROMPT,
    response_format=ResearchPlan,
)