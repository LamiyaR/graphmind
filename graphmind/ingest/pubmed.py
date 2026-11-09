import requests
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path


# PubMed API URL
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


# Where we will save downloaded papers
OUTPUT_FILE = Path("data/raw/pubmed/papers.jsonl")


# Function 1: Search PubMed
def search_papers(query, max_results=10):

    url = f"{BASE_URL}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    paper_ids = data["esearchresult"]["idlist"]

    return paper_ids


# Function 2: Download paper details
def fetch_papers(paper_ids):

    if not paper_ids:
        return []

    url = f"{BASE_URL}/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "xml"
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    papers = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//MedlineCitation/PMID")

        title_element = article.find(".//ArticleTitle")

        title = (
            "".join(title_element.itertext()).strip()
            if title_element is not None
            else ""
        )

        abstract_parts = article.findall(
            ".//Article/Abstract/AbstractText"
        )

        abstract = " ".join(
            "".join(part.itertext()).strip()
            for part in abstract_parts
        )

        if pmid and abstract:

            paper = {
                "pmid": pmid,
                "title": title,
                "abstract": abstract
            }

            papers.append(paper)

    return papers


# Function 3: Save papers
def save_papers(papers):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    existing_ids = set()

    if OUTPUT_FILE.exists():

        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:

            for line in file:

                if line.strip():
                    paper = json.loads(line)
                    existing_ids.add(paper["pmid"])

    new_count = 0

    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:

        for paper in papers:

            if paper["pmid"] not in existing_ids:

                file.write(
                    json.dumps(paper, ensure_ascii=False) + "\n"
                )

                existing_ids.add(paper["pmid"])
                new_count += 1

    return new_count


# Function 4: Run complete pipeline
def download_papers(query, max_results=10):

    print("Searching PubMed...")

    paper_ids = search_papers(query, max_results)

    print(f"Found {len(paper_ids)} paper IDs")

    if not paper_ids:
        return

    time.sleep(0.4)

    print("Downloading paper details...")

    papers = fetch_papers(paper_ids)

    print(f"Downloaded {len(papers)} papers with abstracts")

    new_count = save_papers(papers)

    print(f"Saved {new_count} new papers")

    print(f"Dataset location: {OUTPUT_FILE}")