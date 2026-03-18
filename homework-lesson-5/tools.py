import os
from datetime import datetime
from ddgs import DDGS
import trafilatura
from config import settings

def get_current_datetime() -> str:
    """Повертає поточну дату та час."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query: str) -> str:
    """Шукає інформацію в інтернеті за запитом."""
    try:
        # В новой версии параметры немного изменились, и возвращается просто список словарей
        results = DDGS().text(query, max_results=settings.MAX_SEARCH_RESULTS)
        if not results:
            return "Нічого не знайдено за цим запитом. Спробуй інші ключові слова."
        return str(results)
    except Exception as e:
        return f"Помилка пошуку: {str(e)}"

def read_url(url: str) -> str:
    """Завантажує та витягує основний текст із вказаного URL."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"Помилка: Не вдалося завантажити сторінку {url}."
        
        text = trafilatura.extract(downloaded)
        if not text:
            return f"Помилка: Не вдалося витягти текст зі сторінки {url}."
        
        if len(text) > settings.MAX_URL_TEXT_LENGTH:
            text = text[:settings.MAX_URL_TEXT_LENGTH] + "\n\n...[ТЕКСТ ОБРІЗАНО ЧЕРЕЗ ЛІМІТ]..."
            
        return text
    except Exception as e:
        return f"Помилка під час читання URL: {str(e)}"

def knowledge_search(query: str) -> str:
    """Шукає інформацію в локальній базі знань (RAG-система)."""
    from retriever import rag_retriever
    
    if not rag_retriever:
        return "Помилка: RAG систему не ініціалізовано. Перевірте, чи завантажені документи (запустіть ingest.py)."

    try:
        docs = rag_retriever.invoke(query)
        if not docs:
            return "В базі знань нічого не знайдено за цим запитом."

        result = ["Знайдено наступну інформацію в базі знань:\n"]
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Невідоме джерело')
            page = doc.metadata.get('page', 'Невідома сторінка')
            result.append(f"--- Документ {i+1} (Джерело: {source}, Сторінка: {page}) ---\n{doc.page_content}\n")

        return "\n".join(result)
    except Exception as e:
        return f"Помилка пошуку в базі знань: {str(e)}"

def write_report(filename: str, content: str) -> str:
    """Зберігає згенерований Markdown-звіт у файл."""
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


# Словник для швидкого виклику функцій по імені
AVAILABLE_TOOLS = {
    "get_current_datetime": get_current_datetime,
    "web_search": web_search,
    "read_url": read_url,
    "knowledge_search": knowledge_search,
    "write_report": write_report
}

# Опис інструментів у форматі JSON Schema (OpenAI/Gemini Tool Calling standard)
TOOLS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Повертає поточну дату та час. Використовуй це перед пошуком, щоб розуміти актуальний контекст часу.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Шукає інформацію в інтернеті. Повертає список результатів із ключами 'title', 'href' (URL) та 'body'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Пошуковий запит (краще англійською або українською)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Завантажує та витягує основний корисний текст із вказаного URL. Використовуй для глибокого читання статей.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Пряме посилання на сторінку (http/https)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "knowledge_search",
            "description": "Шукає інформацію в локальній базі знань (завантажених PDF документах). Використовуй для відповідей на питання, що стосуються документів користувача.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Запит для пошуку по базі знань."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_report",
            "description": "Зберігає згенерований Markdown-звіт у файл.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Назва файлу (наприклад, 'rag_comparison.md')"},
                    "content": {"type": "string", "description": "Повний текст звіту у форматі Markdown"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]