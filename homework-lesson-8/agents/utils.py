from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

class HumanInTheLoopMiddleware:
    def __init__(self, interrupt_on: dict):
        self.interrupt_on = interrupt_on

def create_agent(model: str, tools: list, system_prompt: str, response_format=None, middleware=None, checkpointer=None):
    """Обгортка для створення агента з підтримкою структурованого виводу."""
    llm = ChatGoogleGenerativeAI(model=model, api_key=settings.GOOGLE_API_KEY, temperature=0)
    
    kwargs = {}
    if response_format:
        kwargs["response_format"] = response_format
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
        
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        **kwargs
    )