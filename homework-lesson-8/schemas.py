from pydantic import BaseModel, Field
from typing import Literal, List

class ResearchPlan(BaseModel):
    goal: str = Field(description="Що ми намагаємося з'ясувати (головна мета)")
    search_queries: List[str] = Field(description="Список конкретних пошукових запитів")
    sources_to_check: List[str] = Field(description="Джерела для перевірки: 'knowledge_base', 'web', або обидва")
    output_format: str = Field(description="Очікуваний формат фінального звіту (наприклад, порівняльна таблиця, плюси/мінуси)")

class CritiqueResult(BaseModel):
    verdict: Literal["APPROVE", "REVISE"] = Field(description="APPROVE якщо дослідження готове до звіту, REVISE якщо потребує доопрацювання")
    is_fresh: bool = Field(description="Чи базуються знахідки на актуальних даних (2025-2026 роки)?")
    is_complete: bool = Field(description="Чи повністю дослідження відповідає на початковий запит користувача?")
    is_well_structured: bool = Field(description="Чи логічно організовані знахідки?")
    strengths: List[str] = Field(description="Сильні сторони дослідження")
    gaps: List[str] = Field(description="Що пропущено, є застарілим або погано структурованим")
    revision_requests: List[str] = Field(description="Конкретні вказівки для Researcher, що саме треба виправити (якщо verdict == REVISE)")