from graphmind.retrieval.graph_search import search_entity


def main():

    entity_name = input(
        "Enter biomedical entity name: "
    ).strip()

    if not entity_name:
        print("Please enter an entity name.")
        return

    results = search_entity(entity_name)

    if not results:
        print("No valid connected entities found.")
        return

    print(f"\nFound {len(results)} connections:\n")

    for result in results:

        print("Entity:", result["entity"])

        print(
            "Connected to:",
            result["related_entity"]
        )

        print(
            "Type:",
            result["entity_type"]
        )

        print(
            "Predicate:",
            result["predicate"]
        )

        print(
            "Supporting papers:",
            result["supporting_papers"]
        )

        print(
            "Weight:",
            result["weight"]
        )

        print("-" * 40)


if __name__ == "__main__":
    main()