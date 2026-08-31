import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.guest_service import get_guest_by_id


class AssetNotFoundError(Exception):
    """Raised when an asset does not exist."""


def _to_model_data(data: dict) -> dict:
    if "metadata" in data:
        data["metadata_"] = data.pop("metadata")
    return data


def create_asset(db: Session, asset_in: AssetCreate) -> Asset:
    if asset_in.guest_id is not None:
        get_guest_by_id(db, asset_in.guest_id)

    asset = Asset(**_to_model_data(asset_in.model_dump()))
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_assets(
    db: Session, guest_id: uuid.UUID | None = None, asset_type: str | None = None
) -> list[Asset]:
    stmt = select(Asset)
    if guest_id is not None:
        stmt = stmt.where(Asset.guest_id == guest_id)
    if asset_type is not None:
        stmt = stmt.where(Asset.type == asset_type)
    stmt = stmt.order_by(Asset.created_at.desc())

    return list(db.scalars(stmt).all())


def get_asset_by_id(db: Session, asset_id: uuid.UUID) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise AssetNotFoundError(f"Asset '{asset_id}' not found")
    return asset


def update_asset(db: Session, asset_id: uuid.UUID, asset_in: AssetUpdate) -> Asset:
    asset = get_asset_by_id(db, asset_id)

    updates = _to_model_data(asset_in.model_dump(exclude_unset=True))
    if updates.get("guest_id") is not None:
        get_guest_by_id(db, updates["guest_id"])

    for field, value in updates.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id: uuid.UUID) -> None:
    asset = get_asset_by_id(db, asset_id)
    db.delete(asset)
    db.commit()
