
from graphmind.ingest.biomedical_ner import (
    load_ner_model,
    extract_with_ner
)


def main():
    text = (
        "Metformin is used to treat type 2 diabetes. "
        "The TCF7L2 gene is associated with diabetes risk."
    )

    model = load_ner_model()

    entities = extract_with_ner(
        text=text,
        pmid="TEST001",
        model=model
    )

    print("\nEntities found:", len(entities))

    for entity in entities:
        print(
            entity["text"],
            "->",
            entity["type"]
        )


if __name__ == "__main__":
    main()
