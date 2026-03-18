from agent import ResearchAgent

def main():
    print("="*60)
    print("🤖 Research Agent (Custom ReAct Loop) запущено!")
    print("Напишіть 'exit' або 'quit' для виходу")
    print("="*60)

    # Створюємо екземпляр нашого агента (він сам тримає історію)
    agent = ResearchAgent()

    while True:
        try:
            user_input = input("\nВи: ")
            if user_input.lower() in ['exit', 'quit', 'вихід']:
                print("Завершення роботи. До побачення!")
                break
            if not user_input.strip():
                continue

            print("\n⏳ Агент почав дослідження (Multi-step Reasoning)...\n")
            
            # Викликаємо метод чату, який запускає ReAct цикл
            final_response = agent.chat(user_input)
            
            # Виводимо фінальну відповідь після завершення всіх циклів
            print(f"\n🤖 Фінальна відповідь агента:\n{'-'*40}\n{final_response}\n{'-'*40}")
                    
        except Exception as e:
            print(f"\n❌ Сталася непередбачувана помилка: {e}")

if __name__ == "__main__":
    main()