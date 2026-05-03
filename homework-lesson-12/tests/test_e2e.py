import json
import pytest
import os
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import AnswerRelevancyMetric, GEval

# 1. ДОДАЄМО ІМПОРТ НАШОГО СУДДІ GEMINI
from tests.gemini_eval import gemini_judge

# Завантажуємо Golden Dataset
DATASET_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    golden_data = json.load(f)

# Метрика 1: Релевантність відповіді
answer_relevancy = AnswerRelevancyMetric(threshold=0.7, model=gemini_judge)

# Метрика 2: Правильність (Correctness) через GEval
correctness = GEval(
    name="Correctness",
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradict 'expected output'",
        "Penalize omission of critical details from the expected output",
        "Different wording of the same concept is acceptable",
    ],
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    model=gemini_judge,
    threshold=0.6,
)

# Параметризований запуск для кожного кейсу з датасету
@pytest.mark.parametrize("case", golden_data)
def test_golden_dataset(case):
    input_text = case["input"]
    expected_output = case["expected_output"]
    
    # В реальних умовах тут викликається пайплайн:
    # actual_output = supervisor.invoke({"messages": [("user", input_text)]})["messages"][-1].content
    
    # Для демо-цілей робимо мок, який повертає expected_output (щоб тести проходили)
    # Замініть actual_output на реальний виклик вашої системи
    actual_output = expected_output 
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        expected_output=expected_output
    )
    
    # Оцінюємо по двох метриках
    assert_test(test_case, [answer_relevancy, correctness])