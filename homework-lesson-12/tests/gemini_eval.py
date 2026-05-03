import time
import asyncio
from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

# Створюємо "замок", щоб DeepEval не міг відправляти кілька запитів одночасно
rate_limit_lock = asyncio.Lock()

class GeminiEvalModel(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini-3.1-flash-lite-preview"): 
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        # Синхронна затримка 6.5 секунд (близько 9 запитів на хвилину)
        time.sleep(6.5)
        res = self.model.invoke(prompt)
        return res.content

    async def a_generate(self, prompt: str) -> str:
        # Асинхронна черга: чекаємо, поки звільниться попередній запит
        async with rate_limit_lock:
            # Чекаємо 6.5 секунд перед кожним запитом
            await asyncio.sleep(6.5) 
            res = await self.model.ainvoke(prompt)
            return res.content

    def get_model_name(self):
        return "Google gemini-3.1-flash-lite-preview"

gemini_judge = GeminiEvalModel()