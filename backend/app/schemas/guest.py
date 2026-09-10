import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PreparationStatus = Literal[
    "not_started",
    "researching",
    "questions_ready",
    "interview_scheduled",
    "interview_completed",
]

ContentStatus = Literal["not_started", "in_progress", "published"]

# The bilingual NAME is the only bilingual identity field. Required for
# every newly created guest (GuestCreate below); nullable at the DB level
# and in GuestUpdate for legacy-row compatibility - see app/models/guest.py
# and app/services/guest_service.py (update_guest's legacy-upgrade check).
# job_title/company/biography stay single-value, exactly as before.
_BILINGUAL_IDENTITY_FIELDS = (
    "name_ar",
    "name_en",
)


class GuestBase(BaseModel):
    name: str
    slug: str | None = None
    job_title: str | None = None
    company: str | None = None
    biography: str | None = None
    personal_notes: str | None = None
    research_summary: str | None = None

    name_ar: str | None = None
    name_en: str | None = None

    preparation_status: PreparationStatus = "not_started"
    content_status: ContentStatus = "not_started"
    # Calendar feature: at most one scheduled interview per guest. Naive
    # datetime (no timezone) - see app/models/guest.py.
    interview_scheduled_at: datetime | None = None
    interview_location: str | None = None


class GuestCreate(GuestBase):
    """The bilingual name is mandatory for every NEW guest - it's what makes
    the research planner (app/research/collectors/query_builder.py) and
    identity resolution (app/research/identity_resolution.py) cover both
    Arabic and English discovery. job_title/company/biography stay optional,
    single-value fields, same as before this feature existed. Existing rows
    are never retroactively required to have name_ar/name_en (see
    GuestUpdate) - this only gates guest CREATION."""

    # Overrides GuestBase.name (required there) - the legacy/display column
    # is derived from name_ar below, so callers don't need to pass it too.
    name: str | None = None
    name_ar: str = Field(min_length=1)
    name_en: str = Field(min_length=1)

    @field_validator(*_BILINGUAL_IDENTITY_FIELDS, mode="after")
    @classmethod
    def _reject_whitespace_only(cls, value: str) -> str:
        # Field(min_length=1) alone only checks raw length - "   " has
        # length 3 and would otherwise pass straight through as "required".
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @model_validator(mode="after")
    def _use_arabic_name_as_primary(self) -> "GuestCreate":
        # `name` (the legacy/display column) always mirrors name_ar for new
        # guests - callers never need to pass both, and display_name's
        # legacy fallback (Guest.display_name) never has to activate for a
        # row created under this schema.
        if not (self.name or "").strip():
            self.name = self.name_ar
        return self


class GuestUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    job_title: str | None = None
    company: str | None = None
    biography: str | None = None
    personal_notes: str | None = None
    research_summary: str | None = None

    name_ar: str | None = Field(default=None, min_length=1)
    name_en: str | None = Field(default=None, min_length=1)

    @field_validator(*_BILINGUAL_IDENTITY_FIELDS, mode="after")
    @classmethod
    def _reject_whitespace_only(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

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
    # Arabic-first display name for legacy rows created before this profile
    # existed (Guest.display_name = name_ar or the legacy `name` column) -
    # every field the frontend needs for Arabic-first display, without
    # requiring it to reimplement the fallback rule itself.
    display_name: str
