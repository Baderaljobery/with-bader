import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.block import Block
from app.models.notebook import Notebook
from app.models.notebook_page import NotebookPage
from app.schemas.block import BlockCreate, BlockUpdate
from app.services.guest_service import get_guest_by_id
from app.services.notebook_page_service import get_notebook_page_by_id
from app.services.question_service import get_question_by_id

# Text-like block types worth offering as Design Engine supporting context
# (same set Content Creation's context builder uses - see
# app/content/generation/context_builder.py / app/design_planning/context.py).
TEXT_BLOCK_TYPES = (
    "content_idea",
    "personal_note",
    "highlight",
    "quote",
    "question",
    "answer",
    "paragraph",
    "heading",
    "callout",
)


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


def get_blocks(
    db: Session, page_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Block]:
    get_notebook_page_by_id(db, page_id)

    stmt = (
        select(Block)
        .where(Block.page_id == page_id)
        .order_by(Block.position.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_block_by_id(db: Session, block_id: uuid.UUID) -> Block:
    block = db.get(Block, block_id)
    if block is None:
        raise BlockNotFoundError(f"Block '{block_id}' not found")
    return block


def get_block_by_id_for_user(db: Session, block_id: uuid.UUID, user_id: uuid.UUID) -> Block:
    block = get_block_by_id(db, block_id)
    if block.page.notebook.guest.created_by != user_id:
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


def get_text_blocks_for_guest(
    db: Session, guest_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Block]:
    """All text-like blocks across every notebook/page belonging to this
    guest, for the Design Engine's supporting-notebook-content picker (the
    user selects specific blocks manually - this just lists what's
    available, it never auto-includes anything)."""
    get_guest_by_id(db, guest_id)

    stmt = (
        select(Block)
        .join(NotebookPage, Block.page_id == NotebookPage.id)
        .join(Notebook, NotebookPage.notebook_id == Notebook.id)
        .where(Notebook.guest_id == guest_id, Block.type.in_(TEXT_BLOCK_TYPES))
        .order_by(Block.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def delete_block(db: Session, block_id: uuid.UUID) -> None:
    block = get_block_by_id(db, block_id)
    db.delete(block)
    db.commit()
