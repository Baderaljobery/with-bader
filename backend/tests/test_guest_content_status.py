import unittest

from app.database.session import SessionLocal
from app.main import app
from app.schemas.guest import GuestCreate
from app.services.guest_service import create_guest, delete_guest

from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


class GuestContentStatusTests(unittest.TestCase):
    """content_status is a simple 3-state field (not_started / in_progress /
    published) that is normally auto-derived from whether the guest has a
    scheduled interview, until the user explicitly overrides it - see
    guest_service.update_guest and guest_service._auto_content_status."""

    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="ضيف اختبار حالة المحتوى"), created_by=client.user_id)

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_new_guest_with_no_interview_is_not_started(self):
        response = client.get(f"/api/guests/{self.guest.id}")
        body = response.json()
        self.assertEqual(body["content_status"], "not_started")
        self.assertFalse(body["content_status_manual"])

    def test_scheduling_an_interview_automatically_sets_in_progress(self):
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00"},
        )
        body = response.json()
        self.assertEqual(body["content_status"], "in_progress")
        self.assertFalse(body["content_status_manual"])

    def test_removing_the_interview_automatically_returns_to_not_started(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00"},
        )
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": None},
        )
        body = response.json()
        self.assertEqual(body["content_status"], "not_started")
        self.assertFalse(body["content_status_manual"])

    def test_manual_published_survives_a_later_calendar_change(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00"},
        )
        manual_response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"content_status": "published"},
        )
        self.assertEqual(manual_response.json()["content_status"], "published")
        self.assertTrue(manual_response.json()["content_status_manual"])

        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-20T09:00:00"},
        )
        body = response.json()
        self.assertEqual(body["content_status"], "published")
        self.assertTrue(body["content_status_manual"])

    def test_manual_not_started_overrides_an_existing_interview(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00"},
        )
        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"content_status": "not_started"},
        )
        body = response.json()
        self.assertEqual(body["content_status"], "not_started")
        self.assertTrue(body["content_status_manual"])

    def test_resetting_to_automatic_recalculates_from_the_calendar(self):
        client.patch(
            f"/api/guests/{self.guest.id}",
            json={"interview_scheduled_at": "2026-09-12T13:00:00"},
        )
        client.patch(f"/api/guests/{self.guest.id}", json={"content_status": "published"})

        response = client.patch(
            f"/api/guests/{self.guest.id}",
            json={"content_status_manual": False},
        )
        body = response.json()
        self.assertFalse(body["content_status_manual"])
        # interview_scheduled_at is still set from the earlier PATCH, so the
        # automatic rule recalculates back to in_progress, not not_started.
        self.assertEqual(body["content_status"], "in_progress")


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
