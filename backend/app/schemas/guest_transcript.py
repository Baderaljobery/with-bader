import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GuestTranscriptCreate(BaseModel):
    text: str = Field(min_length=1)
    stt_provider: str | None = None
    stt_model: str | None = None


class GuestTranscriptTextUpdate(BaseModel):
    text: str = Field(min_length=1)


class GuestTranscriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    text: str = Field(validation_alias="text_")
    stt_provider: str | None = None
    stt_model: str | None = None
    created_at: datetime
    updated_at: datetime
