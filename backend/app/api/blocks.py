import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.block import BlockCreate, BlockResponse, BlockUpdate
from app.services import block_service, notebook_page_service, question_service

router = APIRouter(prefix="/api/notebook-pages/{page_id}/blocks", tags=["blocks"])
detail_router = APIRouter(prefix="/api/blocks", tags=["blocks"])


@router.post("", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    page_id: uuid.UUID, block_in: BlockCreate, db: Session = Depends(get_db)
) -> BlockResponse:
    try:
        return block_service.create_block(db, page_id, block_in)
    except notebook_page_service.NotebookPageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[BlockResponse])
def list_blocks(page_id: uuid.UUID, db: Session = Depends(get_db)) -> list[BlockResponse]:
    try:
        return block_service.get_blocks(db, page_id)
    except notebook_page_service.NotebookPageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{block_id}", response_model=BlockResponse)
def get_block(block_id: uuid.UUID, db: Session = Depends(get_db)) -> BlockResponse:
    try:
        return block_service.get_block_by_id(db, block_id)
    except block_service.BlockNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{block_id}", response_model=BlockResponse)
def update_block(
    block_id: uuid.UUID, block_in: BlockUpdate, db: Session = Depends(get_db)
) -> BlockResponse:
    try:
        return block_service.update_block(db, block_id, block_in)
    except block_service.BlockNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(block_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        block_service.delete_block(db, block_id)
    except block_service.BlockNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
