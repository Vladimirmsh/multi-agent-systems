from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings
from langfuse import Langfuse
from functools import lru_cache

# ДОДАЄМО ЦЕЙ РЯДОК ДЛЯ ДЕБАГУ:
print(f"🔑 DEBUG LANGFUSE: Host={settings.LANGFUSE_BASE_URL}, Key={settings.LANGFUSE_PUBLIC_KEY[:10]}...")

# Ініціалізація клієнта Langfuse
langfuse_client = Langfuse(
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    secret_key=settings.LANGFUSE_SECRET_KEY,
    host=settings.LANGFUSE_BASE_URL
)
@lru_cache(maxsize=None)
def fetch_prompt(prompt_name: str) -> str:
    """Завантажує промпт з Langfuse Cloud з кешуванням."""
    print(f"📥 Завантаження промпту '{prompt_name}' з Langfuse...")
    prompt = langfuse_client.get_prompt(prompt_name, label="production")
    return prompt.compile()

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