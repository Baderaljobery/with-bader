import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.guest_link import GuestLinkCreate, GuestLinkResponse, GuestLinkUpdate
from app.services import guest_link_service, guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/links", tags=["guest-links"])
detail_router = APIRouter(prefix="/api/guest-links", tags=["guest-links"])


@router.post("", response_model=GuestLinkResponse, status_code=status.HTTP_201_CREATED)
def create_guest_link(
    guest_id: uuid.UUID,
    link_in: GuestLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuestLinkResponse:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return guest_link_service.create_guest_link(db, guest_id, link_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[GuestLinkResponse])
def list_guest_links(
    guest_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GuestLinkResponse]:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return guest_link_service.get_guest_links(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{link_id}", response_model=GuestLinkResponse)
def get_guest_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuestLinkResponse:
    try:
        return guest_link_service.get_guest_link_by_id_for_user(db, link_id, current_user.id)
    except guest_link_service.GuestLinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{link_id}", response_model=GuestLinkResponse)
def update_guest_link(
    link_id: uuid.UUID,
    link_in: GuestLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GuestLinkResponse:
    try:
        guest_link_service.get_guest_link_by_id_for_user(db, link_id, current_user.id)
        return guest_link_service.update_guest_link(db, link_id, link_in)
    except guest_link_service.GuestLinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guest_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        guest_link_service.get_guest_link_by_id_for_user(db, link_id, current_user.id)
        guest_link_service.delete_guest_link(db, link_id)
    except guest_link_service.GuestLinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
