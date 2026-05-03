import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

# 1. ДОДАЄМО ІМПОРТ НАШОГО СУДДІ GEMINI
from tests.gemini_eval import gemini_judge

critique_quality = GEval(
    name="Critique Quality",
    evaluation_steps=[
        "Check that the critique identifies specific issues, not vague complaints",
        "Check that revision_requests are actionable (researcher can act on them)",
        "If verdict is APPROVE, gaps list should be empty or contain only minor items",
        "If verdict is REVISE, there must be at least one revision_request",
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    model=gemini_judge, 
    threshold=0.7,
)

def test_critique_approve():
    findings = "Here is a complete comparison of Multi-Agent Systems vs single LLMs with recent 2025 data and citations."
    actual_output = """
    {
      "verdict": "APPROVE",
      "is_fresh": true,
      "is_complete": true,
      "is_well_structured": true,
      "strengths": ["Clear structure", "Recent 2025 data used"],
      "gaps": [],
      "revision_requests": []
    }
    """
    test_case = LLMTestCase(input=findings, actual_output=actual_output)
    assert_test(test_case, [critique_quality])

def test_critique_revise():
    findings = "Multi-Agent systems are good. Single LLMs are bad."
    actual_output = """
    {
      "verdict": "REVISE",
      "is_fresh": false,
      "is_complete": false,
      "is_well_structured": false,
      "strengths": ["Identifies the core topic"],
      "gaps": ["No specific details", "Lacks comparative criteria", "No citations"],
      "revision_requests": ["Add 3 specific criteria for comparison", "Include recent examples from 2024-2025"]
    }
    """
    test_case = LLMTestCase(input=findings, actual_output=actual_output)
    assert_test(test_case, [critique_quality])