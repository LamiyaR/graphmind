# Runs the download process

from graphmind.ingest.pubmed import download_papers


def main():

    query = (
        '("metformin" OR "type 2 diabetes" '
        'OR "diabetic nephropathy") AND hasabstract'
    )

    download_papers(
        query=query,
        max_results=10
    )


if __name__ == "__main__":
    main()