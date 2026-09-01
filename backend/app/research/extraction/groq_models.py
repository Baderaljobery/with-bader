from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.json_schema import build_strict_json_schema

_ITEM_CONFIG = ConfigDict(extra="forbid")


class CareerHistoryItem(BaseModel):
    model_config = _ITEM_CONFIG

    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class EducationItem(BaseModel):
    model_config = _ITEM_CONFIG

    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    year: int | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class AchievementItem(BaseModel):
    model_config = _ITEM_CONFIG

    title: str
    description: str | None = None
    date: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class ProjectItem(BaseModel):
    model_config = _ITEM_CONFIG

    title: str
    description: str | None = None
    role: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class InterestingEventItem(BaseModel):
    model_config = _ITEM_CONFIG

    title: str
    description: str | None = None
    date: str | None = None
    why_interesting: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)


class InterviewAngleItem(BaseModel):
    model_config = _ITEM_CONFIG

    title: str
    reason: str
    priority: Literal["low", "medium", "high"] = "medium"
    source_ids: list[str] = Field(default_factory=list)


class GroqExtractionSchema(BaseModel):
    """The exact shape requested from Groq via JSON-schema structured output.
    Never persisted as-is - always passed through groq_postprocess first,
    which validates source_ids, resolves them to durable source_urls, and
    drops any factual item that ends up ungrounded."""

    model_config = _ITEM_CONFIG

    role_title: str | None = None
    company: str | None = None
    career_history: list[CareerHistoryItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    achievements: list[AchievementItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    interesting_events: list[InterestingEventItem] = Field(default_factory=list)
    potential_interview_angles: list[InterviewAngleItem] = Field(default_factory=list)


GROQ_EXTRACTION_JSON_SCHEMA = build_strict_json_schema(GroqExtractionSchema)
