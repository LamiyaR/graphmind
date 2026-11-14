from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    question: str
    detected_entity: str | None
    graph_paths: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    answer: str
    evidence_sufficient: bool
    retry_count: int