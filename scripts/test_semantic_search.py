
from graphmind.retrieval.semantic_search import search_papers


def main():

    question = (
        "How does Type 2 Diabetes affect immune cells?"
    )

    print("Question:", question)

    results = search_papers(
        question=question,
        top_k=5
    )

    print("\nTotal results:", len(results))

    for index, paper in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("PMID:", paper["pmid"])
        print("Title:", paper["title"])
        print("Similarity score:", round(paper["score"], 4))
        print("Chunk:", paper["text"][:250], "...")


if __name__ == "__main__":
    main()
