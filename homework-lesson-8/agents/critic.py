from agents.utils import create_agent
from tools import web_search, read_url, knowledge_search
from config import CRITIC_PROMPT
from schemas import CritiqueResult

critic_agent = create_agent(
    model="gemini-3.1-flash-lite-preview",
    tools=[web_search, read_url, knowledge_search],
    system_prompt=CRITIC_PROMPT,
    response_format=CritiqueResult,
)