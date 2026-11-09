
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "NeuML/pubmedbert-base-embeddings"

INPUT_FILE = Path("data/processed/chunks.jsonl")
OUTPUT_FILE = Path("data/processed/embeddings.jsonl")


def generate_embeddings():

    print("Loading biomedical embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Reading biomedical chunks...")

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    if not chunks:
        print("No chunks found. Nothing to embed.")
        return

    texts = [chunk["text"] for chunk in chunks]

    print(f"Found {len(texts)} chunks")
    print("Generating embeddings...")

    vectors = model.encode(
        texts,
        batch_size=8,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:

        for chunk, vector in zip(chunks, vectors):

            record = {
                "chunk_id": chunk["chunk_id"],
                "pmid": chunk["pmid"],
                "title": chunk["title"],
                "text": chunk["text"],
                "embedding": vector.tolist()
            }

            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    print("\nEmbedding generation completed!")
    print("Total embeddings:", len(vectors))
    print("Embedding dimensions:", vectors.shape[1])
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_embeddings()
