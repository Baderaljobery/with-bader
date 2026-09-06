import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('owner', 'editor')", name="users_role_check"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, server_default="owner")

    profile_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # passive_deletes=True is required here: without it, SQLAlchemy's ORM
    # would load this collection on every user delete and issue its own
    # UPDATE ... SET created_by = NULL for each guest (its default
    # behavior for a relationship with no delete cascade configured) -
    # silently overriding and defeating the database's own
    # ON DELETE CASCADE on guests.created_by (see
    # database/008_authentication.sql and
    # app/services/user_service.py's delete_user_account). With
    # passive_deletes=True, SQLAlchemy leaves child-row handling entirely
    # to the database's real foreign key behavior.
    guests: Mapped[list["Guest"]] = relationship(
        back_populates="created_by_user", foreign_keys="Guest.created_by", passive_deletes=True
    )
