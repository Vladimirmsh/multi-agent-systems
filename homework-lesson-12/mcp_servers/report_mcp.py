import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from config import settings

mcp = FastMCP("ReportMCP")

@mcp.tool()
def save_report(filename: str, content: str) -> str:
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
        return f"Успіх! Звіт збережено: {filepath}"
    except Exception as e:
        return f"Помилка збереження файлу: {str(e)}"

@mcp.resource("resource://output-dir")
def get_output_dir() -> str:
    """Повертає вміст папки output."""
    if not os.path.exists("output"):
        return "Директорія output/ порожня."
    files = os.listdir("output")
    return f"Шлях: output/\nФайли: {', '.join(files)}"

if __name__ == "__main__":
    print(f"🚀 Запуск ReportMCP на порту {settings.REPORT_MCP_PORT}...")
    mcp.run(transport="sse", port=settings.REPORT_MCP_PORT)