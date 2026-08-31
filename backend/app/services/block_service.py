import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.block import Block
from app.schemas.block import BlockCreate, BlockUpdate
from app.services.notebook_page_service import get_notebook_page_by_id
from app.services.question_service import get_question_by_id


class BlockNotFoundError(Exception):
    """Raised when a block does not exist."""


def create_block(db: Session, page_id: uuid.UUID, block_in: BlockCreate) -> Block:
    get_notebook_page_by_id(db, page_id)

    if block_in.linked_question_id is not None:
        get_question_by_id(db, block_in.linked_question_id)

    block = Block(page_id=page_id, **block_in.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_blocks(db: Session, page_id: uuid.UUID) -> list[Block]:
    get_notebook_page_by_id(db, page_id)

    stmt = select(Block).where(Block.page_id == page_id).order_by(Block.position.asc())
    return list(db.scalars(stmt).all())


def get_block_by_id(db: Session, block_id: uuid.UUID) -> Block:
    block = db.get(Block, block_id)
    if block is None:
        raise BlockNotFoundError(f"Block '{block_id}' not found")
    return block


def update_block(db: Session, block_id: uuid.UUID, block_in: BlockUpdate) -> Block:
    block = get_block_by_id(db, block_id)

    updates = block_in.model_dump(exclude_unset=True)
    if updates.get("linked_question_id") is not None:
        get_question_by_id(db, updates["linked_question_id"])

    for field, value in updates.items():
        setattr(block, field, value)

    db.commit()
    db.refresh(block)
    return block


def delete_block(db: Session, block_id: uuid.UUID) -> None:
    block = get_block_by_id(db, block_id)
    db.delete(block)
    db.commit()
