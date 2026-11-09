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

                # Skip entities without a valid identifier
                identifier = str(entity.get("identifier") or "").strip()

                if not identifier or identifier == "-":
                    print("Skipping entity without identifier")
                    continue

                # Create a unique entity ID
                entity_id = (
                    entity["type"] + ":" + identifier
                )

                # Create Entity node
                session.run(
                    """
                    MERGE (e:Entity {id: $entity_id})
                    ON CREATE SET
                        e.name = $name,
                        e.type = $type
                    """,
                    entity_id=entity_id,
                    name=entity["text"],
                    type=entity["type"]
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