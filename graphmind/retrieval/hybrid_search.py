
import re

from graphmind.db.neo4j_client import connect_neo4j
from graphmind.retrieval.graph_evidence import retrieve_graph_evidence
from graphmind.retrieval.semantic_search import search_papers


def find_entity_in_question(question):
    """
    Find a known biomedical entity mentioned in the question.
    """

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            result = session.run(
                """
                MATCH (e:Entity)
                WHERE e.name IS NOT NULL
                RETURN DISTINCT e.name AS name
                """
            )

            names = [
                record["name"]
                for record in result
            ]

    finally:
        driver.close()

    # Prefer longer entity names
    names.sort(key=len, reverse=True)

    for name in names:

        name = name.strip()

        if len(name) < 3 or "##" in name:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(name)
            + r"(?!\w)"
        )

        if re.search(pattern, question, re.IGNORECASE):
            return name

    return None


def hybrid_search(question, top_k=5):
    """
    Combine graph evidence and vector search results.
    """

    # Step 1: Find biomedical entity in the question
    entity_name = find_entity_in_question(question)

    print("Detected entity:", entity_name)

    # Step 2: Search Qdrant
    vector_results = search_papers(
        question,
        top_k=top_k
    )

    # Step 3: Search Neo4j
    graph_results = {
        "paths": [],
        "papers": []
    }

    if entity_name:
        graph_results = retrieve_graph_evidence(
            entity_name=entity_name,
            max_hops=2,
            limit=20
        )

    # Step 4: Combine evidence by PMID
    combined = {}

    for result in vector_results:

        pmid = str(result.get("pmid") or "")

        if not pmid:
            continue

        if pmid not in combined:
            combined[pmid] = {
                "pmid": pmid,
                "title": result.get("title"),
                "vector_score": 0.0,
                "graph_match": False,
                "chunks": [],
                "abstract": None
            }

        combined[pmid]["vector_score"] = max(
            combined[pmid]["vector_score"],
            float(result.get("score") or 0)
        )

        combined[pmid]["chunks"].append({
            "chunk_id": result.get("chunk_id"),
            "text": result.get("text")
        })

    for paper in graph_results["papers"]:

        pmid = str(paper.get("pmid") or "")

        if not pmid:
            continue

        if pmid not in combined:
            combined[pmid] = {
                "pmid": pmid,
                "title": paper.get("title"),
                "vector_score": 0.0,
                "graph_match": False,
                "chunks": [],
                "abstract": None
            }

        combined[pmid]["graph_match"] = True
        combined[pmid]["abstract"] = paper.get("abstract")

        if not combined[pmid]["title"]:
            combined[pmid]["title"] = paper.get("title")

    # Step 5: Simple ranking
    for paper in combined.values():

        paper["hybrid_score"] = (
            paper["vector_score"]
            + (0.1 if paper["graph_match"] else 0.0)
        )

    ranked = sorted(
        combined.values(),
        key=lambda paper: paper["hybrid_score"],
        reverse=True
    )

    return {
        "question": question,
        "detected_entity": entity_name,
        "graph_paths": graph_results["paths"],
        "evidence": ranked[:top_k]
    }
