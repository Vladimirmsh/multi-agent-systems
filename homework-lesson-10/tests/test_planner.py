import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

# 1. ДОДАЄМО ІМПОРТ СУДДІ GEMINI
from tests.gemini_eval import gemini_judge

plan_quality = GEval(
    name="Plan Quality",
    evaluation_steps=[
        "Check that the plan contains specific search queries (not vague)",
        "Check that sources_to_check includes relevant sources for the topic",
        "Check that the output_format matches what the user asked for or is logical for a research report",
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    model=gemini_judge, 
    threshold=0.7,
)

def test_plan_quality():
    input_text = "Compare naive RAG vs sentence-window retrieval"
    
    actual_output = """
    {
      "goal": "Compare naive RAG and sentence-window retrieval approaches",
      "search_queries": ["naive RAG architecture", "sentence-window retrieval mechanism", "naive RAG vs sentence-window comparison"],
      "sources_to_check": ["knowledge_base", "web"],
      "output_format": "Comparative table with pros and cons"
    }
    """
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output
    )
    
    assert_test(test_case, [plan_quality])

def test_plan_has_queries_edge_case():
    input_text = "Asdfghjkl qwertyuiop"
    actual_output = """
    {
      "goal": "Clarify the user's intent as the input is nonsensical",
      "search_queries": [],
      "sources_to_check": [],
      "output_format": "Text response asking for clarification"
    }
    """
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output
    )
    assert_test(test_case, [plan_quality])