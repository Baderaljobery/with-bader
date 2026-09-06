import unittest

from app.database.session import SessionLocal
from app.main import app
from app.schemas.guest import GuestCreate
from app.services.guest_service import create_guest, delete_guest

from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


class GuestInterviewScheduleTests(unittest.TestCase):
    """Scheduling/rescheduling/canceling a guest's interview reuses the
    existing PATCH /api/guests/{guest_id} endpoint - no new write endpoint
    was added for the Calendar feature (see app/api/calendar.py)."""

    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="ضيف اختبار الجدولة"), created_by=client.user_id)

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_new_guest_has_no_scheduled_interview(self):
        response = client.get(f"/api/guests/{self.guest.id}")
        body = response.json()
        self.assertIsNone(body["interview_scheduled_at"])
        self.assertIsNone(body["interview_location"])

    def test_patch_can_schedule_an_interview(self):
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00", "interview_location": "مكتب جدة"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["interview_scheduled_at"], "2026-09-12T13:00:00")
        self.assertEqual(body["interview_location"], "مكتب جدة")

    def test_patch_can_reschedule(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00", "interview_location": "مكتب جدة"},
        )
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-14T10:00:00"},
        )
        body = response.json()
        self.assertEqual(body["interview_scheduled_at"], "2026-09-14T10:00:00")
        # Location untouched by a PATCH that didn't mention it.
        self.assertEqual(body["interview_location"], "مكتب جدة")

    def test_patch_can_cancel_the_scheduled_interview(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00", "interview_location": "مكتب جدة"},
        )
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": None, "interview_location": None},
        )
        body = response.json()
        self.assertIsNone(body["interview_scheduled_at"])
        self.assertIsNone(body["interview_location"])


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
