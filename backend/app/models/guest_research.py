import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
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
    potential_interview_angles: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    sources: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")

    raw_ai_response: Mapped[Any | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="research_versions")
