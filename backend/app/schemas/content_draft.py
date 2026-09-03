import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ContentPlatform = Literal["linkedin", "x", "instagram", "general"]
ContentLength = Literal["short", "medium", "detailed"]
ContentStatus = Literal["draft", "approved"]


class ContentDraftCreate(BaseModel):
    platform: ContentPlatform
    length: ContentLength
    title: str | None = None
    content: str = Field(min_length=1)
    # Category keys from ContentGenerationResponse.sources_used when saving a
    # generated preview (e.g. ["answers", "notebook"]) - empty for a
    # manually-written draft. Never the raw prompt or model response.
    source_context: list[str] = Field(default_factory=list)
    ai_provider: str | None = None
    ai_model: str | None = None


class ContentDraftUpdate(BaseModel):
    platform: ContentPlatform | None = None
    length: ContentLength | None = None
    title: str | None = None
    content: str | None = Field(default=None, min_length=1)
    status: ContentStatus | None = None


class ContentDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    platform: ContentPlatform
    length: ContentLength
    title: str | None = None
    content: str
    status: ContentStatus
    source_context: list[str]
    ai_provider: str | None = None
    ai_model: str | None = None
    created_at: datetime
    updated_at: datetime
