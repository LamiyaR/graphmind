
from graphmind.retrieval.hybrid_search import hybrid_search


def retrieve_evidence(state):
    """
    Retrieve biomedical evidence using Srushti's
    existing hybrid Neo4j + Qdrant search.
    """

    print("Step 1: Retrieving real biomedical evidence...")

    question = state["question"]

    results = hybrid_search(
        question=question,
        top_k=5
    )

    evidence = results.get("evidence", [])

    print("Evidence retrieved:", len(evidence))

    return {
        "evidence": evidence
    }
