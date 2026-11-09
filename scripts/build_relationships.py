import argparse

from graphmind.ingest.relationship_loader import create_relationships


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pmid",
        default=None,
        help="Optional PMID for testing"
    )

    args = parser.parse_args()

    create_relationships(args.pmid)


if __name__ == "__main__":
    main()