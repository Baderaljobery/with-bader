from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.calendar import CalendarEventResponse
from app.services import calendar_service

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/events", response_model=list[CalendarEventResponse])
def list_calendar_events(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CalendarEventResponse]:
    """Scheduled interviews (guests with interview_scheduled_at set) whose
    date falls within [start, end] - only for guests the authenticated
    user owns (Part 15). Scheduling/rescheduling/canceling an interview is
    not a separate endpoint - the frontend uses the existing
    PATCH /api/guests/{guest_id} with interview_scheduled_at/
    interview_location (see backend/app/schemas/guest.py)."""
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="'end' must not be before 'start'"
        )
    return calendar_service.get_calendar_events(db, start, end, current_user.id)
