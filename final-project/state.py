from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    classification: dict  # Зберігатимемо ClassificationOutput
    agent_response: dict  # Зберігатимемо AgentResponse
    escalation_report: dict # Зберігатимемо EscalationOutput