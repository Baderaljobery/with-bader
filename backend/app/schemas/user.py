import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

UserRole = Literal["owner", "editor"]


class UserResponse(BaseModel):
    """Never includes password_hash - this is a read-only identity view for
    the Settings page, not an authentication payload."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    created_at: datetime
