
from langgraph.graph import StateGraph, START, END

from graphmind.agent.state import AgentState


def retrieve_evidence(state: AgentState):
    print("Step 1: Retrieving biomedical evidence")

    # Temporary example evidence.
    # We'll connect actual hybrid retrieval later.
    evidence = [
        {
            "pmid": "42999994",
            "text": (
                "Type 2 diabetes is associated with "
                "changes in natural killer cell function."
            )
        }
    ]

    return {"evidence": evidence}


def grade_evidence(state: AgentState):
    print("Step 2: Checking evidence")

    sufficient = len(state["evidence"]) > 0

    return {"evidence_sufficient": sufficient}


def generate_answer_node(state: AgentState):
    print("Step 3: Generating answer")

    # Placeholder until Srushti's LLM is ready.
    answer = (
        "Retrieved evidence is available. "
        "LLM answer generation is not connected yet."
    )

    return {"answer": answer}


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
