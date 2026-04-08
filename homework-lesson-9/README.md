# Multi-Agent Research System: Distributed MCP/ACP Architecture (Homework 9)

Цей проєкт реалізує мультиагентну систему на базі LangGraph із застосуванням мікросервісної архітектури комунікації за допомогою протоколів **MCP** та **ACP**.

## 🏗️ Архітектура (Discovery → Delegate → Collect)
- **MCP Servers (Tools):** - `SearchMCP` (порт 8901) — обробляє пошукові запити (веб, RAG, читання URL).
  - `ReportMCP` (порт 8902) — зберігає звіти у файловій системі.
- **ACP Server (Agents):** - Хостить `Planner`, `Researcher` та `Critic` агентів (порт 8903). Кожен з них підключається як клієнт до `SearchMCP`.
- **Supervisor (Local Orchestrator):** - Локальний агент-оркестратор, який керує HITL-паузами. Він делегує завдання агентам через протокол ACP та звертається до `ReportMCP` для збереження фінального результату після схвалення користувачем.

## ⚙️ Вимоги та встановлення

1. **Клонуйте репозиторій або відкрийте папку проєкту.**
2. **Створіть та активуйте віртуальне середовище**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Для Mac/Linux
   # або .venv\Scripts\activate для Windows

   Встановіть залежності:
Bash
pip install -r requirements.txt
Налаштуйте змінні середовища:
Створіть файл .env та додайте:

Фрагмент коду
GOOGLE_API_KEY=ваш_справжній_ключ_тут
🚀 Порядок запуску (Microservices)
Оскільки тепер система розбита на сервіси, їх потрібно запускати в окремих терміналах:

Термінал 1: (Опціонально) Оновіть базу знань
Bash
python ingest.py

Термінал 2: Запустіть MCP сервери
Bash
python mcp_servers/search_mcp.py

Термінал 3:
Bash
python mcp_servers/report_mcp.py

Термінал 4: Запустіть ACP сервер (агенти)
Bash
python acp_server.py

Термінал 5: Запустіть головний клієнт (REPL + Supervisor)
Bash
python main.py


Приклади запитів:
1. "Compare RAG approaches: naive, sentence-window, and parent-child"
2. "Напиши короткий огляд фреймворку LangChain на основі моїх документів. Збережи у звіт."