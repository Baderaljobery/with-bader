from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# The fixed set of objectives the hybrid research planner is allowed to
# target (deterministic queries and AI-assisted query expansion alike) -
# see app/research/collectors/query_builder.py and
# app/research/research_planner.py. Never freely chosen by the AI.
RESEARCH_OBJECTIVES = (
    "identity",
    "career",
    "education",
    "achievements",
    "projects",
    "public_appearances",
    "recent",
)


class ResearchQuery(BaseModel):
    query: str
    reason: str | None = None
    priority: int | None = None
    objective: str | None = None
    language: str | None = None  # "ar" | "en" | None (mixed/unspecified)
    source: str = "deterministic"  # "deterministic" | "ai_planner"


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
    public_appearances: list[Any] = Field(default_factory=list)
    potential_interview_angles: list[Any] = Field(default_factory=list)
    raw_ai_response: dict[str, Any] | None = None
