from graphmind.db.neo4j_client import connect_neo4j


def fix_weights():

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            query = """
            MATCH ()-[r:RELATED_TO]->()

            WHERE r.predicate = 'co_occurs'

            SET r.weight = size(
                coalesce(r.pmids, [])
            )

            RETURN count(r) AS updated
            """

            result = session.run(query)

            record = result.single()

            print(
                "Relationships updated:",
                record["updated"]
            )

    finally:
        driver.close()


if __name__ == "__main__":
    fix_weights()