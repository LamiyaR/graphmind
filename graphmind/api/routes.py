from fastapi import APIRouter, HTTPException

from graphmind.api.schemas import (
    QuestionRequest,
    QuestionResponse,
    Source
)

from graphmind.agent.workflow import build_graph


router = APIRouter()

agent = build_graph()


@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):

    try:
        result = agent.invoke({
            "question": request.question,
            "evidence": [],
            "answer": "",
            "evidence_sufficient": False,
            "retry_count": 0
        })

        sources = []
        seen_pmids = set()

        for paper in result.get("evidence", []):

            pmid = str(paper.get("pmid") or "").strip()

            if not pmid or pmid in seen_pmids:
                continue

            seen_pmids.add(pmid)

            sources.append(
                Source(
                    pmid=pmid,
                    title=paper.get("title") or ""
                )
            )

        return QuestionResponse(
            question=request.question,
            answer=result.get("answer", ""),
            sources=sources
        )

    except Exception as error:
        print("GraphMind API error:", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to process biomedical question"
        ) from error