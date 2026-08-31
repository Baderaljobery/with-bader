import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.question_version import QuestionVersionCreate, QuestionVersionResponse
from app.services import question_service, question_version_service

router = APIRouter(prefix="/api/questions/{question_id}/versions", tags=["question-versions"])
detail_router = APIRouter(prefix="/api/question-versions", tags=["question-versions"])


@router.post("", response_model=QuestionVersionResponse, status_code=status.HTTP_201_CREATED)
def create_question_version(
    question_id: uuid.UUID, version_in: QuestionVersionCreate, db: Session = Depends(get_db)
) -> QuestionVersionResponse:
    try:
        return question_version_service.create_question_version(db, question_id, version_in)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[QuestionVersionResponse])
def list_question_versions(
    question_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[QuestionVersionResponse]:
    try:
        return question_version_service.get_question_versions(db, question_id)
    except question_service.QuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@detail_router.get("/{version_id}", response_model=QuestionVersionResponse)
def get_question_version(
    version_id: uuid.UUID, db: Session = Depends(get_db)
) -> QuestionVersionResponse:
    try:
        return question_version_service.get_question_version_by_id(db, version_id)
    except question_version_service.QuestionVersionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
