
from transformers import pipeline


MODEL_NAME = "d4data/biomedical-ner-all"


def load_ner_model():
    print("Loading biomedical NER model...")

    model = pipeline(
        "token-classification",
        model=MODEL_NAME,
        aggregation_strategy="simple",
        device=-1
    )

    return model


def extract_with_ner(text, pmid, model):
    """
    Extract biomedical entities from a paper's text.
    """

    if not text.strip():
        return []

    entities = []

    # Process shorter sections to fit the model.
    chunk_size = 1000

    for offset in range(0, len(text), chunk_size):
        chunk = text[offset:offset + chunk_size]

        predictions = model(chunk)

        for item in predictions:
            entities.append({
                "pmid": str(pmid),
                "text": item["word"].strip(),
                "type": item["entity_group"],
                "identifier": None,
                "start": offset + item["start"],
                "end": offset + item["end"],
                "source": "biomedical_ner",
                "score": round(float(item["score"]), 4)
            })

    return entities
