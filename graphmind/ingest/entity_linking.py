
import json
from pathlib import Path

INPUT_FILE = Path("data/processed/entities_cleaned.jsonl")
OUTPUT_FILE = Path("data/processed/entities_linked.jsonl")

# Small curated dictionary for our first test
CONCEPTS = {
    "type 2 diabetes": {
        "id": "MESH:D003924",
        "name": "Diabetes Mellitus, Type 2",
        "category": "Disease",
        "synonyms": [
            "type 2 diabetes mellitus",
            "t2dm",
            "type ii diabetes"
        ]
    },
    "metformin": {
        "id": "MESH:D008687",
        "name": "Metformin",
        "category": "Chemical",
        "synonyms": []
    },
    "tcf7l2": {
        "id": "NCBIGene:6934",
        "name": "TCF7L2",
        "category": "Gene",
        "synonyms": []
    }
}


def normalize(text):
    return " ".join(text.casefold().split())


def create_lookup():
    lookup = {}

    for name, concept in CONCEPTS.items():
        all_names = [name] + concept["synonyms"]

        for synonym in all_names:
            lookup[normalize(synonym)] = concept

    return lookup


LOOKUP = create_lookup()


def link_entity(entity):
    result = entity.copy()

    name = normalize(
        result.get("normalized_name")
        or result.get("text")
        or ""
    )

    result["linked_id"] = None
    result["linked_name"] = None
    result["link_status"] = "unlinked"
    result["link_method"] = None

    concept = LOOKUP.get(name)

    if concept is None:
        return result

    result["linked_id"] = concept["id"]
    result["linked_name"] = concept["name"]
    result["link_status"] = "linked"
    result["link_method"] = "curated_exact_match"

    return result


def link_all_entities():
    if not INPUT_FILE.exists():
        print("Input file missing:", INPUT_FILE)
        return

    linked = []
    linked_count = 0

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            entity = json.loads(line)
            result = link_entity(entity)

            linked.append(result)

            if result["link_status"] == "linked":
                linked_count += 1

    if not linked:
        print("No entities found. Output not overwritten.")
        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for entity in linked:
            file.write(
                json.dumps(entity, ensure_ascii=False) + "\n"
            )

    print("Entity linking completed!")
    print("Total mentions:", len(linked))
    print("Linked mentions:", linked_count)
    print("Unlinked mentions:", len(linked) - linked_count)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    link_all_entities()
