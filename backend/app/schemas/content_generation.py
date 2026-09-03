import uuid
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.content_draft import ContentLength, ContentPlatform

ContentGenerationLanguage = Literal["ar", "en"]


class ContentGenerationRequest(BaseModel):
    platform: ContentPlatform
    length: ContentLength
    language: ContentGenerationLanguage = "ar"
    custom_instructions: str | None = Field(default=None, max_length=1000)


class ContentGenerationResponse(BaseModel):
    """Preview only - nothing here is persisted. The frontend must POST
    /api/guests/{guest_id}/content explicitly to save it as a draft."""

    guest_id: uuid.UUID
    platform: ContentPlatform
    length: ContentLength
    language: ContentGenerationLanguage
    title: str | None = None
    content: str
    sources_used: list[str] = Field(default_factory=list)
    ai_provider: str
    ai_model: str | None = None
