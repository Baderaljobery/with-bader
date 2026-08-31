import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.notebook_page import (
    NotebookPageCreate,
    NotebookPageResponse,
    NotebookPageUpdate,
)
from app.services import notebook_page_service, notebook_service

router = APIRouter(prefix="/api/notebooks/{notebook_id}/pages", tags=["notebook-pages"])
detail_router = APIRouter(prefix="/api/notebook-pages", tags=["notebook-pages"])


@router.post("", response_model=NotebookPageResponse, status_code=status.HTTP_201_CREATED)
def create_notebook_page(
    notebook_id: uuid.UUID, page_in: NotebookPageCreate, db: Session = Depends(get_db)
) -> NotebookPageResponse:
    try:
        return notebook_page_service.create_notebook_page(db, notebook_id, page_in)
    except notebook_service.NotebookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[NotebookPageResponse])
def list_notebook_pages(
    notebook_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[NotebookPageResponse]:
    try:
        return notebook_page_service.get_notebook_pages(db, notebook_id)
    except notebook_service.NotebookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{page_id}", response_model=NotebookPageResponse)
def get_notebook_page(page_id: uuid.UUID, db: Session = Depends(get_db)) -> NotebookPageResponse:
    try:
        return notebook_page_service.get_notebook_page_by_id(db, page_id)
    except notebook_page_service.NotebookPageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{page_id}", response_model=NotebookPageResponse)
def update_notebook_page(
    page_id: uuid.UUID, page_in: NotebookPageUpdate, db: Session = Depends(get_db)
) -> NotebookPageResponse:
    try:
        return notebook_page_service.update_notebook_page(db, page_id, page_in)
    except notebook_page_service.NotebookPageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notebook_page(page_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        notebook_page_service.delete_notebook_page(db, page_id)
    except notebook_page_service.NotebookPageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
