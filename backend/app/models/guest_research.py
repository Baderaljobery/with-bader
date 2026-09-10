import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GuestResearch(Base):
    __tablename__ = "guest_research"
    __table_args__ = (
        CheckConstraint("version > 0", name="guest_research_version_check"),
        UniqueConstraint("guest_id", "version", name="guest_research_guest_id_version_key"),
        Index("idx_guest_research_guest_id", "guest_id"),
        Index("idx_guest_research_guest_version", "guest_id", "version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False
    )

    version: Mapped[int] = mapped_column(Integer, nullable=False)

    role_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str | None] = mapped_column(Text, nullable=True)

    career_history: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    education: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    achievements: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    projects: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    topics: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    interesting_events: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    # Prior public activity (interviews, podcasts, panels, keynotes,
    # articles quoting the guest) - about the guest's history BEFORE this
    # research run, never about the future With Bader interview itself.
    public_appearances: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    potential_interview_angles: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    sources: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")

    # Aggregate identity-relevance signal for this run's evidence (Phase 11,
    # app/research/identity_resolution.py) - 0..1, null for pre-existing
    # rows saved before this concept existed. Low values mean the run found
    # little evidence confidently tied to this specific guest; the frontend
    # surfaces this as "identity confirmation may be needed" rather than
    # presenting a sparse result as if it were simply "no news found".
    identity_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    raw_ai_response: Mapped[Any | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="research_versions")
