import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

QuestionSource = Literal["manual", "ai_generated", "ai_improved"]
QuestionStatus = Literal["draft", "approved", "asked", "answered"]


class QuestionBase(BaseModel):
    text: str = Field(min_length=1)
    source: QuestionSource = "manual"
    status: QuestionStatus = "draft"
    topic: str | None = None
    position: int = Field(default=0, ge=0)
    is_important: bool = False
    is_optional: bool = False
    notes: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    source: QuestionSource | None = None
    status: QuestionStatus | None = None
    topic: str | None = None
    position: int | None = Field(default=None, ge=0)
    is_important: bool | None = None
    is_optional: bool | None = None
    notes: str | None = None


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    text: str = Field(validation_alias="text_")
    source: QuestionSource
    status: QuestionStatus
    topic: str | None = None
    position: int
    is_important: bool
    is_optional: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
