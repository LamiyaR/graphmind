
from graphmind.retrieval.graph_evidence import retrieve_graph_evidence


def main():

    entity_name = input(
        "Enter biomedical entity name: "
    ).strip()

    if not entity_name:
        print("Please enter an entity name.")
        return

    results = retrieve_graph_evidence(
        entity_name=entity_name,
        max_hops=2,
        limit=20
    )

    paths = results["paths"]
    papers = results["papers"]

    print("\nGRAPH RETRIEVAL RESULTS")
    print("-" * 50)

    print("Entity:", entity_name)
    print("Paths found:", len(paths))
    print("Supporting papers found:", len(papers))

    print("\nGRAPH PATHS")
    print("-" * 50)

    for path in paths[:5]:

        print(
            "Path:",
            " -> ".join(path["path_nodes"])
        )

        print("Hops:", path["hops"])
        print("-" * 30)

    print("\nRESEARCH EVIDENCE")
    print("-" * 50)

    for paper in papers[:5]:

        print("PMID:", paper["pmid"])
        print("Title:", paper["title"])

        abstract = paper.get("abstract") or ""

        print("Abstract:", abstract[:500])

        print("-" * 50)


if __name__ == "__main__":
    main()
