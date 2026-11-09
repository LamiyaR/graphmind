
from graphmind.db.neo4j_client import connect_neo4j
from graphmind.retrieval.multi_hop import search_multi_hop


def get_papers_by_pmids(pmids):
    """
    Retrieve paper titles and abstracts from Neo4j.
    """

    if not pmids:
        return []

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            query = """
            MATCH (p:Paper)
            WHERE p.pmid IN $pmids

            RETURN
                p.pmid AS pmid,
                p.title AS title,
                p.abstract AS abstract

            ORDER BY p.pmid
            """

            result = session.run(
                query,
                pmids=list(set(pmids))
            )

            return [record.data() for record in result]

    finally:
        driver.close()


def retrieve_graph_evidence(entity_name, max_hops=2, limit=20):
    """
    Retrieve graph paths and their supporting papers.
    """

    # Step 1: Find connected entities
    paths = search_multi_hop(
        entity_name=entity_name,
        max_hops=max_hops,
        limit=limit
    )

    if not paths:
        return {
            "entity": entity_name,
            "paths": [],
            "papers": []
        }

    # Step 2: Collect supporting PMIDs
    pmids = set()

    for path in paths:

        for relationship in path["relationships"]:

            for pmid in relationship.get("pmids") or []:
                pmids.add(str(pmid))

    # Step 3: Retrieve the actual papers
    papers = get_papers_by_pmids(list(pmids))

    # Step 4: Return graph paths and evidence
    return {
        "entity": entity_name,
        "paths": paths,
        "papers": papers
    }
