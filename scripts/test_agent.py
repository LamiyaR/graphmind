
from graphmind.agent.workflow import build_graph


def main():
    agent = build_graph()

    question = input("Enter biomedical question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    result = agent.invoke({
        "question": question,
        "evidence": [],
        "answer": "",
        "evidence_sufficient": False,
        "retry_count": 0
    })

    print("\nGRAPHMIND FINAL RESULT")
    print("-" * 50)

    print("Question:", result["question"])
    print("Evidence retrieved:", len(result.get("evidence", [])))
    print("\nAnswer:")
    print(result.get("answer", "No answer generated"))


if __name__ == "__main__":
    main()
