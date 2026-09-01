import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest_transcript import GuestTranscript
from app.schemas.guest_transcript import GuestTranscriptCreate
from app.services.guest_service import get_guest_by_id


class GuestTranscriptNotFoundError(Exception):
    """Raised when a guest has no transcript yet."""


class GuestTranscriptAlreadyExistsError(Exception):
    """Raised when a transcript already exists and replace_existing was not
    requested - each Guest has exactly one interview/transcript."""


def get_guest_transcript(db: Session, guest_id: uuid.UUID) -> GuestTranscript | None:
    get_guest_by_id(db, guest_id)
    stmt = select(GuestTranscript).where(GuestTranscript.guest_id == guest_id)
    return db.scalars(stmt).first()


def get_guest_transcript_or_raise(db: Session, guest_id: uuid.UUID) -> GuestTranscript:
    transcript = get_guest_transcript(db, guest_id)
    if transcript is None:
        raise GuestTranscriptNotFoundError(f"Guest '{guest_id}' has no transcript yet")
    return transcript


def create_guest_transcript(
    db: Session,
    guest_id: uuid.UUID,
    transcript_in: GuestTranscriptCreate,
    replace_existing: bool = False,
) -> GuestTranscript:
    get_guest_by_id(db, guest_id)
    existing = get_guest_transcript(db, guest_id)

    if existing is not None and not replace_existing:
        raise GuestTranscriptAlreadyExistsError(
            f"Guest '{guest_id}' already has a transcript - pass "
            "replace_existing=true to replace it"
        )

    if existing is not None:
        existing.text_ = transcript_in.text
        existing.stt_provider = transcript_in.stt_provider
        existing.stt_model = transcript_in.stt_model
        db.commit()
        db.refresh(existing)
        return existing

    transcript = GuestTranscript(
        guest_id=guest_id,
        text_=transcript_in.text,
        stt_provider=transcript_in.stt_provider,
        stt_model=transcript_in.stt_model,
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def update_guest_transcript_text(db: Session, guest_id: uuid.UUID, text: str) -> GuestTranscript:
    """Manual correction only - deliberately does NOT re-run answer
    matching. The caller re-runs POST /match-answers explicitly if wanted."""
    transcript = get_guest_transcript_or_raise(db, guest_id)
    transcript.text_ = text
    db.commit()
    db.refresh(transcript)
    return transcript
