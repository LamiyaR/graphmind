import json
from pathlib import Path

from graphmind.db.neo4j_client import connect_neo4j


PAPERS_FILE = Path("data/raw/pubmed/papers.jsonl")


def read_papers():

    papers = []

    with open(PAPERS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            if line.strip():

                paper = json.loads(line)

                papers.append(paper)

    return papers


def load_papers():

    papers = read_papers()

    driver = connect_neo4j()

    try:

        with driver.session() as session:

            for paper in papers:

                session.run(
                    """
                    MERGE (p:Paper {pmid: $pmid})
                    SET p.title = $title,
                        p.abstract = $abstract
                    """,
                    pmid=str(paper["pmid"]),
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", "")
                ).consume()

        print(f"Processed {len(papers)} papers in Neo4j")

    finally:

        driver.close()