import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResearchContextItem(BaseModel):
    """One compact, ID-tagged fact drawn from the guest's latest structured
    GuestResearch (never from raw search-provider source content)."""

    id: str
    item_type: str
    fact: str
    source_urls: list[str] = Field(default_factory=list)


class ExistingQuestionItem(BaseModel):
    """Compact saved-question context used for avoidance and validation."""

    id: str
    text: str
    topic: str | None = None
    source: str | None = None
    intent_summary: str | None = None
    research_item_ids: list[str] = Field(default_factory=list)


class QuestionGenerationOptions(BaseModel):
    count: int
    language: str
    style: str
    include_followups: bool
    topics: list[str] | None = None


class GeneratedQuestionItem(BaseModel):
    candidate_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text: str
    topic: str | None = None
    category: str
    intent_summary: str = ""
    priority: str = "medium"
    research_item_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    reason: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)


DuplicateClassification = Literal[
    "DUPLICATE", "SAME_TOPIC_DIFFERENT_ANGLE", "DIFFERENT"
]


class SemanticComparisonPair(BaseModel):
    id: str
    candidate: GeneratedQuestionItem
    reference: ExistingQuestionItem


class SemanticComparisonDecision(BaseModel):
    pair_id: str
    classification: DuplicateClassification


class QuestionGenerationResult(BaseModel):
    questions: list[GeneratedQuestionItem] = Field(default_factory=list)
    raw_ai_response: dict[str, Any] | None = None
