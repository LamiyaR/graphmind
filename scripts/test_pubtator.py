
import json
from pathlib import Path

from graphmind.ingest.pubtator import (
    fetch_annotations,
    extract_entities
)

DATA_FILE = Path("data/raw/pubmed/papers.jsonl")


def main():

    with DATA_FILE.open("r", encoding="utf-8") as file:
        first_paper = json.loads(next(file))

    pmid = first_paper["pmid"]

    print("Testing PubTator3...")
    print("Paper PMID:", pmid)

    annotation_text = fetch_annotations(pmid)

    if annotation_text is None:
        print("Skipping this paper.")
        return

    entities = extract_entities(annotation_text)

    print("Entities found:", len(entities))

    for entity in entities[:10]:
        print(entity["text"], "->", entity["type"])


if __name__ == "__main__":
    main()
