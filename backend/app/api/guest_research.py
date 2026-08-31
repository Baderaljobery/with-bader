import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.guest_research import GuestResearchCreate, GuestResearchResponse
from app.services import guest_research_service, guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/research", tags=["guest-research"])
detail_router = APIRouter(prefix="/api/guest-research", tags=["guest-research"])


@router.post("", response_model=GuestResearchResponse, status_code=status.HTTP_201_CREATED)
def create_guest_research(
    guest_id: uuid.UUID, research_in: GuestResearchCreate, db: Session = Depends(get_db)
) -> GuestResearchResponse:
    try:
        return guest_research_service.create_guest_research(db, guest_id, research_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[GuestResearchResponse])
def list_guest_research(
    guest_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[GuestResearchResponse]:
    try:
        return guest_research_service.get_guest_research_history(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/latest", response_model=GuestResearchResponse)
def get_latest_guest_research(
    guest_id: uuid.UUID, db: Session = Depends(get_db)
) -> GuestResearchResponse:
    try:
        research = guest_research_service.get_latest_guest_research(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if research is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No research found for guest '{guest_id}'",
        )
    return research


@detail_router.get("/{research_id}", response_model=GuestResearchResponse)
def get_guest_research(
    research_id: uuid.UUID, db: Session = Depends(get_db)
) -> GuestResearchResponse:
    try:
        return guest_research_service.get_guest_research_by_id(db, research_id)
    except guest_research_service.GuestResearchNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
