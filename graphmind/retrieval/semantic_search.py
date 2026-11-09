
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

MODEL_NAME = "NeuML/pubmedbert-base-embeddings"
DB_PATH = "data/qdrant"
COLLECTION_NAME = "biomedical_chunks"


def search_papers(question, top_k=5):

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Converting question into embedding...")

    question_vector = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    print("Searching Qdrant...")

    client = QdrantClient(path=DB_PATH)

    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=question_vector,
            limit=top_k,
            with_payload=True
        ).points

        papers = []

        for result in results:
            payload = result.payload or {}

            papers.append({
                "score": result.score,
                "pmid": payload.get("pmid"),
                "title": payload.get("title"),
                "text": payload.get("text"),
                "chunk_id": payload.get("chunk_id")
            })

        return papers

    finally:
        client.close()
