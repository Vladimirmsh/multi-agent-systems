from pydantic import BaseModel, Field
from typing import Literal, List

class ClassificationOutput(BaseModel):
    category: Literal["product", "general", "critical"] = Field(
        description="Категорія запиту: 'product' для питань по системі/тарифах, 'general' для зовнішніх інтеграцій/сумісності, 'critical' для скарг та помилок."
    )
    urgency: Literal["low", "medium", "critical"] = Field(description="Терміновість запиту.")
    language: str = Field(description="Мова запиту клієнта (наприклад, 'uk', 'en').")

class AgentResponse(BaseModel):
    answer: str = Field(description="Текст відповіді клієнту")
    sources: List[str] = Field(description="Список використаних джерел (URLs або назви файлів KB)")
    confidence: float = Field(description="Впевненість у відповіді від 0.0 до 1.0")

class EscalationOutput(BaseModel):
    summary: str = Field(description="Короткий опис проблеми для оператора")
    category: str = Field(description="Категорія, визначена роутером")
    customer_message: str = Field(description="Оригінальне повідомлення клієнта")
    attempted_resolution: str = Field(description="Що система намагалася зробити (якщо був fallback)")