import uuid
from datetime import datetime

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class GuestLinkBase(BaseModel):
    label: str = Field(min_length=1)
    url: AnyUrl


class GuestLinkCreate(GuestLinkBase):
    pass


class GuestLinkUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1)
    url: AnyUrl | None = None


class GuestLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    guest_id: uuid.UUID
    label: str
    url: AnyUrl
    created_at: datetime
