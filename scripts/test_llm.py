
from graphmind.retrieval.hybrid_search import hybrid_search
from graphmind.llm.answer_generator import generate_answer


def main():
    question = input("Enter biomedical question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    print("\nRetrieving evidence...")

    results = hybrid_search(
        question=question,
        top_k=5
    )

    evidence = results["evidence"]

    print("Evidence retrieved:", len(evidence))

    print("\nGenerating answer...")

    answer = generate_answer(
        question=question,
        evidence=evidence
    )

    print("\nGRAPHMIND ANSWER")
    print("-" * 50)
    print(answer)


if __name__ == "__main__":
    main()
