from graphmind.db.neo4j_client import connect_neo4j


def is_valid_entity(name):
    """
    Filter obvious invalid biomedical entity names.
    """

    if not name:
        return False

    name = str(name).strip()

    if len(name) < 2:
        return False

    if "##" in name:
        return False

    if not any(char.isalpha() for char in name):
        return False

    return True


def search_entity(entity_name, limit=20):
    """
    Find biomedical entities connected to a given entity.
    """

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            query = """
            MATCH (e:Entity)-[r:RELATED_TO]-(related:Entity)

            WHERE toLower(e.name) = toLower($entity_name)
              AND r.predicate = 'co_occurs'

            RETURN
                e.name AS entity,
                related.name AS related_entity,
                related.type AS entity_type,
                r.predicate AS predicate,
                r.pmids AS supporting_papers,
                coalesce(
                    r.weight,
                    size(coalesce(r.pmids, []))
                ) AS weight

            ORDER BY weight DESC
            LIMIT $candidate_limit
            """

            result = session.run(
                query,
                entity_name=entity_name,
                candidate_limit=max(limit * 10, 100)
            )

            records = [record.data() for record in result]

            valid_records = [
                record
                for record in records
                if is_valid_entity(record["related_entity"])
            ]

            return valid_records[:limit]

    finally:
        driver.close()