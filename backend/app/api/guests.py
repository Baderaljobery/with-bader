import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from app.services import guest_service

router = APIRouter(prefix="/api/guests", tags=["guests"])


@router.post("", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_db)) -> GuestResponse:
    try:
        return guest_service.create_guest(db, guest_in)
    except guest_service.DuplicateSlugError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("", response_model=list[GuestResponse])
def list_guests(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[GuestResponse]:
    return guest_service.get_guests(db, skip=skip, limit=limit)


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: uuid.UUID, db: Session = Depends(get_db)) -> GuestResponse:
    try:
        return guest_service.get_guest_by_id(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{guest_id}", response_model=GuestResponse)
def update_guest(
    guest_id: uuid.UUID, guest_in: GuestUpdate, db: Session = Depends(get_db)
) -> GuestResponse:
    try:
        return guest_service.update_guest(db, guest_id, guest_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except guest_service.DuplicateSlugError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{guest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest(guest_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        guest_service.delete_guest(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
