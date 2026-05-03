from dotenv import load_dotenv
import uuid
import os

# 1. Завантажуємо змінні середовища НАЙПЕРШИМИ
load_dotenv()

# ЖОРСТКО вимикаємо LangSmith, щоб він не спамив у консоль
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_PROJECT"] = ""

from graph import support_system
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler  # ВАЖЛИВО: Оновлений імпорт тут!

# 2. Ініціалізуємо обробник Langfuse для трекінгу графа
langfuse_handler = CallbackHandler()

def main():
    print("="*50)
    print("🎧 Вітаємо у системі підтримки клієнтів!")
    print("Напишіть 'exit' або 'quit' для виходу.")
    print("="*50)
    
    while True:
        user_input = input("\n👤 Ви: ")
        if user_input.lower() in ["exit", "quit", "вихід"]:
            print("Дякуємо за звернення! До побачення.")
            break
            
        if not user_input.strip():
            continue
            
        print("⚙️ Система обробляє запит...")
        
        # Додаємо langfuse_handler у конфігурацію виклику
        config = {
            "configurable": {"thread_id": str(uuid.uuid4())},
            "callbacks": [langfuse_handler] 
        }
        
        try:
            # Використовуємо HumanMessage замість tuple
            result = support_system.invoke(
                {"messages": [HumanMessage(content=user_input)]}, 
                config=config
            )
            
            # Виводимо результат
            if "escalation_report" in result:
                print("\n👨‍💻 Агент: Ваш запит передано живому оператору. Ми зв'яжемося з вами найближчим часом.")
            elif "agent_response" in result:
                category = result.get('classification', {}).get('category', 'unknown')
                answer = result['agent_response'].get('answer', 'Немає відповіді.')
                confidence = result['agent_response'].get('confidence', 0.0)
                
                print(f"\n🤖 Відповідь (маршрут: {category}, впевненість: {confidence}):")
                print(answer)
        except Exception as e:
            print(f"\n❌ Виникла помилка: {e}")

if __name__ == "__main__":
    main()