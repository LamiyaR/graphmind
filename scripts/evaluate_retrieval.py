
import json
import csv
from pathlib import Path

from graphmind.retrieval.semantic_search import search_papers


EVAL_FILE = Path("data/fixtures/retrieval_eval.json")
CHUNKS_FILE = Path("data/processed/chunks.jsonl")
OUTPUT_FILE = Path("data/processed/retrieval_metrics.csv")

K = 5


def precision_at_k(retrieved, relevant, k=5):
    hits = sum(
        chunk_id in relevant
        for chunk_id in retrieved[:k]
    )
    return hits / k


def recall_at_k(retrieved, relevant, k=5):
    if not relevant:
        return 0.0

    hits = len(set(retrieved[:k]) & relevant)
    return hits / len(relevant)


def reciprocal_rank(retrieved, relevant, k=5):
    for rank, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def main():
    with EVAL_FILE.open(encoding="utf-8") as file:
        evaluations = json.load(file)

    with CHUNKS_FILE.open(encoding="utf-8") as file:
        valid_ids = {
            json.loads(line)["chunk_id"]
            for line in file
            if line.strip()
        }

    if not evaluations:
        raise ValueError("No evaluation questions found.")

    rows = []

    for index, item in enumerate(evaluations, start=1):
        question = item["question"]
        relevant_list = item["relevant_chunk_ids"]

        if not relevant_list:
            raise ValueError(
                f"Question {index} has no relevance judgments. "
                "Review the chunks before running evaluation."
            )

        relevant = set(relevant_list)

        unknown = relevant - valid_ids
        if unknown:
            raise ValueError(
                f"Unknown chunk IDs for question {index}: {unknown}"
            )

        print(f"\nEvaluating question {index}: {question}")

        results = search_papers(question, top_k=K)
        retrieved = [r["chunk_id"] for r in results]

        precision = precision_at_k(retrieved, relevant, K)
        recall = recall_at_k(retrieved, relevant, K)
        rr = reciprocal_rank(retrieved, relevant, K)

        rows.append({
            "question": question,
            "precision_at_5": precision,
            "recall_at_5": recall,
            "reciprocal_rank_at_5": rr,
            "retrieved_ids": "|".join(retrieved)
        })

        print("Retrieved:", retrieved)
        print("Precision@5:", round(precision, 4))
        print("Recall@5:", round(recall, 4))
        print("RR@5:", round(rr, 4))

    count = len(rows)

    mean_precision = sum(
        r["precision_at_5"] for r in rows
    ) / count

    mean_recall = sum(
        r["recall_at_5"] for r in rows
    ) / count

    mrr = sum(
        r["reciprocal_rank_at_5"] for r in rows
    ) / count

    print("\n===== FINAL EVALUATION =====")
    print("Questions evaluated:", count)
    print("Mean Precision@5:", round(mean_precision, 4))
    print("Mean Recall@5:", round(mean_recall, 4))
    print("MRR@5:", round(mrr, 4))

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Saved results to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
