import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Text, func, text
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
            "content_status IN ('not_started', 'in_progress', 'published')",
            name="guests_content_status_check",
        ),
        Index("idx_guests_created_by", "created_by"),
        Index("idx_guests_preparation_status", "preparation_status"),
        Index("idx_guests_content_status", "content_status"),
        Index("idx_guests_name", "name"),
        Index(
            "idx_guests_interview_scheduled_at",
            "interview_scheduled_at",
            postgresql_where=text("interview_scheduled_at IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    job_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    company: Mapped[str | None] = mapped_column(Text, nullable=True)

    photo_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "assets.id",
            name="guests_photo_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        ),
        nullable=True,
    )

    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    personal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    preparation_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="not_started"
    )
    content_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="not_started"
    )
    # True once the user has explicitly chosen content_status themselves -
    # while False, content_status is kept in sync with the automatic
    # Calendar-derived rule instead (see guest_service.update_guest).
    content_status_manual: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    # Calendar feature (Part 007): at most one scheduled interview per guest,
    # no separate events table. Naive timestamp on purpose - this product
    # has no multi-timezone concept, so the plain wall-clock value entered
    # by the user is stored and returned as-is, with no UTC conversion.
    interview_scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    interview_location: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    transcript: Mapped["GuestTranscript | None"] = relationship(
        back_populates="guest", cascade="all, delete-orphan", uselist=False
    )
    content_drafts: Mapped[list["ContentDraft"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
    design_drafts: Mapped[list["DesignDraft"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan"
    )
