import argparse

from graphmind.ingest.entity_loader import load_entities


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        default="data/processed/entities.jsonl",
        help="Path to the entity JSONL file"
    )

    args = parser.parse_args()

    load_entities(args.file)


if __name__ == "__main__":
    main()