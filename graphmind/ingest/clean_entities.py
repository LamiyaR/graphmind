
import json
from pathlib import Path

# Input file containing extracted biomedical entities
INPUT_FILE = Path("data/processed/entities.jsonl")

# Output file for cleaned entities
OUTPUT_FILE = Path("data/processed/entities_cleaned.jsonl")


def clean_entities():

    cleaned = []
    seen = set()
    total = 0

    # Step 1: Read the original entities
    with INPUT_FILE.open("r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            total += 1
            entity = json.loads(line)

            # Step 2: Remove empty entity names
            name = (entity.get("text") or "").strip()

            if not name:
                continue

            # Step 3: Normalize entity names
            normalized_name = " ".join(
                name.lower().split()
            )

            # Step 4: Identify duplicate annotations
            key = (
                str(entity.get("pmid")),
                normalized_name,
                entity.get("type"),
                entity.get("start"),
                entity.get("end")
            )

            if key in seen:
                continue

            seen.add(key)

            # Keep original text and add normalized name
            entity["normalized_name"] = normalized_name

            cleaned.append(entity)

    # Step 5: Create output folder if needed
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 6: Save cleaned entities
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:

        for entity in cleaned:

            file.write(
                json.dumps(entity, ensure_ascii=False) + "\n"
            )

    # Step 7: Display results
    print("Entity cleaning completed!")
    print("Original mentions:", total)
    print("Cleaned mentions:", len(cleaned))
    print("Removed:", total - len(cleaned))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    clean_entities()
