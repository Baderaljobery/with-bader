import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SlideRole = Literal["cover", "main_content", "continuation", "quote", "quick_points", "closing"]


class DesignSlideUpdate(BaseModel):
    headline: str | None = None
    body_text: str | None = None
    cta_text: str | None = None


class DesignSlideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    design_draft_id: uuid.UUID
    slide_index: int = Field(ge=1, le=5)
    role: SlideRole
    headline: str
    body_text: str
    cta_text: str | None = None
    # prompt is deliberately NOT exposed - never shown to end users, same
    # convention as every other AI-generation feature in this project.
    image_path: str | None = None
    created_at: datetime
    updated_at: datetime
