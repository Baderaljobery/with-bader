import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionSource as QuestionVersionSource


class QuestionVersionCreate(BaseModel):
    text: str = Field(min_length=1)
    source: QuestionVersionSource


class QuestionVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID
    version: int
    text: str = Field(validation_alias="text_")
    source: QuestionVersionSource
    created_at: datetime
