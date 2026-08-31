import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from app.services import guest_service, notebook_service

router = APIRouter(prefix="/api/guests/{guest_id}/notebooks", tags=["notebooks"])
detail_router = APIRouter(prefix="/api/notebooks", tags=["notebooks"])


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
def create_notebook(
    guest_id: uuid.UUID, notebook_in: NotebookCreate, db: Session = Depends(get_db)
) -> NotebookResponse:
    try:
        return notebook_service.create_notebook(db, guest_id, notebook_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[NotebookResponse])
def list_notebooks(guest_id: uuid.UUID, db: Session = Depends(get_db)) -> list[NotebookResponse]:
    try:
        return notebook_service.get_notebooks(db, guest_id)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{notebook_id}", response_model=NotebookResponse)
def get_notebook(notebook_id: uuid.UUID, db: Session = Depends(get_db)) -> NotebookResponse:
    try:
        return notebook_service.get_notebook_by_id(db, notebook_id)
    except notebook_service.NotebookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{notebook_id}", response_model=NotebookResponse)
def update_notebook(
    notebook_id: uuid.UUID, notebook_in: NotebookUpdate, db: Session = Depends(get_db)
) -> NotebookResponse:
    try:
        return notebook_service.update_notebook(db, notebook_id, notebook_in)
    except notebook_service.NotebookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notebook(notebook_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        notebook_service.delete_notebook(db, notebook_id)
    except notebook_service.NotebookNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
