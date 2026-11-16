
import csv
import json
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/entities_linked.jsonl"
)

REVIEW_FILE = Path(
    "data/processed/entity_linking_review.csv"
)

METRICS_FILE = Path(
    "data/processed/entity_linking_metrics.csv"
)


def load_entities():

    with INPUT_FILE.open(encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def generate_review():

    entities = load_entities()

    linked = [
        entity for entity in entities
        if entity.get("link_status") == "linked"
    ]

    rows = []

    for entity in linked:

        rows.append({
            "pmid": entity.get("pmid", ""),
            "entity_text": entity.get("text", ""),
            "entity_type": entity.get("type", ""),
            "linked_id": entity.get("linked_id", ""),
            "linked_name": entity.get("linked_name", ""),
            "link_method": entity.get("link_method", ""),
            "correct": "",
            "review_notes": ""
        })

    REVIEW_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "pmid",
        "entity_text",
        "entity_type",
        "linked_id",
        "linked_name",
        "link_method",
        "correct",
        "review_notes"
    ]

    with REVIEW_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n===== ENTITY LINKING REVIEW =====")
    print("Total mentions:", len(entities))
    print("Linked mentions:", len(linked))
    print("Unlinked mentions:", len(entities) - len(linked))
    print(
        "Coverage:",
        round(len(linked) / len(entities), 4)
        if entities else 0.0
    )
    print("Saved review file to:", REVIEW_FILE)


def calculate_metrics():

    entities = load_entities()

    linked = [
        entity for entity in entities
        if entity.get("link_status") == "linked"
    ]

    with REVIEW_FILE.open(
        encoding="utf-8",
        newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    if len(rows) != len(linked):
        raise ValueError(
            "Review row count does not match linked mentions."
        )

    reviewed = [
        row for row in rows
        if row["correct"] in ("0", "1")
    ]

    correct = sum(
        row["correct"] == "1"
        for row in reviewed
    )

    coverage = (
        len(linked) / len(entities)
        if entities else 0.0
    )

    precision = (
        correct / len(reviewed)
        if reviewed else None
    )

    print("\n===== ENTITY LINKING EVALUATION =====")
    print("Total mentions:", len(entities))
    print("Linked mentions:", len(linked))
    print("Coverage:", round(coverage, 4))
    print("Reviewed links:", len(reviewed))

    if precision is None:
        print("Linking precision: Not yet evaluated")
    else:
        print("Linking precision:", round(precision, 4))

    METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with METRICS_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "total_mentions",
                "linked_mentions",
                "coverage",
                "reviewed_links",
                "correct_links",
                "linking_precision"
            ]
        )

        writer.writeheader()

        writer.writerow({
            "total_mentions": len(entities),
            "linked_mentions": len(linked),
            "coverage": coverage,
            "reviewed_links": len(reviewed),
            "correct_links": correct,
            "linking_precision": (
                precision if precision is not None else ""
            )
        })

    print("Saved metrics to:", METRICS_FILE)


def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--score",
        action="store_true"
    )

    args = parser.parse_args()

    if args.score:
        calculate_metrics()
    else:
        generate_review()


if __name__ == "__main__":
    main()
