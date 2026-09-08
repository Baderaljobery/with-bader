import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.pagination import PaginationParams
from app.database.session import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionAnswerUpdate,
    QuestionCreate,
    QuestionResponse,
    QuestionSource,
    QuestionStatus,
    QuestionUpdate,
)
from app.services import guest_service, question_service

router = APIRouter(prefix="/api/guests/{guest_id}/questions", tags=["questions"])
detail_router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("", response_model=QuestionResponse, status_code=http_status.HTTP_201_CREATED)
def create_question(
    guest_id: uuid.UUID,
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return question_service.create_question(db, guest_id, question_in)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[QuestionResponse])
def list_questions(
    guest_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    status: QuestionStatus | None = None,
    source: QuestionSource | None = None,
    topic: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QuestionResponse]:
    try:
        guest_service.get_guest_by_id_for_user(db, guest_id, current_user.id)
        return question_service.get_questions(
            db,
            guest_id,
            status=status,
            source=source,
            topic=topic,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    try:
        return question_service.get_question_by_id_for_user(db, question_id, current_user.id)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: uuid.UUID,
    question_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    try:
        question_service.get_question_by_id_for_user(db, question_id, current_user.id)
        return question_service.update_question(db, question_id, question_in)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.delete("/{question_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        question_service.get_question_by_id_for_user(db, question_id, current_user.id)
        question_service.delete_question(db, question_id)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.patch("/{question_id}/answer", response_model=QuestionResponse)
def set_question_answer(
    question_id: uuid.UUID,
    answer_in: QuestionAnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionResponse:
    """Manual answer entry/edit/clear - works independently of AI, and
    always wins over any AI-extracted answer (see
    app/interview_intelligence/service.py's manual-protection rule)."""
    try:
        question_service.get_question_by_id_for_user(db, question_id, current_user.id)
        return question_service.set_question_answer(db, question_id, answer_in)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
