import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookUpdate
from app.services.guest_service import get_guest_by_id


class NotebookNotFoundError(Exception):
    """Raised when a notebook does not exist."""


def create_notebook(db: Session, guest_id: uuid.UUID, notebook_in: NotebookCreate) -> Notebook:
    get_guest_by_id(db, guest_id)

    notebook = Notebook(guest_id=guest_id, title=notebook_in.title)
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


def get_notebooks(db: Session, guest_id: uuid.UUID) -> list[Notebook]:
    get_guest_by_id(db, guest_id)

    stmt = (
        select(Notebook).where(Notebook.guest_id == guest_id).order_by(Notebook.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def get_notebook_by_id(db: Session, notebook_id: uuid.UUID) -> Notebook:
    notebook = db.get(Notebook, notebook_id)
    if notebook is None:
        raise NotebookNotFoundError(f"Notebook '{notebook_id}' not found")
    return notebook


def update_notebook(db: Session, notebook_id: uuid.UUID, notebook_in: NotebookUpdate) -> Notebook:
    notebook = get_notebook_by_id(db, notebook_id)

    for field, value in notebook_in.model_dump(exclude_unset=True).items():
        setattr(notebook, field, value)

    db.commit()
    db.refresh(notebook)
    return notebook


def delete_notebook(db: Session, notebook_id: uuid.UUID) -> None:
    notebook = get_notebook_by_id(db, notebook_id)
    db.delete(notebook)
    db.commit()
