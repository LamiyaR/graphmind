
import json
from pathlib import Path

from graphmind.retrieval.semantic_search import search_papers


EVAL_FILE = Path("data/fixtures/retrieval_eval.json")


def precision_at_k(retrieved, relevant, k=5):
    relevant_set = set(relevant)
    top_k = retrieved[:k]

    hits = sum(
        chunk_id in relevant_set
        for chunk_id in top_k
    )

    return hits / k


def recall_at_k(retrieved, relevant, k=5):
    relevant_set = set(relevant)

    if not relevant_set:
        return 0.0

    hits = len(
        set(retrieved[:k]) & relevant_set
    )

    return hits / len(relevant_set)


def reciprocal_rank(retrieved, relevant, k=5):
    relevant_set = set(relevant)

    for rank, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant_set:
            return 1.0 / rank

    return 0.0


def main():
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        evaluations = json.load(file)

    precision_scores = []
    recall_scores = []
    reciprocal_ranks = []

    for evaluation in evaluations:
        question = evaluation["question"]
        relevant = evaluation["relevant_chunk_ids"]

        print("\nQuestion:", question)

        results = search_papers(
            question=question,
            top_k=5
        )

        retrieved = [
            result["chunk_id"]
            for result in results
        ]

        precision = precision_at_k(
            retrieved, relevant
        )

        recall = recall_at_k(
            retrieved, relevant
        )

        rr = reciprocal_rank(
            retrieved, relevant
        )

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_ranks.append(rr)

        print("Retrieved:", retrieved)
        print("Precision@5:", round(precision, 4))
        print("Recall@5:", round(recall, 4))
        print("Reciprocal Rank:", round(rr, 4))

    count = len(evaluations)

    if count == 0:
        print("No evaluation questions found.")
        return

    print("\nEvaluation Summary")
    print("Questions evaluated:", count)
    print(
        "Mean Precision@5:",
        round(sum(precision_scores) / count, 4)
    )
    print(
        "Mean Recall@5:",
        round(sum(recall_scores) / count, 4)
    )
    print(
        "MRR@5:",
        round(sum(reciprocal_ranks) / count, 4)
    )


if __name__ == "__main__":
    main()
