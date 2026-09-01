from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.json_schema import build_strict_json_schema

_ITEM_CONFIG = ConfigDict(extra="forbid")


class GroqMatchedAnswerItem(BaseModel):
    model_config = _ITEM_CONFIG

    question_ref: str
    spoken_question: str | None = None
    answer: str | None = None
    status: Literal["answered", "not_answered", "uncertain"] = "not_answered"
    confidence: float | None = Field(default=None, ge=0, le=1)


class GroqInterviewMatchSchema(BaseModel):
    """The exact shape requested from Groq via JSON-schema structured
    output. Never trusted as-is - always passed through postprocess.py,
    which validates question_ref against the refs actually supplied and
    collapses duplicate matches per question."""

    model_config = _ITEM_CONFIG

    matches: list[GroqMatchedAnswerItem] = Field(default_factory=list)


GROQ_INTERVIEW_MATCH_JSON_SCHEMA = build_strict_json_schema(GroqInterviewMatchSchema)
