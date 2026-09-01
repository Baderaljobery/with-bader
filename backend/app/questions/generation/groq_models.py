from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.json_schema import build_strict_json_schema

_ITEM_CONFIG = ConfigDict(extra="forbid")


class GroqGeneratedQuestionItem(BaseModel):
    model_config = _ITEM_CONFIG

    text: str
    topic: str | None = None
    category: str
    priority: Literal["low", "medium", "high"] = "medium"
    research_item_ids: list[str] = Field(default_factory=list)
    reason: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)


class GroqQuestionGenerationSchema(BaseModel):
    """The exact shape requested from Groq via JSON-schema structured output.
    Deliberately has NO source_urls field anywhere - the model cites
    research_item_ids only; source_urls are resolved by application code in
    postprocess.py, never authored by the model."""

    model_config = _ITEM_CONFIG

    questions: list[GroqGeneratedQuestionItem] = Field(default_factory=list)


GROQ_QUESTION_GENERATION_JSON_SCHEMA = build_strict_json_schema(GroqQuestionGenerationSchema)
