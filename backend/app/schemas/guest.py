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

ContentStatus = Literal["not_started", "in_progress", "published"]


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
    # Calendar feature: at most one scheduled interview per guest. Naive
    # datetime (no timezone) - see app/models/guest.py.
    interview_scheduled_at: datetime | None = None
    interview_location: str | None = None


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
    # Setting content_status above always marks it manual. Send
    # content_status_manual=False on its own (no content_status) to clear
    # an existing override and let the automatic Calendar-derived rule take
    # back over - see guest_service.update_guest.
    content_status_manual: bool | None = None
    interview_scheduled_at: datetime | None = None
    interview_location: str | None = None


class GuestResponse(GuestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID | None = None
    photo_id: uuid.UUID | None = None
    content_status_manual: bool = False
    created_at: datetime
    updated_at: datetime
