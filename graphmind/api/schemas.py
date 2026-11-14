from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class Source(BaseModel):
    pmid: str
    title: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]