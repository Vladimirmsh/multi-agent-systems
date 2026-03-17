import uuid
from agent import get_agent
from config import settings

def main():
    print("="*50)
    print("🤖 Research Agent запущено! (Напишіть 'exit' або 'quit' для виходу)")
    print("="*50)

    agent_executor = get_agent()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": settings.MAX_AGENT_ITERATIONS}

    while True:
        try:
            user_input = input("\nВи: ")
            if user_input.lower() in ['exit', 'quit', 'вихід']:
                print("Завершення роботи. До побачення!")
                break
            if not user_input.strip():
                continue

            print("\n⏳ Агент почав дослідження...\n")
            
            events = agent_executor.stream(
                {"messages": [("user", user_input)]},
                config=config,
                stream_mode="values"
            )
            
            for event in events:
                message = event["messages"][-1]
                
                # Якщо агент викликає інструмент (гуглить або читає) - показуємо це!
                if message.type == "ai" and message.tool_calls:
                    for tool_call in message.tool_calls:
                        print(f" 🛠  Агент використовує: {tool_call['name']} (Параметри: {tool_call['args']})")
                
                # Якщо це фінальна відповідь
                elif message.type == "ai" and not message.tool_calls:
                    print(f"\n🤖 Фінальна відповідь:\n{message.content}")
                    
        except Exception as e:
            print(f"\n❌ Сталася помилка: {e}")

if __name__ == "__main__":
    main()