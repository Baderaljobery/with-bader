import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

DESIGN_PLATFORMS = ("linkedin", "x", "instagram", "general")
DESIGN_STATUSES = ("draft", "approved")
DESIGN_ASPECT_RATIOS = ("1:1", "4:5", "16:9", "9:16")


class DesignDraft(Base):
    """Shared configuration for a multi-slide design set. Per-slide content
    and image state lives on DesignSlide (design_slides table) - see
    app/models/design_slide.py. template_id and slide_count are always a
    manual user choice, never inferred."""

    __tablename__ = "design_drafts"
    __table_args__ = (
        CheckConstraint(
            "platform IN (" + ", ".join(f"'{p}'" for p in DESIGN_PLATFORMS) + ")",
            name="design_drafts_platform_check",
        ),
        CheckConstraint(
            "status IN (" + ", ".join(f"'{s}'" for s in DESIGN_STATUSES) + ")",
            name="design_drafts_status_check",
        ),
        CheckConstraint(
            "aspect_ratio IN (" + ", ".join(f"'{a}'" for a in DESIGN_ASPECT_RATIOS) + ")",
            name="design_drafts_aspect_ratio_check",
        ),
        CheckConstraint("slide_count >= 1 AND slide_count <= 5", name="design_drafts_slide_count_check"),
        Index("idx_design_drafts_guest_id", "guest_id"),
        Index("idx_design_drafts_content_draft_id", "content_draft_id"),
        Index("idx_design_drafts_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False
    )
    content_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_drafts.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")

    template_id: Mapped[str] = mapped_column(Text, nullable=False)
    slide_count: Mapped[int] = mapped_column(Integer, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(Text, nullable=False)

    background_color: Mapped[str] = mapped_column(Text, nullable=False)
    accent_color: Mapped[str] = mapped_column(Text, nullable=False)

    customizations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")

    ai_provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_model: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="design_drafts")
    content_draft: Mapped["ContentDraft | None"] = relationship()
    slides: Mapped[list["DesignSlide"]] = relationship(
        back_populates="design_draft",
        cascade="all, delete-orphan",
        order_by="DesignSlide.slide_index",
    )
