# Multi-Agent Research System (з Langfuse Observability) 🕵️‍♂️📊

Цей проєкт — це мультиагентна система для автоматизованого пошуку, аналізу та критики інформації, побудована на базі **LangGraph** та **LangChain** (Gemini 3.1 Flash Lite). У рамках **Homework 12** система була інтегрована з **Langfuse** для забезпечення повноцінного моніторингу (Observability), хмарного управління промптами та автоматичної оцінки (LLM-as-a-Judge).

## 🌟 Основні можливості

* **Мультиагентна архітектура:** Роботу координує `Supervisor`, який делегує завдання агентам: `Planner` (планування), `Researcher` (пошук даних) та `Critic` (оцінка знахідок).
* **Langfuse Tracing:** Кожен запуск системи створює детальне дерево трейсів (Trace Tree) у Langfuse, що дозволяє відстежувати кожен виклик LLM, інструментів (tools) та суб-агентів.
* **Cloud Prompt Management:** Жодних захардкоджених промптів у коді. Всі системні промпти динамічно завантажуються з Langfuse Cloud.
* **LLM-as-a-Judge:** Автоматизована система оцінювання (online evaluation), яка аналізує якість роботи агентів (наприклад, повноту та релевантність) безпосередньо у хмарі.
* **Session Tracking:** Усі дії користувача групуються у сесії (Sessions) із фіксацією `user_id` та `session_id`.
* **Human-in-the-Loop (HITL):** Перед збереженням фінального звіту система зупиняється та просить схвалення (Approve/Edit/Reject) у користувача.

## 🛠 Технологічний стек

* **Мова:** Python 3.10+
* **Оркестрація агентів:** LangGraph
* **LLM:** Google Gemini (`gemini-3.1-flash-lite-preview`)
* **Observability & Analytics:** Langfuse
* **Векторна БД:** Qdrant (локально)
* **Інструменти:** MCP (Model Context Protocol), ACP

---

## 🚀 Інструкція зі встановлення та запуску

### 1. Клонування та налаштування середовища
Створіть віртуальне середовище та активуйте його:
```bash
python3 -m venv .venv
source .venv/bin/activate
Встановіть усі необхідні залежності:

Bash
pip install -r requirements.txt

2. Налаштування ключів доступу (.env)

Створіть файл .env у кореневій папці проєкту та додайте ваші ключі.

Фрагмент коду
# Google AI API Key
GOOGLE_API_KEY="ваш-ключ-gemini"

# Langfuse Observability Keys
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."

LANGFUSE_BASE_URL="https://cloud.langfuse.com"
LANGFUSE_HOST="https://cloud.langfuse.com"

3. Налаштування Langfuse Cloud

Перед запуском системи необхідно налаштувати Langfuse UI:

Зайдіть у розділ Prompts та створіть 4 промпти з міткою (label) production:

planner_prompt
researcher_prompt
critic_prompt
supervisor_prompt

Зайдіть у розділ Evaluators та налаштуйте мінімум 2 оцінювачі (наприклад, Relevance та Completeness), використовуючи змінні {{input}} та {{output}}.

4. Запуск системи

Щоб запустити головний цикл спілкування з мультиагентною системою, виконайте:

Bash
python3 main.py
📂 Структура проєкту
main.py — Точка входу, ініціалізація CallbackHandler та запуск циклу взаємодії (Graph Stream).
supervisor.py — Головний агент-координатор (оркестратор).
agents/ — Папка з суб-агентами:
planner.py, research.py, critic.py — логіка вузькоспеціалізованих агентів.
utils.py — допоміжні функції (завантаження промптів з Langfuse, створення агентів).
config.py — Конфігураційний файл, який зчитує .env.
requirements.txt — Список залежностей бібліотек.

📊 Observability (Як перевірити результати)
Після 3-5 успішних запитів у терміналі, перейдіть до Langfuse Cloud:
Traces: Ви побачите список запитів. Клікніть на будь-який, щоб розгорнути повне дерево викликів суб-агентів.
Sessions: Ваші запити будуть згруповані у єдину сесію (ідентифікатор генерується автоматично).
Scores: Перевірте вкладку оцінок у трейсі — ваш LLM-as-a-Judge автоматично проставить бали за виконання завдання.