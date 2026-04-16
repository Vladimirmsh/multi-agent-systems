import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

# 1. ДОДАЄМО ІМПОРТ НАШОГО СУДДІ GEMINI
from tests.gemini_eval import gemini_judge

groundedness = GEval(
    name="Groundedness",
    evaluation_steps=[
        "Extract every factual claim from 'actual output'",
        "For each claim, check if it can be directly supported by 'retrieval context'",
        "Claims not present in retrieval context count as ungrounded, even if true",
        "Score = number of grounded claims / total claims",
    ],
    evaluation_params=[
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.RETRIEVAL_CONTEXT,
    ],
    model=gemini_judge,
    threshold=0.7,
)

def test_research_grounded():
    retrieval_context = [
        "Naive RAG splits documents into fixed-size chunks, which can cut off context.",
        "Sentence-window retrieval fetches a single sentence and adds surrounding sentences for context, improving generation quality."
    ]
    actual_output = "Naive RAG uses fixed-size chunks, whereas sentence-window retrieval provides better context by fetching a specific sentence along with its surrounding sentences."
    
    test_case = LLMTestCase(
        input="Compare naive RAG and sentence window retrieval",
        actual_output=actual_output,
        retrieval_context=retrieval_context
    )
    assert_test(test_case, [groundedness])

def test_research_edge_case_hallucination():
    retrieval_context = ["The capital of France is Paris."]
    # Модель додає факт, якого немає в контексті
    actual_output = "The capital of France is Paris, and its population is over 2 million."
    
    test_case = LLMTestCase(
        input="What is the capital of France and its population?",
        actual_output=actual_output,
        retrieval_context=retrieval_context
    )
    
    # Цей тест може впасти (fail), оскільки додано факт про населення, якого не було в retrieval_context
    assert_test(test_case, [groundedness])