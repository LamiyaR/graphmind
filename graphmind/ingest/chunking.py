
import json
from pathlib import Path

INPUT_FILE = Path("data/raw/pubmed/papers.jsonl")
OUTPUT_FILE = Path("data/processed/chunks.jsonl")


def chunk_text(text, chunk_size=100, overlap=20):
    """
    Split text into overlapping word-based chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be between 0 and chunk_size"
        )

    words = text.split()

    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):

        chunk_words = words[start:start + chunk_size]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


def create_chunks():

    all_chunks = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            paper = json.loads(line)

            pmid = str(paper["pmid"])
            title = paper.get("title") or ""
            abstract = paper.get("abstract") or ""

            # Split the abstract into smaller chunks
            chunks = chunk_text(
                abstract,
                chunk_size=100,
                overlap=20
            )

            for index, chunk in enumerate(chunks):

                all_chunks.append({
                    "chunk_id": f"{pmid}_{index}",
                    "pmid": pmid,
                    "title": title,
                    "text": chunk,
                    "chunk_index": index
                })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:

        for chunk in all_chunks:

            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    print("Chunking completed!")
    print("Total chunks:", len(all_chunks))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    create_chunks()
