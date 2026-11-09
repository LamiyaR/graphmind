from graphmind.retrieval.multi_hop import search_multi_hop


def main():

    entity_name = input(
        "Enter biomedical entity name: "
    ).strip()

    if not entity_name:
        print("Please enter an entity name.")
        return

    results = search_multi_hop(
        entity_name=entity_name,
        max_hops=2,
        limit=20
    )

    if not results:
        print("No multi-hop connections found.")
        return

    print(f"\nFound {len(results)} paths:\n")

    for result in results:

        print("Source:", result["source"])
        print("Target:", result["target"])
        print("Target type:", result["target_type"])
        print("Number of hops:", result["hops"])

        print(
            "Path:",
            " -> ".join(result["path_nodes"])
        )

        for relationship in result["relationships"]:
            print(
                "Predicate:",
                relationship["predicate"]
            )

            print(
                "Supporting papers:",
                relationship["pmids"]
            )

            print(
                "Weight:",
                relationship["weight"]
            )

        print("-" * 50)


if __name__ == "__main__":
    main()