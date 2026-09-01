from typing import Any

from pydantic import BaseModel, Field


class QuestionContext(BaseModel):
    """One saved question exposed to the matcher, with a stable local ref
    (Q1..Qn) the model must cite - never a UUID, never the question's own
    text used as an identifier."""

    ref: str
    question_id: str
    text: str


class MatchedAnswer(BaseModel):
    question_ref: str
    spoken_question: str | None = None
    answer: str | None = None
    status: str = "not_answered"  # answered | not_answered | uncertain
    confidence: float | None = None


class QuestionAnswerMatchResult(BaseModel):
    matches: list[MatchedAnswer] = Field(default_factory=list)
    raw_ai_response: dict[str, Any] | None = None
