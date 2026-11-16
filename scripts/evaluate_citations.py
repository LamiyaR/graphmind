
import csv
import json
import re
from pathlib import Path

import requests


API_URL = "http://127.0.0.1:8000/ask"

QUESTIONS_FILE = Path(
    "data/fixtures/retrieval_eval.json"
)

PAPERS_FILE = Path(
    "data/raw/pubmed/papers.jsonl"
)

OUTPUT_FILE = Path(
    "data/processed/citation_review.csv"
)

SUMMARY_FILE = Path(
    "data/processed/citation_metrics.csv"
)

CITATION_PATTERN = re.compile(
    r"PMID\s*:\s*(\d+)",
    re.IGNORECASE
)


def load_papers():
    papers = {}

    with PAPERS_FILE.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            paper = json.loads(line)
            pmid = str(paper.get("pmid", "")).strip()

            if pmid:
                papers[pmid] = paper

    return papers


def split_claims(answer):
    """
    Extract individual findings and the PMIDs
    explicitly listed in Supporting Evidence.

    The returned associations are candidates for
    manual review, not verified citations.
    """

    findings = []
    supporting_pmids = []

    section = None

    for line in answer.splitlines():
        line = line.strip()

        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue

        if section == "key research findings":
            if line.startswith("- "):
                findings.append(line[2:].strip())

        elif section == "supporting evidence":
            supporting_pmids.extend(
                CITATION_PATTERN.findall(line)
            )

    supporting_pmids = list(
        dict.fromkeys(supporting_pmids)
    )

    claims = []

    for finding in findings:
        claims.append(
            (finding, supporting_pmids)
        )

    return claims


def generate_review_file():

    with QUESTIONS_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    papers = load_papers()

    rows = []

    for question_number, item in enumerate(
        questions, start=1
    ):

        question = item["question"]

        print(
            f"\nEvaluating question {question_number}: "
            f"{question}"
        )

        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get("answer", "")

        claims = split_claims(answer)

        if not claims:
            print("No inline PMID citations found.")

        for claim, citations in claims:

            for pmid in citations:

                paper = papers.get(pmid)

                rows.append({
                    "question": question,
                    "claim": claim,
                    "cited_pmid": pmid,
                    "pmid_exists": (
                        1 if paper else 0
                    ),
                    "paper_title": (
                        paper.get("title", "")
                        if paper else ""
                    ),
                    "paper_abstract": (
                        paper.get("abstract", "")
                        if paper else ""
                    ),
                    "supported": "",
                    "review_notes": ""
                })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "question",
        "claim",
        "cited_pmid",
        "pmid_exists",
        "paper_title",
        "paper_abstract",
        "supported",
        "review_notes"
    ]

    with OUTPUT_FILE.open(
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

    print("\nCitation review file generated!")
    print("Citation-bearing pairs:", len(rows))
    print("Saved to:", OUTPUT_FILE)


def calculate_metrics():

    with OUTPUT_FILE.open(
        encoding="utf-8",
        newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        print("No citation pairs found.")
        return

    total = len(rows)

    valid = sum(
        row["pmid_exists"] == "1"
        for row in rows
    )

    reviewed = [
        row for row in rows
        if row["supported"] in ("0", "1")
    ]

    supported = sum(
        row["supported"] == "1"
        for row in reviewed
    )

    validity = valid / total

    accuracy = (
        supported / len(reviewed)
        if reviewed else None
    )

    print("\n===== CITATION EVALUATION =====")
    print("Total citation pairs:", total)
    print("Valid PMIDs:", valid)
    print("Citation validity:", round(validity, 4))
    print("Manually reviewed pairs:", len(reviewed))

    if accuracy is None:
        print("Citation accuracy: Not yet evaluated")
    else:
        print(
            "Citation accuracy:",
            round(accuracy, 4)
        )

    SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "total_citation_pairs",
                "valid_pmids",
                "citation_validity",
                "reviewed_pairs",
                "supported_pairs",
                "citation_accuracy"
            ]
        )

        writer.writeheader()

        writer.writerow({
            "total_citation_pairs": total,
            "valid_pmids": valid,
            "citation_validity": validity,
            "reviewed_pairs": len(reviewed),
            "supported_pairs": supported,
            "citation_accuracy": (
                accuracy if accuracy is not None else ""
            )
        })

    print("Saved to:", SUMMARY_FILE)


def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--score",
        action="store_true",
        help="Calculate metrics from reviewed CSV"
    )

    args = parser.parse_args()

    if args.score:
        calculate_metrics()
    else:
        generate_review_file()


if __name__ == "__main__":
    main()
