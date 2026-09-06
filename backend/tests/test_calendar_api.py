import unittest

from app.database.session import SessionLocal
from app.schemas.guest import GuestCreate
from app.services.guest_service import create_guest, delete_guest
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


def _events(start: str, end: str) -> list[dict]:
    response = client.get("/api/calendar/events", params={"start": start, "end": end})
    assert response.status_code == 200
    return response.json()


def _event_for(events: list[dict], guest_id) -> dict | None:
    return next((event for event in events if event["guest_id"] == str(guest_id)), None)


class CalendarApiTests(unittest.TestCase):
    """Assertions look up a specific fixture's own guest_id within the
    response rather than assuming array position or an exact total count -
    this endpoint reads the same shared dev database real usage (and other
    tests) may already have scheduled interviews in."""

    def setUp(self):
        self.db = SessionLocal()
        self.guests = []

    def tearDown(self):
        for guest in self.guests:
            delete_guest(self.db, guest.id)
        self.db.close()

    def _make_guest(self, name, scheduled_at=None, location=None):
        guest = create_guest(
            self.db,
            GuestCreate(
                name=name,
                interview_scheduled_at=scheduled_at,
                interview_location=location,
            ),
            created_by=client.user_id,
        )
        self.guests.append(guest)
        return guest

    def test_only_guests_with_a_scheduled_interview_appear(self):
        unscheduled = self._make_guest("بلا موعد")
        scheduled = self._make_guest(
            "لديه موعد", scheduled_at="2026-09-10T14:30:00", location="مكتب With Bader"
        )

        events = _events("2026-09-01", "2026-09-30")
        self.assertIsNotNone(_event_for(events, scheduled.id))
        self.assertIsNone(_event_for(events, unscheduled.id))

    def test_event_shape_matches_the_scheduled_guest(self):
        guest = self._make_guest(
            "ضيف اختبار شكل الحدث", scheduled_at="2026-09-15T09:00:00", location="فرع الرياض"
        )

        event = _event_for(_events("2026-09-01", "2026-09-30"), guest.id)
        self.assertIsNotNone(event)
        self.assertEqual(event["id"], str(guest.id))
        self.assertEqual(event["guest_id"], str(guest.id))
        self.assertEqual(event["guest_name"], "ضيف اختبار شكل الحدث")
        self.assertEqual(event["date"], "2026-09-15")
        self.assertEqual(event["time"], "09:00")
        self.assertEqual(event["location"], "فرع الرياض")

    def test_events_outside_the_requested_range_are_excluded(self):
        guest = self._make_guest("ضيف خارج النطاق", scheduled_at="2026-10-01T10:00:00")

        events = _events("2026-09-01", "2026-09-30")
        self.assertIsNone(_event_for(events, guest.id))

    def test_end_before_start_is_rejected(self):
        response = client.get("/api/calendar/events", params={"start": "2026-09-30", "end": "2026-09-01"})
        self.assertEqual(response.status_code, 422)

    def test_missing_location_is_null_not_an_error(self):
        guest = self._make_guest("ضيف بدون موقع", scheduled_at="2026-09-20T11:00:00")

        event = _event_for(_events("2026-09-01", "2026-09-30"), guest.id)
        self.assertIsNotNone(event)
        self.assertIsNone(event["location"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
