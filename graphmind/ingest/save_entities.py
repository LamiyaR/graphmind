
import json
import time
from pathlib import Path

from graphmind.ingest.pubtator import (
    fetch_annotations,
    extract_entities
)

INPUT_FILE = Path("data/raw/pubmed/papers.jsonl")
OUTPUT_FILE = Path("data/processed/entities.jsonl")


def save_entities():

    # Read the PubMed papers
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        papers = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    print(f"Found {len(papers)} papers")

    all_entities = []
    skipped = 0

    # Process every paper
    for paper in papers:

        #pmid = paper["pmid"]
        
        pmid = paper["pmid"]
        
        print(f"Processing PMID: {pmid}")
    
        
    
        try:
            annotation_text = fetch_annotations(pmid)

            if annotation_text is None:
                skipped += 1
                print("Skipped: annotations unavailable")
                continue

            entities = extract_entities(annotation_text)
            all_entities.extend(entities)

            print(f"Found {len(entities)} entities")

        except Exception as error:
            skipped += 1
            print(f"Error processing {pmid}: {error}")

        time.sleep(0.4)

    # Create output folder if needed
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

# Save only when entities were successfully extracted
    if not all_entities:
        print("No entities extracted.")
        print("Existing output will not be overwritten.")
        return

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for entity in all_entities:
            file.write(
                json.dumps(entity, ensure_ascii=False) + "\n"
            )

    print("\nExtraction complete!")
    print(f"Total entity mentions: {len(all_entities)}")
    print(f"Papers skipped: {skipped}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    save_entities()
