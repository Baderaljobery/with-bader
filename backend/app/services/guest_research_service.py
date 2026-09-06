import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.guest_research import GuestResearch
from app.schemas.guest_research import GuestResearchCreate
from app.services.guest_service import get_guest_by_id


class GuestResearchNotFoundError(Exception):
    """Raised when a guest research version does not exist."""


def create_guest_research(
    db: Session, guest_id: uuid.UUID, research_in: GuestResearchCreate
) -> GuestResearch:
    get_guest_by_id(db, guest_id)

    highest_version = db.scalar(
        select(func.coalesce(func.max(GuestResearch.version), 0)).where(
            GuestResearch.guest_id == guest_id
        )
    )

    data = research_in.model_dump(mode="json", exclude={"sources"})
    data["sources"] = [source.model_dump(mode="json") for source in research_in.sources]

    research = GuestResearch(
        guest_id=guest_id,
        version=highest_version + 1,
        **data,
    )
    db.add(research)
    db.commit()
    db.refresh(research)
    return research


def get_guest_research_history(db: Session, guest_id: uuid.UUID) -> list[GuestResearch]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(GuestResearch)
        .where(GuestResearch.guest_id == guest_id)
        .order_by(GuestResearch.version.asc())
    )
    return list(db.scalars(stmt).all())


def get_latest_guest_research(db: Session, guest_id: uuid.UUID) -> GuestResearch | None:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(GuestResearch)
        .where(GuestResearch.guest_id == guest_id)
        .order_by(GuestResearch.version.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def get_guest_research_by_id(db: Session, research_id: uuid.UUID) -> GuestResearch:
    research = db.get(GuestResearch, research_id)
    if research is None:
        raise GuestResearchNotFoundError(f"Guest research '{research_id}' not found")
    return research


def get_guest_research_by_id_for_user(
    db: Session, research_id: uuid.UUID, user_id: uuid.UUID
) -> GuestResearch:
    research = get_guest_research_by_id(db, research_id)
    if research.guest.created_by != user_id:
        raise GuestResearchNotFoundError(f"Guest research '{research_id}' not found")
    return research
