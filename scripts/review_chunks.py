
import json
from pathlib import Path

CHUNKS_FILE = Path("data/processed/chunks.jsonl")


def main():
    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            chunk = json.loads(line)

            print("\n" + "=" * 60)
            print("Chunk ID:", chunk["chunk_id"])
            print("PMID:", chunk["pmid"])
            print("Title:", chunk["title"])
            print("Text:", chunk["text"])


if __name__ == "__main__":
    main()
