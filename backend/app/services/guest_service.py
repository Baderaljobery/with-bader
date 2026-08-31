import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


class GuestNotFoundError(Exception):
    """Raised when a guest does not exist."""


class DuplicateSlugError(Exception):
    """Raised when a guest slug is already in use."""


def create_guest(db: Session, guest_in: GuestCreate) -> Guest:
    guest = Guest(**guest_in.model_dump())
    db.add(guest)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSlugError(f"Guest with slug '{guest_in.slug}' already exists") from exc
    db.refresh(guest)
    return guest


def get_guests(db: Session, skip: int = 0, limit: int = 100) -> list[Guest]:
    stmt = select(Guest).order_by(Guest.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_guest_by_id(db: Session, guest_id: uuid.UUID) -> Guest:
    guest = db.get(Guest, guest_id)
    if guest is None:
        raise GuestNotFoundError(f"Guest '{guest_id}' not found")
    return guest


def update_guest(db: Session, guest_id: uuid.UUID, guest_in: GuestUpdate) -> Guest:
    guest = get_guest_by_id(db, guest_id)

    for field, value in guest_in.model_dump(exclude_unset=True).items():
        setattr(guest, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSlugError(f"Guest with slug '{guest_in.slug}' already exists") from exc
    db.refresh(guest)
    return guest


def delete_guest(db: Session, guest_id: uuid.UUID) -> None:
    guest = get_guest_by_id(db, guest_id)
    db.delete(guest)
    db.commit()
