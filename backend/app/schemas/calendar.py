import uuid

from pydantic import BaseModel


class CalendarEventResponse(BaseModel):
    """A calendar "event" is just a guest with a scheduled interview -
    there is no separate events table (see app/models/guest.py). `id` is
    the guest's own id: with at most one scheduled interview per guest,
    the guest id already uniquely identifies the event."""

    id: uuid.UUID
    guest_id: uuid.UUID
    guest_name: str
    date: str
    time: str
    location: str | None = None
