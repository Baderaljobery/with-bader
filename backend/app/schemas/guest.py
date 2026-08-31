import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

PreparationStatus = Literal[
    "not_started",
    "researching",
    "questions_ready",
    "interview_scheduled",
    "interview_completed",
]

ContentStatus = Literal["not_started", "in_progress", "review", "published"]


class GuestBase(BaseModel):
    name: str
    slug: str | None = None
    job_title: str | None = None
    company: str | None = None
    biography: str | None = None
    personal_notes: str | None = None
    research_summary: str | None = None
    preparation_status: PreparationStatus = "not_started"
    content_status: ContentStatus = "not_started"


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    job_title: str | None = None
    company: str | None = None
    biography: str | None = None
    personal_notes: str | None = None
    research_summary: str | None = None
    preparation_status: PreparationStatus | None = None
    content_status: ContentStatus | None = None


class GuestResponse(GuestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID | None = None
    photo_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
