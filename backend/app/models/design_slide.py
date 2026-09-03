import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

DESIGN_SLIDE_ROLES = (
    "cover",
    "main_content",
    "continuation",
    "quote",
    "quick_points",
    "closing",
)


class DesignSlide(Base):
    """One slide within a DesignDraft's multi-slide set. role/headline/
    body_text/cta_text are produced by DesignContentPlanner and remain
    user-editable; image_path/prompt are null until that specific slide's
    image has been generated (preview-first: text is approved before any
    Gemini/OpenRouter call is made) - see app/design_planning/ and
    app/design_generation/."""

    __tablename__ = "design_slides"
    __table_args__ = (
        CheckConstraint(
            "role IN (" + ", ".join(f"'{r}'" for r in DESIGN_SLIDE_ROLES) + ")",
            name="design_slides_role_check",
        ),
        CheckConstraint("slide_index >= 1 AND slide_index <= 5", name="design_slides_slide_index_check"),
        UniqueConstraint("design_draft_id", "slide_index", name="design_slides_draft_index_unique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    design_draft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("design_drafts.id", ondelete="CASCADE"), nullable=False
    )

    slide_index: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)

    headline: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    body_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    cta_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    customizations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    design_draft: Mapped["DesignDraft"] = relationship(back_populates="slides")
