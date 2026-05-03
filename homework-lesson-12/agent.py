from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from config import settings, SYSTEM_PROMPT
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMAS

class ResearchAgent:
    def __init__(self):
        # 1. Ініціалізація LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )
        
        # 2. Передаємо моделі наші JSON Schemas інструментів
        self.llm_with_tools = self.llm.bind_tools(TOOLS_SCHEMAS)
        
        # 3. Власна "пам'ять" агента (замість MemorySaver)
        self.messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]

    def chat(self, user_input: str):
        # Додаємо запит користувача в історію
        self.messages.append(HumanMessage(content=user_input))
        
        iterations = 0
        
        # 4. ВЛАСНИЙ ReAct LOOP
        while iterations < settings.MAX_AGENT_ITERATIONS:
            # Відправляємо поточну історію моделі
            response = self.llm_with_tools.invoke(self.messages)
            
            # Зберігаємо відповідь моделі в історію
            self.messages.append(response)
            
            # Умова виходу: якщо модель не викликає інструменти, значить це фінальна текстова відповідь
            if not response.tool_calls:
                return response.content
                
            # Якщо є виклики інструментів, обробляємо їх
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Логування кроку (Дія)
                print(f"\n🔧 Tool call: {tool_name}({tool_args})")
                
                # Виклик функції
                if tool_name in AVAILABLE_TOOLS:
                    try:
                        func = AVAILABLE_TOOLS[tool_name]
                        # Викликаємо функцію, передаючи аргументи як kwargs
                        result = str(func(**tool_args))
                    except Exception as e:
                        result = f"Error execution tool {tool_name}: {str(e)}"
                else:
                    result = f"Error: Tool {tool_name} is not defined."
                
                # Логування результату (Спостереження), обрізаємо для консолі
                preview_result = result[:300].replace('\n', ' ') + ("..." if len(result) > 300 else "")
                print(f"📎 Result: {preview_result}")
                
                # Додаємо результат роботи інструменту назад в контекст
                # ВАЖЛИВО: Обов'язково передавати tool_call_id, щоб LLM зрозуміла, до якого запиту цей результат
                self.messages.append(ToolMessage(content=result, tool_call_id=tool_id, name=tool_name))
                
            iterations += 1
            
        # Якщо ми вийшли з циклу через ліміт ітерацій
        return "❌ Перервано: Досягнуто максимального ліміту ітерацій агента (захист від зациклення)."