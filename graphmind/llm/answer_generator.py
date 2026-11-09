
from graphmind.llm.client import call_llm
from graphmind.llm.prompts import SYSTEM_PROMPT


def format_evidence(evidence):
    """
    Convert retrieved evidence into text for the LLM.
    """

    formatted = []

    for paper in evidence:
        pmid = str(paper.get("pmid") or "").strip()
        title = paper.get("title") or "Untitled"

        chunks = paper.get("chunks") or []

        texts = [
            chunk.get("text", "")
            for chunk in chunks
            if chunk.get("text")
        ]

        if not texts and paper.get("abstract"):
            texts = [paper["abstract"]]

        if not pmid or not texts:
            continue

        evidence_text = "\n".join(texts)

        formatted.append(
            f"PMID: {pmid}\n"
            f"Title: {title}\n"
            f"Evidence: {evidence_text[:2500]}"
        )

    return "\n\n---\n\n".join(formatted)


def generate_answer(question: str, evidence: list[dict]) -> str:
    """
    Generate an answer using retrieved biomedical evidence.
    """

    if not evidence:
        return "Insufficient research evidence to answer the question."

    evidence_text = format_evidence(evidence)

    if not evidence_text:
        return "Insufficient research evidence to answer the question."

    user_prompt = f"""
Question:
{question}

Research evidence:
{evidence_text}

Answer the question using the research evidence above.
Include PubMed citations for supported claims.
"""

    return call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
