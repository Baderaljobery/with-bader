import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class QuestionVersion(Base):
    __tablename__ = "question_versions"
    __table_args__ = (
        CheckConstraint("version > 0", name="question_versions_version_check"),
        CheckConstraint(
            "source IN ('manual', 'ai_generated', 'ai_improved')",
            name="question_versions_source_check",
        ),
        UniqueConstraint(
            "question_id", "version", name="question_versions_question_id_version_key"
        ),
        Index("idx_question_versions_question_id", "question_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    version: Mapped[int] = mapped_column(Integer, nullable=False)
    text_: Mapped[str] = mapped_column("text", Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    question: Mapped["Question"] = relationship(back_populates="versions")
