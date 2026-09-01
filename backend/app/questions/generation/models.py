from typing import Any

from pydantic import BaseModel, Field


class ResearchContextItem(BaseModel):
    """One compact, ID-tagged fact drawn from the guest's latest structured
    GuestResearch (never from raw search-provider source content)."""

    id: str
    item_type: str
    fact: str
    source_urls: list[str] = Field(default_factory=list)


class QuestionGenerationOptions(BaseModel):
    count: int
    language: str
    style: str
    include_followups: bool
    topics: list[str] | None = None


class GeneratedQuestionItem(BaseModel):
    text: str
    topic: str | None = None
    category: str
    priority: str = "medium"
    research_item_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    reason: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)


class QuestionGenerationResult(BaseModel):
    questions: list[GeneratedQuestionItem] = Field(default_factory=list)
    raw_ai_response: dict[str, Any] | None = None
