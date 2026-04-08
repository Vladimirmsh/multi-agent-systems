import os
from datetime import datetime
from ddgs import DDGS
import trafilatura
from langchain_core.tools import tool
from langgraph.types import interrupt
from config import settings

@tool
def get_current_datetime() -> str:
    """Повертає поточну дату та час."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def web_search(query: str) -> str:
    """Шукає інформацію в інтернеті за запитом. Повертає список результатів."""
    try:
        results = DDGS().text(query, max_results=settings.MAX_SEARCH_RESULTS)
        if not results:
            return "Нічого не знайдено за цим запитом."
        return str(results)
    except Exception as e:
        return f"Помилка пошуку: {str(e)}"

@tool
def read_url(url: str) -> str:
    """Завантажує та витягує основний текст із вказаного URL."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"Помилка завантаження сторінки {url}."
        text = trafilatura.extract(downloaded)
        if not text:
            return f"Помилка витягнення тексту зі сторінки {url}."
        if len(text) > settings.MAX_URL_TEXT_LENGTH:
            text = text[:settings.MAX_URL_TEXT_LENGTH] + "\n\n...[ТЕКСТ ОБРІЗАНО]..."
        return text
    except Exception as e:
        return f"Помилка під час читання URL: {str(e)}"

@tool
def knowledge_search(query: str) -> str:
    """Шукає інформацію в локальній базі знань (RAG-система)."""
    from retriever import rag_retriever
    if not rag_retriever:
        return "Помилка: RAG систему не ініціалізовано."
    try:
        docs = rag_retriever.invoke(query)
        if not docs:
            return "В базі знань нічого не знайдено."
        result = ["Знайдено в базі знань:\n"]
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Невідомо')
            result.append(f"--- Джерело: {source} ---\n{doc.page_content}\n")
        return "\n".join(result)
    except Exception as e:
        return f"Помилка пошуку в базі знань: {str(e)}"

@tool
def save_report(filename: str, content: str) -> str:
    """Зберігає згенерований Markdown-звіт у файл. ПОТРЕБУЄ ЗАТВЕРДЖЕННЯ КОРИСТУВАЧА."""
    try:
        # HITL: Зупиняємо виконання та чекаємо рішення користувача
        action = interrupt({"tool": "save_report", "filename": filename, "content": content})
        
        decisions = action.get("decisions", [])
        if not decisions:
            return "Користувач не надав рішення."
            
        decision = decisions[0]
        
        if decision.get("type") == "approve":
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            safe_filename = os.path.basename(filename)
            if not safe_filename.endswith(".md"):
                safe_filename += ".md"
            filepath = os.path.join(output_dir, safe_filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Успіх! Звіт збережено: {filepath}"
            
        elif decision.get("type") == "edit":
            feedback = decision.get("edited_action", {}).get("feedback", "Без коментарів")
            return f"Звіт ВІДХИЛЕНО. Користувач просить внести зміни: {feedback}. Виправ звіт і виклич збереження знову."
            
        elif decision.get("type") == "reject":
            reason = decision.get("message", "Без пояснень")
            return f"Звіт ВІДХИЛЕНО повністю. Причина: {reason}."
            
        return "Невідома дія від користувача."
    except Exception as e:
        return f"Помилка збереження файлу: {str(e)}"