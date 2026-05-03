from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from schemas import ClassificationOutput, AgentResponse, EscalationOutput
from state import SupportState
import os
from tools import search_kb, duckduckgo_search, save_escalation_report, notify_slack

# Ініціалізація LLM (Gemini або інша модель)
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

# ВУЗЛИ (NODES)
def router_node(state: SupportState):
    """Router Agent: класифікує запит."""
    user_msg = state["messages"][-1].content
    structured_llm = llm.with_structured_output(ClassificationOutput)
    
    prompt = f"Проаналізуй запит клієнта та класифікуй його:\n\n{user_msg}"
    classification = structured_llm.invoke(prompt)
    
    return {"classification": classification.model_dump()}

def docs_agent_node(state: SupportState):
    """Docs Agent: шукає в KB."""
    user_msg = state["messages"][-1].content
    structured_llm = llm.with_structured_output(AgentResponse)
    
    # Виклик RAG-інструмента
    kb_info = search_kb(user_msg) 
    
    prompt = f"Ти агент підтримки продукту. Дай відповідь клієнту на базі цих даних KB:\n{kb_info}\n\nЗапит: {user_msg}"
    response = structured_llm.invoke(prompt)
    
    return {"agent_response": response.model_dump()}

def web_agent_node(state: SupportState):
    """Web Search Agent: шукає в інтернеті."""
    user_msg = state["messages"][-1].content
    structured_llm = llm.with_structured_output(AgentResponse)
    
    # Виклик DuckDuckGo
    web_info = duckduckgo_search(user_msg)
    
    prompt = f"Ти технічний агент. Дай відповідь клієнту використовуючи результати пошуку:\n{web_info}\n\nЗапит: {user_msg}"
    response = structured_llm.invoke(prompt)
    
    return {"agent_response": response.model_dump()}

def escalation_agent_node(state: SupportState):
    """Escalation Agent: ескалює на людину."""
    user_msg = state["messages"][0].content # Оригінальний запит
    classification = state.get("classification", {"category": "unknown"})
    agent_resp = state.get("agent_response", {"answer": "Не вдалося згенерувати автоматичну відповідь."})
    
    structured_llm = llm.with_structured_output(EscalationOutput)
    prompt = f"""Сформуй звіт для оператора. 
    Оригінальний запит: {user_msg}
    Категорія: {classification.get('category')}
    Спроба відповіді: {agent_resp.get('answer')}"""
    
    escalation_data = structured_llm.invoke(prompt)
    
    # Використання інструментів ескалації
    save_escalation_report(escalation_data.model_dump())
    notify_slack(escalation_data.summary)
    
    return {
        "escalation_report": escalation_data.model_dump(),
        "messages": [SystemMessage(content="Ваш запит передано живому оператору. Ми зв'яжемося з вами найближчим часом.")]
    }

# ЛОГІКА МАРШРУТИЗАЦІЇ (EDGES)
def route_request(state: SupportState):
    """Направляє запит до потрібного агента після Router'а."""
    category = state["classification"]["category"]
    urgency = state["classification"]["urgency"]
    
    if category == "critical" or urgency == "critical":
        return "escalation_agent"
    elif category == "product":
        return "docs_agent"
    else:
        return "web_agent"

def check_confidence(state: SupportState):
    """Fallback логіка: якщо агент не впевнений, переводимо на людину."""
    confidence = state["agent_response"].get("confidence", 0.0)
    if confidence < 0.75:
        return "escalation_agent"
    return END

# ПОБУДОВА ГРАФА
workflow = StateGraph(SupportState)

workflow.add_node("router", router_node)
workflow.add_node("docs_agent", docs_agent_node)
workflow.add_node("web_agent", web_agent_node)
workflow.add_node("escalation_agent", escalation_agent_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", route_request)
workflow.add_conditional_edges("docs_agent", check_confidence)
workflow.add_conditional_edges("web_agent", check_confidence)
workflow.add_edge("escalation_agent", END)

support_system = workflow.compile()