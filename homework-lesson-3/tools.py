import os
from datetime import datetime
from langchain_core.tools import tool
from ddgs import DDGS  # <--- Використовуємо правильну нову назву
import trafilatura
from config import settings

@tool
def get_current_datetime() -> str:
    """Повертає поточну дату та час. Використовуй це перед пошуком, щоб розуміти актуальний контекст часу."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def web_search(query: str) -> list[dict]:
    """
    Шукає інформацію в інтернеті за запитом. 
    Повертає список словників із ключами 'title', 'href' (URL) та 'body' (короткий сніпет).
    """
    try:
        # Робимо пошук
        results_generator = DDGS().text(query, max_results=settings.MAX_SEARCH_RESULTS)
        
        # ВАЖЛИВО: перетворюємо генератор на список, щоб LLM могла прочитати текст
        results = list(results_generator)
        
        if not results:
            return [{"error": "Нічого не знайдено за цим запитом. Спробуй інші ключові слова."}]
            
        return results
    except Exception as e:
        return [{"error": f"Помилка пошуку: {str(e)}"}]

@tool
def read_url(url: str) -> str:
    """
    Завантажує та витягує основний текст із вказаного URL.
    Використовуй це для глибокого читання статей, знайдених через web_search.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"Помилка: Не вдалося завантажити сторінку {url} (можливо, блокування або таймаут)."
        
        text = trafilatura.extract(downloaded)
        if not text:
            return f"Помилка: Не вдалося витягти текст зі сторінки {url}."
        
        # Context Engineering: обрізаємо текст
        if len(text) > settings.MAX_URL_TEXT_LENGTH:
            text = text[:settings.MAX_URL_TEXT_LENGTH] + "\n\n...[ТЕКСТ ОБРІЗАНО ЧЕРЕЗ ЛІМІТ]..."
            
        return text
    except Exception as e:
        return f"Помилка під час читання URL: {str(e)}"

@tool
def write_report(filename: str, content: str) -> str:
    """
    Зберігає згенерований Markdown-звіт у файл.
    filename: назва файлу (наприклад, 'rag_comparison.md').
    content: повний текст звіту у форматі Markdown.
    """
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        safe_filename = os.path.basename(filename)
        if not safe_filename.endswith(".md"):
            safe_filename += ".md"
            
        filepath = os.path.join(output_dir, safe_filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Успіх! Звіт збережено за шляхом: {filepath}"
    except Exception as e:
        return f"Помилка збереження файлу: {str(e)}"

# Список інструментів
TOOLS = [get_current_datetime, web_search, read_url, write_report]