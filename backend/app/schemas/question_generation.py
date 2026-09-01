import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.schemas.question import QuestionResponse

QuestionGenerationLanguage = Literal["ar", "en"]
QuestionGenerationPriority = Literal["low", "medium", "high"]


class QuestionGenerationRequest(BaseModel):
    count: int = Field(default_factory=lambda: settings.question_generation_default_count, ge=1)
    language: QuestionGenerationLanguage = "ar"
    style: str = "conversational"
    include_followups: bool = True
    topics: list[str] | None = None

    @field_validator("count")
    @classmethod
    def _validate_count_max(cls, value: int) -> int:
        max_count = settings.question_generation_max_count
        if value > max_count:
            raise ValueError(f"count must be <= {max_count}")
        return value


class GeneratedQuestionResponse(BaseModel):
    text: str
    topic: str | None = None
    category: str
    priority: QuestionGenerationPriority = "medium"
    research_item_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    reason: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)


class QuestionGenerationResponse(BaseModel):
    guest_id: uuid.UUID
    research_id: uuid.UUID
    research_version: int
    generator_provider: str
    generator_model: str | None = None
    requested_count: int
    generated_count: int
    questions: list[GeneratedQuestionResponse]


class SelectedGeneratedQuestion(BaseModel):
    """What the client sends back to /generated/save for each question the
    user chose to keep. Only `text`/`topic` are currently persisted onto the
    questions table (see final report for why) - the rest are accepted so
    the client can round-trip the full preview payload, but are not yet
    stored with the row."""

    text: str = Field(min_length=1)
    topic: str | None = None
    category: str | None = None
    priority: QuestionGenerationPriority | None = None
    research_item_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
    reason: str | None = None
    follow_up_questions: list[str] = Field(default_factory=list)


class QuestionGenerationSaveRequest(BaseModel):
    questions: list[SelectedGeneratedQuestion] = Field(min_length=1)


class QuestionGenerationSaveResponse(BaseModel):
    guest_id: uuid.UUID
    saved_count: int
    questions: list[QuestionResponse]
