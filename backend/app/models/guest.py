import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Guest(Base):
    __tablename__ = "guests"
    __table_args__ = (
        CheckConstraint(
            "preparation_status IN ("
            "'not_started', 'researching', 'questions_ready', "
            "'interview_scheduled', 'interview_completed'"
            ")",
            name="guests_preparation_status_check",
        ),
        CheckConstraint(
            "content_status IN ('not_started', 'in_progress', 'review', 'published')",
            name="guests_content_status_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    job_title: Mapped[str | None] = mapped_column(String, nullable=True)
    company: Mapped[str | None] = mapped_column(String, nullable=True)

    photo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )

    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    personal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    preparation_status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="not_started"
    )
    content_status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="not_started"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    created_by_user: Mapped["User"] = relationship(
        back_populates="guests", foreign_keys=[created_by]
    )
    notebooks: Mapped[list["Notebook"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
    questions: Mapped[list["Question"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
    guest_links: Mapped[list["GuestLink"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
    research_versions: Mapped[list["GuestResearch"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
