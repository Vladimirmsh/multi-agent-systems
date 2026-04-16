import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric

# 1. ДОДАЄМО ІМПОРТ НАШОГО СУДДІ GEMINI
from tests.gemini_eval import gemini_judge

tool_metric = ToolCorrectnessMetric(threshold=0.5, model=gemini_judge)

def test_planner_tools():
    # Симулюємо ситуацію: Planner має викликати інструмент для пошуку
    tools_called = [
        ToolCall(name="web_search", arguments={"query": "RAG approaches 2025"})
    ]
    test_case = LLMTestCase(
        input="Draft a research plan for comparing modern RAG approaches.",
        actual_output="I have initiated a search to build the plan.",
        tools_called=tools_called
    )
    assert_test(test_case, [tool_metric])

def test_supervisor_save():
    # Симулюємо ситуацію: Supervisor отримує APPROVE і має викликати save_report
    tools_called = [
        ToolCall(name="save_report", arguments={"filename": "report.md", "content": "# Report"})
    ]
    test_case = LLMTestCase(
        input="The critique verdict is APPROVE. The research is done.",
        actual_output="I will now save the report.",
        tools_called=tools_called
    )
    assert_test(test_case, [tool_metric])

def test_researcher_tools():
    # Симулюємо ситуацію: Researcher читає конкретний URL
    tools_called = [
        ToolCall(name="read_url", arguments={"url": "https://langchain.com/docs"})
    ]
    test_case = LLMTestCase(
        input="Research LangChain capabilities using their official website.",
        actual_output="Fetching data from LangChain docs.",
        tools_called=tools_called
    )
    assert_test(test_case, [tool_metric])