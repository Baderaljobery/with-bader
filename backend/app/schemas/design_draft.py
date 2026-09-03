import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.design_slide import DesignSlideResponse

DesignPlatform = Literal["linkedin", "x", "instagram", "general"]
DesignStatus = Literal["draft", "approved"]
DesignAspectRatio = Literal["1:1", "4:5", "16:9", "9:16"]

HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


class DesignDraftUpdate(BaseModel):
    """Updates shared design-set settings only - per-slide text is edited
    via PATCH /api/designs/{design_id}/slides/{slide_index} instead (see
    app/schemas/design_slide.py)."""

    title: str | None = None
    background_color: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)
    accent_color: str | None = Field(default=None, pattern=HEX_COLOR_PATTERN)
    status: DesignStatus | None = None


class DesignDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    content_draft_id: uuid.UUID | None = None
    title: str | None = None
    platform: DesignPlatform
    status: DesignStatus
    template_id: str
    slide_count: int = Field(ge=1, le=5)
    aspect_ratio: DesignAspectRatio
    background_color: str
    accent_color: str
    customizations: dict[str, Any]
    ai_provider: str | None = None
    ai_model: str | None = None
    slides: list[DesignSlideResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
