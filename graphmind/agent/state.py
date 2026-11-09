
from typing import TypedDict


class AgentState(TypedDict):
    question: str
    evidence: list[dict]
    answer: str
    evidence_sufficient: bool
    retry_count: int
