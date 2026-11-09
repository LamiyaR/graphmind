
import requests

BASE_URL = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api"


def fetch_annotations(pmid):
    """
    Download biomedical annotations for one PubMed paper.
    """

    def fetch_annotations(pmid):
        """ 
        Download biomedical annotations for a PubMed paper.
        Return None if annotations are unavailable. 
        """""

    url = f"{BASE_URL}/publications/export/pubtator"

    params = {
        "pmids": str(pmid)
    }

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    if response.status_code == 400:
        print(f"PubTator3 could not process PMID {pmid}")
        return None

    response.raise_for_status()

    return response.text


def extract_entities(pubtator_text):
    """
    Extract biomedical entities from PubTator format.
    """

    entities = []

    for line in pubtator_text.splitlines():

        columns = line.split("\t")

        if len(columns) < 6:
            continue

        pmid, start, end, mention, entity_type, entity_id = columns[:6]

        entities.append({
            "pmid": pmid,
            "text": mention,
            "type": entity_type,
            "identifier": entity_id,
            "start": int(start),
            "end": int(end)
        })

    return entities
