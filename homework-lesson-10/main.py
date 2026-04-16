import uuid
from langgraph.types import Command
from supervisor import supervisor

def main():
    print("="*60)
    print("🤖 Multi-Agent Research System (MCP/ACP Mode) запущено!")
    print("Напишіть 'exit' або 'quit' для виходу")
    print("="*60)

    # Унікальний thread_id для збереження контексту (пам'яті) графа
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
            
            # Початкова команда для запуску графа
            command = {"messages": [("user", user_input)]}
            
            while True:
                # Виконуємо граф і логуємо активність вузлів
                for event in supervisor.stream(command, config=config):
                    for node_name, output in event.items():
                        print(f"📍 [Graph Activity] Вузол: {node_name}")
                        
                        # Логуємо виклики інструментів (делегацію агентам)
                        if "messages" in output:
                            last_msg = output["messages"][-1]
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    print(f"   👉 Виклик інструменту: {tc['name']}")
                
                # Перевіряємо поточний стан після зупинки (через завершення або переривання)
                state = supervisor.get_state(config)
                
                # Якщо state.next не порожній - значить ми зупинилися через interrupt() (HITL)
                if state.next:
                    # Отримуємо дані переривання з останнього завдання
                    pending_task = state.tasks[0]
                    if pending_task.interrupts:
                        interrupt_data = pending_task.interrupts[0].value
                        
                        print("\n" + "="*60)
                        print(" ⏸️  ACTION REQUIRES APPROVAL (HITL)")
                        print("="*60)
                        print(f"   Tool:     {interrupt_data.get('tool')}")
                        print(f"   Filename: {interrupt_data.get('filename')}")
                        print(f"   Preview:  {interrupt_data.get('content')[:150]}...\n")

                        action = input(" 👉 approve / edit / reject: ").strip().lower()

                        if action == "approve":
                            command = Command(resume={"decisions": [{"type": "approve"}]})
                        elif action == "edit":
                            feedback = input(" ✏️  Вкажіть ваші зауваження: ")
                            command = Command(resume={"decisions": [{"type": "edit", "edited_action": {"feedback": feedback}}]})
                        elif action == "reject":
                            reason = input(" 🚫 Причина відмови: ")
                            command = Command(resume={"decisions": [{"type": "reject", "message": reason}]})
                        else:
                            print("⚠️ Невідома дія. Відхиляємо для безпеки.")
                            command = Command(resume={"decisions": [{"type": "reject", "message": "Unknown action"}]})
                        
                        continue # Продовжуємо цикл виконання з новою командою resume
                else:
                    # Якщо state.next порожній, граф завершив роботу
                    final_content = state.values['messages'][-1].content
                    print(f"\n✅ Фінальна відповідь Supervisor:\n{'-'*40}\n{final_content}\n{'-'*40}")
                    break
                    
        except Exception as e:
            print(f"\n❌ Сталася критична помилка в Main: {e}")

if __name__ == "__main__":
    main()