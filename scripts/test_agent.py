
from graphmind.agent.workflow import build_graph


def main():
    agent = build_graph()

    result = agent.invoke({
        "question": (
            "How does Type 2 Diabetes affect immune cells?"
        ),
        "evidence": [],
        "answer": "",
        "evidence_sufficient": False,
        "retry_count": 0
    })

    print("\nFinal result:")
    print("Question:", result["question"])
    print("Evidence:", result["evidence"])
    print("Answer:", result["answer"])


if __name__ == "__main__":
    main()
