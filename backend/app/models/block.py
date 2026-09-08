import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Double, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

BLOCK_TYPES = (
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
)


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (
        CheckConstraint(
            "type IN (" + ", ".join(f"'{block_type}'" for block_type in BLOCK_TYPES) + ")",
            name="blocks_type_check",
        ),
        Index("idx_blocks_page_id", "page_id"),
        Index("idx_blocks_page_position", "page_id", "position"),
        Index("idx_blocks_linked_question", "linked_question_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notebook_pages.id", ondelete="CASCADE"), nullable=False
    )

    type: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    position: Mapped[float] = mapped_column(Double, nullable=False, server_default="0")

    is_important: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_potential_content: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    linked_question_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    page: Mapped["NotebookPage"] = relationship(back_populates="blocks")
    linked_question: Mapped["Question | None"] = relationship(back_populates="linked_blocks")
