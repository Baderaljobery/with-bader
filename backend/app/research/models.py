from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResearchQuery(BaseModel):
    query: str
    reason: str | None = None
    priority: int | None = None


class RawResearchSource(BaseModel):
    source_type: str
    url: str | None = None
    title: str | None = None
    publisher: str | None = None
    published_at: datetime | None = None
    content: str | None = None
    snippet: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedResearchSource(BaseModel):
    source_type: str
    url: str | None = None
    canonical_url: str | None = None
    title: str | None = None
    publisher: str | None = None
    published_at: datetime | None = None
    content: str | None = None
    snippet: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchExtractionResult(BaseModel):
    role_title: str | None = None
    company: str | None = None
    career_history: list[Any] = Field(default_factory=list)
    education: list[Any] = Field(default_factory=list)
    achievements: list[Any] = Field(default_factory=list)
    projects: list[Any] = Field(default_factory=list)
    topics: list[Any] = Field(default_factory=list)
    interesting_events: list[Any] = Field(default_factory=list)
    potential_interview_angles: list[Any] = Field(default_factory=list)
    raw_ai_response: dict[str, Any] | None = None
