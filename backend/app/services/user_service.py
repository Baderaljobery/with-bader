import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    """Raised on registration when the (normalized) email is already in use."""


class UserNotFoundError(Exception):
    """Raised when a user id does not exist."""


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def create_user(db: Session, name: str, email: str, password: str) -> User:
    """`email` must already be normalized (lowercased/stripped) by the
    caller - see app/schemas/auth.py's validators, which every entry point
    into this function goes through."""
    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError(f"Email '{email}' is already registered") from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Returns `None` uniformly for "no such email" and "wrong password" -
    callers must never distinguish these in the response (see
    app/api/auth.py)."""
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def delete_user_account(db: Session, user_id: uuid.UUID) -> None:
    """Deletes the user row - every Guest with `created_by == user_id`
    cascades away automatically (see database/008_authentication.sql,
    which changes that foreign key from ON DELETE SET NULL to ON DELETE
    CASCADE), and each Guest's own cascades already remove all of its
    research/questions/transcript/notebook/content/designs. This never
    touches rows owned by any other user."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise UserNotFoundError(f"User '{user_id}' not found")
    db.delete(user)
    db.commit()
