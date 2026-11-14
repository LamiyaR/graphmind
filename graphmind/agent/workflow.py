
from langgraph.graph import StateGraph, START, END

from graphmind.agent.state import AgentState
from graphmind.agent.retrieval_node import retrieve_evidence
from graphmind.llm.answer_generator import generate_answer


def grade_evidence(state: AgentState):
    print("Step 2: Checking evidence")

    evidence = state.get("evidence", [])

    sufficient = len(evidence) > 0

    return {
        "evidence_sufficient": sufficient
    }


def generate_answer_node(state: AgentState):
    print("Step 3: Generating answer")
    if not state.get("evidence_sufficient", False):
        return {
            "answer": "Insufficient research evidence to answer the question."
        }

    answer = generate_answer(
    question=state["question"],
    evidence=state["evidence"]
    )
    return {
        "answer": answer
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_evidence)
    graph.add_node("grade", grade_evidence)
    graph.add_node("generate", generate_answer_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_edge("grade", "generate")
    graph.add_edge("generate", END)

    return graph.compile()
