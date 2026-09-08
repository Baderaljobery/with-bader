import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

CONTENT_PLATFORMS = ("linkedin", "x", "instagram", "general")
CONTENT_LENGTHS = ("short", "medium", "detailed")
CONTENT_STATUSES = ("draft", "approved")


class ContentDraft(Base):
    __tablename__ = "content_drafts"
    __table_args__ = (
        CheckConstraint(
            "platform IN (" + ", ".join(f"'{p}'" for p in CONTENT_PLATFORMS) + ")",
            name="content_drafts_platform_check",
        ),
        CheckConstraint(
            "length IN (" + ", ".join(f"'{l}'" for l in CONTENT_LENGTHS) + ")",
            name="content_drafts_length_check",
        ),
        CheckConstraint(
            "status IN (" + ", ".join(f"'{s}'" for s in CONTENT_STATUSES) + ")",
            name="content_drafts_status_check",
        ),
        Index("idx_content_drafts_guest_id", "guest_id"),
        Index("idx_content_drafts_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False
    )

    platform: Mapped[str] = mapped_column(Text, nullable=False)
    length: Mapped[str] = mapped_column(Text, nullable=False)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")

    source_context: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")

    ai_provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_model: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="content_drafts")
