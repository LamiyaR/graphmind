
from graphmind.retrieval.improved_search import improved_search


def main():

    question = (
        "How does Type 2 Diabetes affect immune cells?"
    )

    output = improved_search(
        question=question,
        top_k=5,
        unique_papers=True
    )

    print("\nQuestion:", output["question"])
    print("Results:", len(output["results"]))
    print(
        "Search time:",
        output["search_time_seconds"],
        "seconds"
    )

    for index, result in enumerate(
        output["results"], start=1
    ):
        print(f"\nResult {index}")
        print("PMID:", result["pmid"])
        print("Title:", result["title"])
        print("Score:", round(result["score"], 4))
        print("Chunk:", result["text"][:200], "...")


if __name__ == "__main__":
    main()
