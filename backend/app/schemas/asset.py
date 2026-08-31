import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

AssetType = Literal["guest_photo", "pdf_upload", "image", "document", "other"]


class AssetBase(BaseModel):
    guest_id: uuid.UUID | None = None
    type: AssetType
    file_name: str = Field(min_length=1)
    file_path: str = Field(min_length=1)
    mime_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    guest_id: uuid.UUID | None = None
    type: AssetType | None = None
    file_name: str | None = Field(default=None, min_length=1)
    file_path: str | None = Field(default=None, min_length=1)
    mime_type: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_by: uuid.UUID | None = None
    guest_id: uuid.UUID | None = None
    type: AssetType
    file_name: str
    file_path: str
    mime_type: str | None = None
    size_bytes: int | None = None
    metadata: dict[str, Any] = Field(validation_alias="metadata_")
    created_at: datetime
