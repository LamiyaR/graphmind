
import json
from pathlib import Path

from qdrant_client import QdrantClient, models


DB_PATH = "data/qdrant"
COLLECTION_NAME = "biomedical_chunks"
EMBEDDINGS_FILE = Path("data/processed/embeddings.jsonl")


def upload_embeddings():

    print("Connecting to Qdrant...")

    client = QdrantClient(path=DB_PATH)

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    if not records:
        print("No embeddings found.")
        return

    vector_size = len(records[0]["embedding"])

    # Create the collection if it does not exist
    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )

    points = []

    for index, record in enumerate(records):

        points.append(
            models.PointStruct(
                id=index + 1,
                vector=record["embedding"],
                payload={
                    "chunk_id": record["chunk_id"],
                    "pmid": record["pmid"],
                    "title": record["title"],
                    "text": record["text"]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    count = client.count(
        collection_name=COLLECTION_NAME,
        exact=True
    ).count

    print("Qdrant upload completed!")
    print("Total vectors stored:", count)
    print("Vector dimensions:", vector_size)

    client.close()


if __name__ == "__main__":
    upload_embeddings()
