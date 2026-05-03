import uuid
import getpass
from dotenv import load_dotenv 
from config import settings

# Завантажуємо змінні з .env у системне середовище ДО ініціалізації Langfuse
load_dotenv() 

from langgraph.types import Command
from supervisor import supervisor
from langfuse.langchain import CallbackHandler

def main():
    print("="*60)
    print("🤖 Multi-Agent Research System (MCP/ACP Mode) запущено!")
    print("Напишіть 'exit' або 'quit' для виходу")
    print("="*60)

    # Унікальний thread_id для збереження контексту
    thread_id = str(uuid.uuid4())
    user_id = getpass.getuser() # Отримуємо поточного юзера системи (або можете задати статично)
    
  # 1. Ініціалізуємо Langfuse CallbackHandler (тепер він створюється БЕЗ аргументів)
    langfuse_handler = CallbackHandler()

    # Додаємо callbacks та спеціальні метадані Langfuse у config LangGraph
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],
        "metadata": {
            "langfuse_session_id": thread_id,
            "langfuse_user_id": user_id,
            "langfuse_tags": ["hw-12", "multi-agent"]
        }
    }

    while True:
        try:
            user_input = input("\nВи: ")
            if user_input.lower() in ['exit', 'quit', 'вихід']:
                print("Завершення роботи. До побачення!")
                break
            if not user_input.strip():
                continue

            print("\n⏳ Supervisor почав оркестрацію (Plan -> Research -> Critique)...\n")
            
            command = {"messages": [("user", user_input)]}
            
            while True:
                # Виконуємо граф
                for event in supervisor.stream(command, config=config):
                    # ... [ваш існуючий код виводу дій залишається без змін] ...
                    for node_name, output in event.items():
                        print(f"📍 [Graph Activity] Вузол: {node_name}")
                        if "messages" in output:
                            last_msg = output["messages"][-1]
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    print(f"   👉 Виклик інструменту: {tc['name']}")
                
                state = supervisor.get_state(config)
                
                if state.next:
                    # ... [код Human-in-the-Loop залишається без змін] ...
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
                        
                        continue
                else:
                    final_content = state.values['messages'][-1].content
                    print(f"\n✅ Фінальна відповідь Supervisor:\n{'-'*40}\n{final_content}\n{'-'*40}")
                    break
                    
        except Exception as e:
            print(f"\n❌ Сталася критична помилка в Main: {e}")

if __name__ == "__main__":
    main()