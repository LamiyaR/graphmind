
import csv
import json
from collections import Counter
from pathlib import Path

from graphmind.retrieval.semantic_search import search_papers
from graphmind.retrieval.hybrid_search import find_entity_in_question
from graphmind.retrieval.graph_evidence import retrieve_graph_evidence


EVAL_FILE = Path("data/fixtures/retrieval_eval.json")
CHUNKS_FILE = Path("data/processed/chunks.jsonl")
OUTPUT_FILE = Path("data/processed/retrieval_methods_benchmark.csv")

K = 5
GRAPH_BONUS = 0.1


def unique_pmids(results):
    """Preserve ranking while removing duplicate PMIDs."""
    seen = set()
    pmids = []

    for result in results:
        pmid = str(result.get("pmid") or "").strip()

        if pmid and pmid not in seen:
            seen.add(pmid)
            pmids.append(pmid)

    return pmids


def evaluate(retrieved, relevant):
    """Calculate paper-level Precision, Recall and RR."""

    retrieved = retrieved[:K]

    hits = len(set(retrieved) & relevant)

    precision = hits / K
    recall = hits / len(relevant) if relevant else 0.0

    rr = 0.0
    for rank, pmid in enumerate(retrieved, start=1):
        if pmid in relevant:
            rr = 1.0 / rank
            break

    return precision, recall, rr


def rank_graph_papers(graph_results):
    """
    Rank graph papers by the number of retrieved
    relationships supported by each PMID.

    This is a benchmark-specific ranking heuristic.
    """

    counts = Counter()

    for path in graph_results.get("paths", []):
        for relationship in path.get("relationships", []):
            for pmid in relationship.get("pmids") or []:
                counts[str(pmid)] += 1

    papers = graph_results.get("papers", [])

    return sorted(
        papers,
        key=lambda paper: (
            -counts[str(paper.get("pmid"))],
            str(paper.get("pmid"))
        )
    )


def main():

    with EVAL_FILE.open(encoding="utf-8") as f:
        evaluations = json.load(f)

    with CHUNKS_FILE.open(encoding="utf-8") as f:
        chunks = [
            json.loads(line)
            for line in f
            if line.strip()
        ]

    chunk_to_pmid = {
        str(chunk["chunk_id"]): str(chunk["pmid"])
        for chunk in chunks
    }

    rows = []

    for index, item in enumerate(evaluations, start=1):

        question = item["question"]

        relevant_chunks = item["relevant_chunk_ids"]

        if not relevant_chunks:
            raise ValueError(
                f"Question {index} has no relevance labels."
            )

        unknown = set(relevant_chunks) - set(chunk_to_pmid)

        if unknown:
            raise ValueError(
                f"Unknown chunk IDs: {sorted(unknown)}"
            )

        relevant_pmids = {
            chunk_to_pmid[chunk_id]
            for chunk_id in relevant_chunks
        }

        print("\n" + "=" * 65)
        print(f"QUESTION {index}: {question}")
        print("=" * 65)

        # ----------------------------------
        # 1. VECTOR-ONLY RETRIEVAL
        # ----------------------------------

        # Retrieve all indexed chunks so we can
        # produce a unique-paper ranking.
        vector_chunks = search_papers(
            question,
            top_k=len(chunks)
        )

        vector_pmids = unique_pmids(vector_chunks)

        vector_scores = {}

        for chunk in vector_chunks:
            pmid = str(chunk.get("pmid") or "").strip()

            if not pmid:
                continue

            score = float(chunk.get("score") or 0.0)

            vector_scores[pmid] = max(
                vector_scores.get(pmid, float("-inf")),
                score
            )

        # ----------------------------------
        # 2. GRAPH-ONLY RETRIEVAL
        # ----------------------------------

        entity = find_entity_in_question(question)

        graph_results = {
            "paths": [],
            "papers": []
        }

        if entity:
            graph_results = retrieve_graph_evidence(
                entity_name=entity,
                max_hops=2,
                limit=20
            )

        ranked_graph = rank_graph_papers(graph_results)
        graph_pmids = unique_pmids(ranked_graph)

        graph_set = set(graph_pmids)

        # ----------------------------------
        # 3. HYBRID RETRIEVAL
        # ----------------------------------

        # Same score formula as production:
        # vector_score + 0.1 for graph matches.
        # Here we use the full candidate pool.
        candidate_pmids = set(vector_scores) | graph_set

        hybrid_scores = {
            pmid: (
                vector_scores.get(pmid, 0.0)
                + (GRAPH_BONUS if pmid in graph_set else 0.0)
            )
            for pmid in candidate_pmids
        }

        hybrid_pmids = sorted(
            candidate_pmids,
            key=lambda pmid: (
                -hybrid_scores[pmid],
                pmid
            )
        )

        # ----------------------------------
        # EVALUATE ALL THREE
        # ----------------------------------

        methods = {
            "vector": vector_pmids,
            "graph": graph_pmids,
            "hybrid": hybrid_pmids
        }

        for method, pmids in methods.items():

            precision, recall, rr = evaluate(
                pmids,
                relevant_pmids
            )

            rows.append({
                "question": question,
                "method": method,
                "precision_at_5": round(precision, 4),
                "recall_at_5": round(recall, 4),
                "rr_at_5": round(rr, 4),
                "returned_papers": len(pmids[:K]),
                "retrieved_pmids": "|".join(pmids[:K])
            })

            print(f"\nMethod: {method.upper()}")
            print("PMIDs:", pmids[:K])
            print("Precision@5:", round(precision, 4))
            print("Recall@5:", round(recall, 4))
            print("RR@5:", round(rr, 4))

    # ----------------------------------
    # SAVE RESULTS
    # ----------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    # ----------------------------------
    # PRINT SUMMARY
    # ----------------------------------

    print("\n" + "=" * 65)
    print("FINAL RETRIEVAL COMPARISON")
    print("=" * 65)

    for method in ("vector", "graph", "hybrid"):

        method_rows = [
            row for row in rows
            if row["method"] == method
        ]

        count = len(method_rows)

        print(f"\n{method.upper()}")

        for metric in (
            "precision_at_5",
            "recall_at_5",
            "rr_at_5"
        ):

            average = sum(
                row[metric] for row in method_rows
            ) / count

            print(f"{metric}: {average:.4f}")

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
