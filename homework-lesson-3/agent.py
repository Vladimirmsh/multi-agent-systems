from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings, SYSTEM_PROMPT
from tools import TOOLS

def get_agent():
    # 1. Ініціалізація LLM (Gemini 3.1 Flash lite)
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )

    # 2. Ініціалізація пам'яті (для підтримки контексту діалогу)
    memory = MemorySaver()

    # 3. Створення ReAct агента через LangGraph
    # У нових версіях LangGraph параметр для системного промпту називається 'prompt'
    agent_executor = create_react_agent(
        model=llm,
        tools=TOOLS,
        checkpointer=memory,
        prompt=SYSTEM_PROMPT,
    )
    
    return agent_executor