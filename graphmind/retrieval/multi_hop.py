from graphmind.db.neo4j_client import connect_neo4j


def search_multi_hop(entity_name, max_hops=2, limit=20):

    if max_hops not in (1, 2):
        raise ValueError("max_hops must be 1 or 2")

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            query = f"""
            MATCH (start:Entity)
            WHERE toLower(start.name) = toLower($entity_name)

            MATCH path =
                (start)-[:RELATED_TO*1..{max_hops}]-(target:Entity)

            WHERE start <> target

              AND ALL(
                  r IN relationships(path)
                  WHERE r.predicate = 'co_occurs'
              )

              AND ALL(
                  n IN nodes(path)
                  WHERE single(x IN nodes(path) WHERE x = n)
              )

              AND ALL(
                  n IN nodes(path)
                  WHERE n.name IS NOT NULL
                    AND size(trim(n.name)) >= 2
                    AND NOT n.name CONTAINS '##'
                    AND n.name =~ '.*[a-zA-Z].*'
              )

            WITH start, target, path,
                 length(path) AS hops

            RETURN
                start.name AS source,
                target.name AS target,
                target.type AS target_type,
                hops,

                [n IN nodes(path) | n.name] AS path_nodes,

                [r IN relationships(path) |
                    {{
                        predicate: r.predicate,
                        pmids: r.pmids,
                        weight: coalesce(
                            r.weight,
                            size(coalesce(r.pmids, []))
                        )
                    }}
                ] AS relationships

            ORDER BY hops DESC, target ASC
            LIMIT $limit
            """

            result = session.run(
                query,
                entity_name=entity_name,
                limit=limit
            )

            return [record.data() for record in result]

    finally:
        driver.close()