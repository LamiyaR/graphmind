import json

from graphmind.db.neo4j_client import connect_neo4j


def read_entities(file_path):
    """
    Read biomedical entities from a JSONL file.
    """

    entities = []

    with open(file_path, "r", encoding="utf-8") as file:

        for line in file:

            if line.strip():
                entity = json.loads(line)
                entities.append(entity)

    return entities


def load_entities(file_path):
    """
    Create Entity nodes and connect them to Paper nodes.
    """

    entities = read_entities(file_path)

    driver = connect_neo4j()

    try:
        with driver.session() as session:

            for entity in entities:

                identifier = str(entity.get("identifier") or "").strip()

                entity_type = str(entity["type"]).strip()
                entity_name = str(
                entity.get("normalized_name") or entity["text"]
                ).strip()

                if not entity_type or not entity_name:
                    print("Skipping invalid entity")
                    continue

                if identifier and identifier != "-":
                    entity_id = entity_type + ":" + identifier
                else:
                    normalized_name = " ".join(entity_name.lower().split())
                    entity_id = entity_type + ":text:" + normalized_name

                # Create Entity node
                session.run(
                """
                MERGE (e:Entity {id: $entity_id})
                ON CREATE SET
                    e.name = $name,
                    e.type = $type,
                    e.is_normalized = $is_normalized
                """,
                entity_id=entity_id,
                name=entity_name,
                type=entity_type,
                is_normalized=bool(identifier and identifier != "-")
            ).consume()
    

                # Connect Entity to existing Paper
                session.run(
                    """
                    MATCH (e:Entity {id: $entity_id})
                    MATCH (p:Paper {pmid: $pmid})
                    MERGE (e)-[:MENTIONED_IN]->(p)
                    """,
                    entity_id=entity_id,
                    pmid=str(entity["pmid"])
                ).consume()

        print(f"Processed {len(entities)} entity records")

    finally:
        driver.close()