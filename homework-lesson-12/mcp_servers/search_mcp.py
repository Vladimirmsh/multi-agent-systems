import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from ddgs import DDGS
import trafilatura
from config import settings
from retriever import rag_retriever

mcp = FastMCP("SearchMCP")

@mcp.tool()
def web_search(query: str) -> str:
    """Шукає інформацію в інтернеті за запитом. Повертає список результатів."""
    try:
        results = DDGS().text(query, max_results=settings.MAX_SEARCH_RESULTS)
        if not results:
            return "Нічого не знайдено за цим запитом."
        return str(results)
    except Exception as e:
        return f"Помилка пошуку: {str(e)}"

@mcp.tool()
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

@mcp.tool()
def knowledge_search(query: str) -> str:
    """Шукає інформацію в локальній базі знань (RAG-система)."""
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

@mcp.resource("resource://knowledge-base-stats")
def get_kb_stats() -> str:
    """Повертає статистику локальної бази знань."""
    return "Статус: Активна\nКількість джерел (PDF): 3\nДата останнього оновлення: Квітень 2026"

if __name__ == "__main__":
    print(f"🚀 Запуск SearchMCP на порту {settings.SEARCH_MCP_PORT}...")
    mcp.run(transport="sse", port=settings.SEARCH_MCP_PORT)