import json
import os
from datetime import datetime
from ddgs import DDGS  

def duckduckgo_search(query: str) -> str:
    """Шукає інформацію в інтернеті за допомогою DuckDuckGo."""
    try:
        # Використовуємо менеджер контексту для надійного підключення
        with DDGS() as ddgs:
            # Беремо топ-3 результати
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "Пошук не дав результатів."
            
            # Форматуємо результати так, щоб LLM було зручно їх читати
            formatted_results = "\n\n".join([
                f"Джерело: {r.get('href')}\nЗаголовок: {r.get('title')}\nТекст: {r.get('body')}" 
                for r in results
            ])
            return formatted_results
            
    except Exception as e:
        print(f"⚠️ [Debug] Помилка пошуку DDG: {str(e)}")
        return f"Помилка пошуку в інтернеті: {str(e)}"

def search_kb(query: str) -> str:
    """
    Пошук у локальній базі знань (RAG).
    TODO: Замінити цей mock на реальний пошук по векторній базі
    """
    mock_kb_context = """
    Тарифи: Basic ($10/міс), Pro ($30/міс), Enterprise (індивідуально).
    Політика повернення: Кошти можна повернути протягом 14 днів після оплати.
    """
    return mock_kb_context

def save_escalation_report(report_data: dict):
    """Зберігає звіт про ескалацію у файлову систему."""
    os.makedirs("escalations", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"escalations/report_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)
    print(f"\n📁 [Система] Звіт збережено у файл: {filename}")

def notify_slack(summary: str):
    """Надсилає нотифікацію оператору."""
    print(f"🚨 [SLACK NOTIFICATION MOCK] Нова ескалація: {summary}")