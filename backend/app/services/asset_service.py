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


def create_asset(db: Session, asset_in: AssetCreate, uploaded_by: uuid.UUID) -> Asset:
    if asset_in.guest_id is not None:
        get_guest_by_id(db, asset_in.guest_id)

    asset = Asset(**_to_model_data(asset_in.model_dump()), uploaded_by=uploaded_by)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_assets(
    db: Session,
    uploaded_by: uuid.UUID,
    guest_id: uuid.UUID | None = None,
    asset_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Asset]:
    """Always scoped: either to a specific guest (ownership of which the
    caller has already verified) or, with no guest_id, to the current
    user's own directly-uploaded assets - never "every asset in the
    database" (Part 9's "no accidentally public data APIs" applies here
    too, even though Assets isn't one of the explicitly-named domains)."""
    stmt = select(Asset)
    if guest_id is not None:
        stmt = stmt.where(Asset.guest_id == guest_id)
    else:
        stmt = stmt.where(Asset.uploaded_by == uploaded_by)
    if asset_type is not None:
        stmt = stmt.where(Asset.type == asset_type)
    stmt = stmt.order_by(Asset.created_at.desc()).offset(skip).limit(limit)

    return list(db.scalars(stmt).all())


def get_asset_by_id(db: Session, asset_id: uuid.UUID) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise AssetNotFoundError(f"Asset '{asset_id}' not found")
    return asset


def get_asset_by_id_for_user(db: Session, asset_id: uuid.UUID, user_id: uuid.UUID) -> Asset:
    asset = get_asset_by_id(db, asset_id)
    owns_via_guest = asset.guest_id is not None and asset.guest.created_by == user_id
    owns_directly = asset.guest_id is None and asset.uploaded_by == user_id
    if not (owns_via_guest or owns_directly):
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
