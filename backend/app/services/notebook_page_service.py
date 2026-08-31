import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notebook_page import NotebookPage
from app.schemas.notebook_page import NotebookPageCreate, NotebookPageUpdate
from app.services.notebook_service import get_notebook_by_id


class NotebookPageNotFoundError(Exception):
    """Raised when a notebook page does not exist."""


def create_notebook_page(
    db: Session, notebook_id: uuid.UUID, page_in: NotebookPageCreate
) -> NotebookPage:
    get_notebook_by_id(db, notebook_id)

    page = NotebookPage(notebook_id=notebook_id, title=page_in.title, position=page_in.position)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


def get_notebook_pages(db: Session, notebook_id: uuid.UUID) -> list[NotebookPage]:
    get_notebook_by_id(db, notebook_id)

    stmt = (
        select(NotebookPage)
        .where(NotebookPage.notebook_id == notebook_id)
        .order_by(NotebookPage.position.asc())
    )
    return list(db.scalars(stmt).all())


def get_notebook_page_by_id(db: Session, page_id: uuid.UUID) -> NotebookPage:
    page = db.get(NotebookPage, page_id)
    if page is None:
        raise NotebookPageNotFoundError(f"Notebook page '{page_id}' not found")
    return page


def update_notebook_page(
    db: Session, page_id: uuid.UUID, page_in: NotebookPageUpdate
) -> NotebookPage:
    page = get_notebook_page_by_id(db, page_id)

    for field, value in page_in.model_dump(exclude_unset=True).items():
        setattr(page, field, value)

    db.commit()
    db.refresh(page)
    return page


def delete_notebook_page(db: Session, page_id: uuid.UUID) -> None:
    page = get_notebook_page_by_id(db, page_id)
    db.delete(page)
    db.commit()
