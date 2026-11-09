
from langgraph.graph import StateGraph, START, END

from graphmind.agent.state import AgentState
from graphmind.agent.retrieval_node import retrieve_evidence


def grade_evidence(state: AgentState):
    print("Step 2: Checking evidence")

    evidence = state.get("evidence", [])

    sufficient = len(evidence) > 0

    return {
        "evidence_sufficient": sufficient
    }


def generate_answer_node(state: AgentState):
    print("Step 3: Generating answer")

    # Placeholder until we connect Srushti's LLM
    return {
        "answer": (
            "Retrieved evidence is available. "
            "LLM answer generation is not connected yet."
        )
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
