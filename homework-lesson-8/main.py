import uuid
from langgraph.types import Command
from supervisor import supervisor

def main():
    print("="*60)
    print("🤖 Multi-Agent Research System (Supervisor Mode) запущено!")
    print("Напишіть 'exit' або 'quit' для виходу")
    print("="*60)

    # Унікальний thread_id для збереження контексту графа (HITL вимагає пам'яті)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            user_input = input("\nВи: ")
            if user_input.lower() in ['exit', 'quit', 'вихід']:
                print("Завершення роботи. До побачення!")
                break
            if not user_input.strip():
                continue

            print("\n⏳ Supervisor почав оркестрацію (Plan -> Research -> Critique)...\n")
            
            # Початковий інпут (формат Command)
            command = {"messages": [("user", user_input)]}
            
            while True:
                # Виконуємо граф поки він не зупиниться самостійно або через переривання
                for event in supervisor.stream(command, config=config):
                    pass # Тут можна додати логування проміжних кроків
                
                # Перевіряємо поточний стан після зупинки
                state = supervisor.get_state(config)
                
                # Якщо state.next не порожній - значить ми зупинилися через interrupt()
                if state.next:
                    pending_task = state.tasks[0]
                    if pending_task.interrupts:
                        interrupt_data = pending_task.interrupts[0].value
                        
                        print("\n============================================================")
                        print(" ⏸️  ACTION REQUIRES APPROVAL")
                        print("============================================================")
                        print(f"   Tool:  {interrupt_data.get('tool')}")
                        print(f"   Args:  filename={interrupt_data.get('filename')}")
                        print(f"   Preview: {interrupt_data.get('content')[:100]}...\n")

                        action = input(" 👉 approve / edit / reject: ").strip().lower()

                        if action == "approve":
                            command = Command(resume={"decisions": [{"type": "approve"}]})
                        elif action == "edit":
                            feedback = input(" ✏️  Your feedback: ")
                            command = Command(resume={"decisions": [{"type": "edit", "edited_action": {"feedback": feedback}}]})
                        elif action == "reject":
                            reason = input(" 🚫 Reason: ")
                            command = Command(resume={"decisions": [{"type": "reject", "message": reason}]})
                        else:
                            print("Невідома дія. Відхиляємо автоматично.")
                            command = Command(resume={"decisions": [{"type": "reject", "message": "Unknown action"}]})
                        
                        # Продовжуємо внутрішній while loop з новою `Command(resume=...)`
                        continue
                else:
                    # Граф завершив роботу
                    print(f"\n🤖 Фінальна відповідь Supervisor:\n{'-'*40}\n{state.values['messages'][-1].content}\n{'-'*40}")
                    break
                    
        except Exception as e:
            print(f"\n❌ Сталася помилка: {e}")

if __name__ == "__main__":
    main()