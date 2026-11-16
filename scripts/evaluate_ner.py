
import csv
import json
from pathlib import Path

from graphmind.ingest.biomedical_ner import (
    load_ner_model,
    extract_with_ner
)


EVAL_FILE = Path("data/fixtures/ner_eval.json")
OUTPUT_FILE = Path("data/processed/ner_metrics.csv")


def calculate_metrics(tp, fp, fn):

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return precision, recall, f1


def entity_key(entity):
    """
    Strict matching:
    start offset, end offset and entity type.
    """

    return (
        int(entity["start"]),
        int(entity["end"]),
        str(entity["type"]).strip().lower()
    )


def main():

    with EVAL_FILE.open(encoding="utf-8") as file:
        evaluations = json.load(file)

    model = load_ner_model()

    total_tp = 0
    total_fp = 0
    total_fn = 0

    rows = []

    for item in evaluations:

        pmid = item["pmid"]
        text = item["text"]

        gold = {
            entity_key(entity)
            for entity in item["entities"]
        }

        predictions = extract_with_ner(
            text=text,
            pmid=pmid,
            model=model
        )

        predicted = {
            entity_key(entity)
            for entity in predictions
        }

        tp = len(gold & predicted)
        fp = len(predicted - gold)
        fn = len(gold - predicted)

        precision, recall, f1 = calculate_metrics(
            tp, fp, fn
        )

        total_tp += tp
        total_fp += fp
        total_fn += fn

        rows.append({
            "pmid": pmid,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        })

        print(f"\nEvaluating: {pmid}")
        print("Gold entities:", gold)
        print("Predicted entities:", predicted)
        print("Precision:", round(precision, 4))
        print("Recall:", round(recall, 4))
        print("F1:", round(f1, 4))

    precision, recall, f1 = calculate_metrics(
        total_tp,
        total_fp,
        total_fn
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n===== FINAL NER EVALUATION =====")
    print("True positives:", total_tp)
    print("False positives:", total_fp)
    print("False negatives:", total_fn)
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1-score:", round(f1, 4))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
