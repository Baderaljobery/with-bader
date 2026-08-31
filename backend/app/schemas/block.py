import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

BlockType = Literal[
    "heading",
    "paragraph",
    "question",
    "answer",
    "quote",
    "highlight",
    "bullet_list",
    "numbered_list",
    "checklist",
    "divider",
    "image",
    "callout",
    "table",
    "guest_info",
    "content_idea",
    "personal_note",
]


class BlockBase(BaseModel):
    type: BlockType
    content: dict[str, Any] = Field(default_factory=dict)
    position: float = 0
    is_important: bool = False
    is_potential_content: bool = False
    linked_question_id: uuid.UUID | None = None


class BlockCreate(BlockBase):
    pass


class BlockUpdate(BaseModel):
    type: BlockType | None = None
    content: dict[str, Any] | None = None
    position: float | None = None
    is_important: bool | None = None
    is_potential_content: bool | None = None
    linked_question_id: uuid.UUID | None = None


class BlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    page_id: uuid.UUID
    type: BlockType
    content: dict[str, Any]
    position: float
    is_important: bool
    is_potential_content: bool
    linked_question_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
