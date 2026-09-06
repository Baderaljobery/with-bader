import uuid
from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.guest import Guest
from app.schemas.calendar import CalendarEventResponse


def get_calendar_events(
    db: Session, start: date, end: date, user_id: uuid.UUID
) -> list[CalendarEventResponse]:
    """Guests with a scheduled interview whose date falls within
    [start, end] (inclusive on both ends - the caller passes the exact
    first/last visible day of the calendar grid it's rendering), scoped to
    the authenticated user's own guests only."""
    range_start = datetime.combine(start, time.min)
    range_end = datetime.combine(end, time.max)

    stmt = (
        select(Guest)
        .where(
            Guest.created_by == user_id,
            Guest.interview_scheduled_at.is_not(None),
            Guest.interview_scheduled_at >= range_start,
            Guest.interview_scheduled_at <= range_end,
        )
        .order_by(Guest.interview_scheduled_at.asc())
    )
    guests = db.scalars(stmt).all()

    return [
        CalendarEventResponse(
            id=guest.id,
            guest_id=guest.id,
            guest_name=guest.name,
            date=guest.interview_scheduled_at.date().isoformat(),
            time=guest.interview_scheduled_at.strftime("%H:%M"),
            location=guest.interview_location,
        )
        for guest in guests
    ]
