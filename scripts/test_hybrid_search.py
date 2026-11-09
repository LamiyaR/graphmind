
from graphmind.retrieval.hybrid_search import hybrid_search


def main():

    question = input(
        "Enter biomedical question: "
    ).strip()

    if not question:
        print("Please enter a question.")
        return

    results = hybrid_search(
        question=question,
        top_k=5
    )

    print("\nHYBRID SEARCH RESULTS")
    print("-" * 50)

    print("Detected entity:", results["detected_entity"])
    print("Graph paths:", len(results["graph_paths"]))
    print("Evidence results:", len(results["evidence"]))

    for index, paper in enumerate(
        results["evidence"], start=1
    ):

        print(f"\nResult {index}")

        print("PMID:", paper["pmid"])
        print("Title:", paper["title"])
        print("Vector score:", paper["vector_score"])
        print("Graph match:", paper["graph_match"])
        print("Hybrid score:", round(paper["hybrid_score"], 4))

        if paper["chunks"]:
            print(
                "Text chunk:",
                str(paper["chunks"][0]["text"])[:250]
            )

        elif paper["abstract"]:
            print(
                "Abstract:",
                paper["abstract"][:250]
            )

        print("-" * 50)


if __name__ == "__main__":
    main()
