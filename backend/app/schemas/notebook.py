import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotebookBase(BaseModel):
    title: str = Field(default="Notebook", min_length=1)


class NotebookCreate(NotebookBase):
    pass


class NotebookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
