from graphmind.db.neo4j_client import connect_neo4j


def create_relationships(pmid=None):
    """
    Connect biomedical entities that appear
    in the same research paper.
    """

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            query = """
            MATCH (e1:Entity)-[:MENTIONED_IN]->(p:Paper)
                  <-[:MENTIONED_IN]-(e2:Entity)

            WHERE e1.id < e2.id
              AND ($pmid IS NULL OR p.pmid = $pmid)

            WITH e1, e2, collect(DISTINCT p.pmid) AS pmids

            MERGE (e1)-[r:RELATED_TO {
                predicate: 'co_occurs'
            }]->(e2)

            SET r.pmids =
                reduce(
                    all_pmids = coalesce(r.pmids, []),
                    paper_id IN pmids |
                    CASE
                        WHEN paper_id IN all_pmids
                        THEN all_pmids
                        ELSE all_pmids + paper_id
                    END
                ),
                r.weight = size(r.pmids),
                r.source = 'cooccurrence'

            RETURN count(r) AS relationships_processed
            """

            result = session.run(query, pmid=pmid)

            record = result.single()

            count = record["relationships_processed"]

            print(f"Processed {count} entity relationships")

    finally:
        driver.close()