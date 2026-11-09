
import csv
import json
from pathlib import Path
from time import perf_counter

from graphmind.retrieval.semantic_search import search_papers
from graphmind.retrieval.improved_search import improved_search


EVAL_FILE = Path("data/fixtures/retrieval_eval.json")
OUTPUT_FILE = Path("data/processed/retrieval_benchmark.csv")


def main():

    with EVAL_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    rows = []

    for item in questions:

        question = item["question"]

        print("\nBenchmarking:", question)

        # Original retrieval
        start = perf_counter()
        original = search_papers(question, top_k=5)
        original_time = perf_counter() - start

        # Improved retrieval
        improved = improved_search(
            question,
            top_k=5,
            unique_papers=True
        )

        rows.append({
            "question": question,
            "original_results": len(original),
            "improved_results": len(improved["results"]),
            "original_unique_papers": len({
                str(r["pmid"]) for r in original
            }),
            "improved_unique_papers": len({
                str(r["pmid"])
                for r in improved["results"]
            }),
            "original_time_seconds": round(
                original_time, 4
            ),
            "improved_time_seconds": improved[
                "search_time_seconds"
            ]
        })

        print(
            "Original unique papers:",
            rows[-1]["original_unique_papers"]
        )

        print(
            "Improved unique papers:",
            rows[-1]["improved_unique_papers"]
        )

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

    print("\nBenchmark completed!")
    print("Questions tested:", len(rows))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
