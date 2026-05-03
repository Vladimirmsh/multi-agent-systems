import os
import time
from dotenv import load_dotenv

# Завантажуємо змінні середовища НАЙПЕРШИМИ
load_dotenv()

# Вимикаємо LangSmith для чистішого виводу
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_PROJECT"] = ""

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from graph import support_system

# Додаємо автоматичну паузу між тестами, щоб не ловити помилку 429 (Rate Limit) від безкоштовного Gemini
@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    print("\n⏳ Пауза 15 секунд для скидання лімітів Gemini API...")
    time.sleep(15)

# Ініціалізуємо LLM-суддю
judge_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

def evaluate_with_llm(input_text: str, expected_category: str, actual_category: str) -> bool:
    prompt = f"""Ти незалежний суддя. 
    Текст користувача: '{input_text}'
    Очікувана категорія: {expected_category}
    Система визначила: {actual_category}
    Чи коректна класифікація системи? Відповідай ТІЛЬКИ 'YES' або 'NO'."""
    
    result = judge_llm.invoke(prompt).content.strip()
    return "YES" in result.upper()

# Тест-кейс 1: Product (Документація)
def test_router_product_classification():
    user_input = "Які у вас тарифи на Business підписку?"
    result = support_system.invoke({"messages": [HumanMessage(content=user_input)]})
    actual_category = result["classification"]["category"]
    assert evaluate_with_llm(user_input, "product", actual_category)

# Тест-кейс 2: General (Web Search)
def test_router_general_classification():
    user_input = "Як підключити ваш API до стороннього сервісу Zapier?"
    result = support_system.invoke({"messages": [HumanMessage(content=user_input)]})
    actual_category = result["classification"]["category"]
    assert evaluate_with_llm(user_input, "general", actual_category)

# Тест-кейс 3: Critical (Ескалація)
def test_escalation_routing():
    user_input = "ВАШ СЕРВІС ВПАВ І Я ВТРАЧАЮ ГРОШІ! ПОВЕРНІТЬ КОШТИ НЕГАЙНО!"
    result = support_system.invoke({"messages": [HumanMessage(content=user_input)]})
    assert "escalation_report" in result