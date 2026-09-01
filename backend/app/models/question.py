import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint(
            "source IN ('manual', 'ai_generated', 'ai_improved')",
            name="questions_source_check",
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'asked', 'answered')",
            name="questions_status_check",
        ),
        CheckConstraint("position >= 0", name="questions_position_check"),
        CheckConstraint(
            "answer_status IN ('not_answered', 'answered', 'uncertain')",
            name="questions_answer_status_check",
        ),
        CheckConstraint(
            "answer_source IS NULL OR answer_source IN ('manual', 'ai_extracted')",
            name="questions_answer_source_check",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False
    )

    text_: Mapped[str] = mapped_column("text", Text, nullable=False)

    source: Mapped[str] = mapped_column(String, nullable=False, server_default="manual")
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="draft")
    topic: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    is_important: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_optional: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    spoken_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_status: Mapped[str] = mapped_column(
        String, nullable=False, server_default="not_answered"
    )
    answer_source: Mapped[str | None] = mapped_column(String, nullable=True)
    answer_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    guest: Mapped["Guest"] = relationship(back_populates="questions")
    versions: Mapped[list["QuestionVersion"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    linked_blocks: Mapped[list["Block"]] = relationship(back_populates="linked_question")
