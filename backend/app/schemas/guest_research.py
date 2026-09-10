import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResearchSource(BaseModel):
    type: str
    url: str | None = None
    title: str | None = None
    publisher: str | None = None
    published_at: datetime | None = None

    snippet: str | None = None
    content: str | None = None

    provider: str | None = None
    score: float | None = None
    query: str | None = None

    notes: str | None = None


class GuestResearchCreate(BaseModel):
    role_title: str | None = None
    company: str | None = None
    career_history: list[Any] = Field(default_factory=list)
    education: list[Any] = Field(default_factory=list)
    achievements: list[Any] = Field(default_factory=list)
    projects: list[Any] = Field(default_factory=list)
    topics: list[Any] = Field(default_factory=list)
    interesting_events: list[Any] = Field(default_factory=list)
    public_appearances: list[Any] = Field(default_factory=list)
    potential_interview_angles: list[Any] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    identity_confidence: float | None = None
    raw_ai_response: dict[str, Any] | list[Any] | None = None


class GuestResearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    version: int
    role_title: str | None = None
    company: str | None = None
    career_history: list[Any]
    education: list[Any]
    achievements: list[Any]
    projects: list[Any]
    topics: list[Any]
    interesting_events: list[Any]
    public_appearances: list[Any] = Field(default_factory=list)
    potential_interview_angles: list[Any]
    sources: list[Any]
    identity_confidence: float | None = None
    raw_ai_response: dict[str, Any] | list[Any] | None = None
    created_at: datetime
