from time import perf_counter

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

MODEL_NAME = "NeuML/pubmedbert-base-embeddings"
DB_PATH = "data/qdrant"
COLLECTION_NAME = "biomedical_chunks"


def improved_search(question, top_k=5, unique_papers=True):
    """
    Search biomedical chunks and optionally
    return only one chunk per paper.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty")

    print("Loading PubMedBERT...")
    model = SentenceTransformer(MODEL_NAME)

    start = perf_counter()

    # Convert question to a vector
    query_vector = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    client = QdrantClient(path=DB_PATH)

    try:
        # Retrieve extra chunks so we have enough
        # candidates after removing repeated papers.
        candidate_limit = max(top_k * 5, 38)

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=candidate_limit,
            with_payload=True
        ).points

        selected = []
        seen_pmids = set()

        for result in results:
            payload = result.payload or {}
            pmid = str(payload.get("pmid", ""))

            if unique_papers and pmid in seen_pmids:
                continue

            seen_pmids.add(pmid)

            selected.append({
                "chunk_id": payload.get("chunk_id"),
                "pmid": pmid,
                "title": payload.get("title"),
                "text": payload.get("text"),
                "score": float(result.score)
            })

            if len(selected) >= top_k:
                break

    finally:
        client.close()

    elapsed = perf_counter() - start

    return {
        "question": question,
        "results": selected,
        "search_time_seconds": round(elapsed, 4)
    }

