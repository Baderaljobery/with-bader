import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.asset import AssetCreate, AssetResponse, AssetType, AssetUpdate
from app.services import asset_service, guest_service

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)) -> AssetResponse:
    try:
        return asset_service.create_asset(db, asset_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[AssetResponse])
def list_assets(
    guest_id: uuid.UUID | None = None,
    type: AssetType | None = None,
    db: Session = Depends(get_db),
) -> list[AssetResponse]:
    return asset_service.get_assets(db, guest_id=guest_id, asset_type=type)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> AssetResponse:
    try:
        return asset_service.get_asset_by_id(db, asset_id)
    except asset_service.AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: uuid.UUID, asset_in: AssetUpdate, db: Session = Depends(get_db)
) -> AssetResponse:
    try:
        return asset_service.update_asset(db, asset_id, asset_in)
    except (asset_service.AssetNotFoundError, guest_service.GuestNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        asset_service.delete_asset(db, asset_id)
    except asset_service.AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
