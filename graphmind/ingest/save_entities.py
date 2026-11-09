
import json
import time
from pathlib import Path

from graphmind.ingest.biomedical_ner import (
    load_ner_model,
    extract_with_ner
)

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
    ner_model = None

    # Process every paper

    for paper in papers:

        pmid = paper["pmid"]
        print(f"\nProcessing PMID: {pmid}")

        entities = []

        try:
            annotation_text = fetch_annotations(pmid)

            if annotation_text is not None:
                entities = extract_entities(annotation_text)

                for entity in entities:
                    entity["source"] = "pubtator3"

                print(
                    f"PubTator3 found {len(entities)} entities"
                )

        except Exception as error:
            print(f"PubTator3 error: {error}")

        # Use fallback if PubTator3 found nothing
        if not entities:

            print("Using biomedical NER fallback...")

            if ner_model is None:
                ner_model = load_ner_model()

            text = (
                paper.get("title", "") + " " +
                paper.get("abstract", "")
            ).strip()

            try:
                entities = extract_with_ner(
                    text=text,
                    pmid=pmid,
                    model=ner_model
                )

                print(
                    f"NER found {len(entities)} entities"
                )

            except Exception as error:
                print(f"NER error: {error}")

        if not entities:
            skipped += 1

        all_entities.extend(entities)

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
