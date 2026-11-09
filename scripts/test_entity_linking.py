
from graphmind.ingest.entity_linking import link_entity


def main():
    examples = [
        {"text": "T2DM", "type": "Disease_disorder"},
        {"text": "Metformin", "type": "Medication"},
        {"text": "TCF7L2", "type": "Gene"},
        {"text": "unknown term", "type": "Other"}
    ]

    for entity in examples:
        result = link_entity(entity)

        print("Entity:", result["text"])
        print("Linked ID:", result["linked_id"])
        print("Status:", result["link_status"])
        print("-" * 30)


if __name__ == "__main__":
    main()
