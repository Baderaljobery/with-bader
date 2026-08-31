import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest_link import GuestLink
from app.schemas.guest_link import GuestLinkCreate, GuestLinkUpdate
from app.services.guest_service import get_guest_by_id


class GuestLinkNotFoundError(Exception):
    """Raised when a guest link does not exist."""


def create_guest_link(db: Session, guest_id: uuid.UUID, link_in: GuestLinkCreate) -> GuestLink:
    get_guest_by_id(db, guest_id)

    link = GuestLink(guest_id=guest_id, label=link_in.label, url=str(link_in.url))
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_guest_links(db: Session, guest_id: uuid.UUID) -> list[GuestLink]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(GuestLink)
        .where(GuestLink.guest_id == guest_id)
        .order_by(GuestLink.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def get_guest_link_by_id(db: Session, link_id: uuid.UUID) -> GuestLink:
    link = db.get(GuestLink, link_id)
    if link is None:
        raise GuestLinkNotFoundError(f"Guest link '{link_id}' not found")
    return link


def update_guest_link(db: Session, link_id: uuid.UUID, link_in: GuestLinkUpdate) -> GuestLink:
    link = get_guest_link_by_id(db, link_id)

    updates = link_in.model_dump(exclude_unset=True)
    if updates.get("url") is not None:
        updates["url"] = str(updates["url"])

    for field, value in updates.items():
        setattr(link, field, value)

    db.commit()
    db.refresh(link)
    return link


def delete_guest_link(db: Session, link_id: uuid.UUID) -> None:
    link = get_guest_link_by_id(db, link_id)
    db.delete(link)
    db.commit()
