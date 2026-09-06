import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate


class GuestNotFoundError(Exception):
    """Raised when a guest does not exist - also raised (never a different
    error) when it exists but belongs to a different user, so ownership
    mismatches are indistinguishable from "doesn't exist" to any caller."""


class DuplicateSlugError(Exception):
    """Raised when a guest slug is already in use."""


def _auto_content_status(guest: Guest) -> str:
    """The V1 automatic rule: a scheduled interview means content prep is
    under way. `published` is never inferred - there is no real publishing
    integration yet, so it can only be set manually (see update_guest)."""
    return "in_progress" if guest.interview_scheduled_at is not None else "not_started"


def create_guest(db: Session, guest_in: GuestCreate, created_by: uuid.UUID | None = None) -> Guest:
    """`created_by` is always the authenticated user's id in production use
    (see app/api/guests.py) - the client-supplied `guest_in` has no
    `created_by` field at all (see app/schemas/guest.py), so there is
    nothing for it to override. The default of `None` exists only so
    existing tests for *other* features, which create guests purely as
    fixtures and predate ownership, keep working unchanged."""
    guest = Guest(**guest_in.model_dump(), created_by=created_by)
    db.add(guest)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSlugError(f"Guest with slug '{guest_in.slug}' already exists") from exc
    db.refresh(guest)
    return guest


def get_guests(db: Session, created_by: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Guest]:
    stmt = (
        select(Guest)
        .where(Guest.created_by == created_by)
        .order_by(Guest.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_guest_by_id(db: Session, guest_id: uuid.UUID) -> Guest:
    """Unscoped by design - internal callers (every other domain service)
    use this only for an already ownership-gated guest_id, after the API
    layer has already verified access via get_guest_by_id_for_user below.
    Never call this directly from an API endpoint."""
    guest = db.get(Guest, guest_id)
    if guest is None:
        raise GuestNotFoundError(f"Guest '{guest_id}' not found")
    return guest


def get_guest_by_id_for_user(db: Session, guest_id: uuid.UUID, user_id: uuid.UUID) -> Guest:
    """The real access-control checkpoint (Part 12) - every API endpoint
    that takes a guest_id (directly or as a path prefix for a nested
    resource) must call this, not get_guest_by_id. Returns the same
    GuestNotFoundError for "doesn't exist" and "exists but isn't yours" -
    never leaks which one it was."""
    guest = get_guest_by_id(db, guest_id)
    if guest.created_by != user_id:
        raise GuestNotFoundError(f"Guest '{guest_id}' not found")
    return guest


def update_guest(db: Session, guest_id: uuid.UUID, guest_in: GuestUpdate) -> Guest:
    guest = get_guest_by_id(db, guest_id)

    updates = guest_in.model_dump(exclude_unset=True)
    # content_status/content_status_manual are handled below, once the rest
    # of the fields (interview_scheduled_at in particular) are applied -
    # the automatic rule needs to see the *new* schedule, not the old one.
    manual_status = updates.pop("content_status", None)
    manual_flag = updates.pop("content_status_manual", None)

    for field, value in updates.items():
        setattr(guest, field, value)

    if manual_status is not None:
        guest.content_status = manual_status
        guest.content_status_manual = True
    elif manual_flag is not None:
        guest.content_status_manual = manual_flag

    if not guest.content_status_manual:
        guest.content_status = _auto_content_status(guest)

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
