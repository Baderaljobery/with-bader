import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotebookPageBase(BaseModel):
    title: str = Field(default="Untitled Page", min_length=1)
    position: int = Field(default=0, ge=0)


class NotebookPageCreate(NotebookPageBase):
    pass


class NotebookPageUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    position: int | None = Field(default=None, ge=0)


class NotebookPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    notebook_id: uuid.UUID
    title: str
    position: int
    created_at: datetime
    updated_at: datetime
