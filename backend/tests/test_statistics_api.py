import unittest
from datetime import date, timedelta

from app.database.session import SessionLocal
from app.schemas.content_draft import ContentDraftCreate
from app.schemas.design_generation import DesignCreateRequest, DesignSlideInput
from app.schemas.guest import GuestCreate, GuestUpdate
from app.schemas.guest_transcript import GuestTranscriptCreate
from app.services import content_service, design_service, guest_transcript_service
from app.services.guest_service import create_guest, delete_guest, update_guest
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


def _overview():
    response = client.get("/api/statistics/overview")
    assert response.status_code == 200
    return response.json()


class StatisticsApiTests(unittest.TestCase):
    """Every assertion here compares a *delta* (before vs. after creating a
    known fixture) rather than an absolute count - these tests run against
    the same shared dev database as the rest of the suite, which may
    already hold unrelated guests/content/designs from other tests or real
    usage."""

    def setUp(self):
        self.db = SessionLocal()
        self.guests = []

    def tearDown(self):
        for guest in self.guests:
            delete_guest(self.db, guest.id)
        self.db.close()

    def _make_guest(self, name="ضيف اختبار الإحصائيات"):
        guest = create_guest(self.db, GuestCreate(name=name), created_by=client.user_id)
        self.guests.append(guest)
        return guest

    def test_response_shape(self):
        body = _overview()
        self.assertIn("totals", body)
        self.assertIn("content_by_platform", body)
        self.assertIn("activity", body)
        for field in (
            "guests",
            "scheduled_interviews",
            "completed_interviews",
            "questions",
            "content_drafts",
            "approved_content",
            "designs",
            "design_slides",
        ):
            self.assertIn(field, body["totals"])
            self.assertIsInstance(body["totals"][field], int)

    def test_guest_total_increases_when_a_guest_is_created(self):
        before = _overview()["totals"]["guests"]
        self._make_guest()
        after = _overview()["totals"]["guests"]
        self.assertEqual(after, before + 1)

    def test_scheduled_interviews_counts_guests_with_a_schedule(self):
        before = _overview()["totals"]["scheduled_interviews"]
        guest = self._make_guest()
        # Not scheduled yet - must not count.
        self.assertEqual(_overview()["totals"]["scheduled_interviews"], before)

        update_guest(self.db, guest.id, GuestUpdate(interview_scheduled_at="2026-09-20T10:00:00"))
        self.assertEqual(_overview()["totals"]["scheduled_interviews"], before + 1)

    def test_completed_interviews_counts_guest_transcripts(self):
        before = _overview()["totals"]["completed_interviews"]
        guest = self._make_guest()
        guest_transcript_service.create_guest_transcript(
            self.db, guest.id, GuestTranscriptCreate(text="نص تجريبي للمقابلة.")
        )
        after = _overview()["totals"]["completed_interviews"]
        self.assertEqual(after, before + 1)

    def test_content_drafts_and_approved_content_and_platform_breakdown(self):
        before_totals = _overview()["totals"]
        before_platforms = {row["platform"]: row["count"] for row in _overview()["content_by_platform"]}

        guest = self._make_guest()
        draft1 = content_service.create_content_draft(
            self.db, guest.id, ContentDraftCreate(platform="linkedin", length="short", content="نص 1")
        )
        content_service.create_content_draft(
            self.db, guest.id, ContentDraftCreate(platform="x", length="short", content="نص 2")
        )
        content_service.approve_content_draft(self.db, draft1.id)

        after = _overview()
        self.assertEqual(after["totals"]["content_drafts"], before_totals["content_drafts"] + 2)
        self.assertEqual(after["totals"]["approved_content"], before_totals["approved_content"] + 1)

        after_platforms = {row["platform"]: row["count"] for row in after["content_by_platform"]}
        self.assertEqual(after_platforms["linkedin"], before_platforms.get("linkedin", 0) + 1)
        self.assertEqual(after_platforms["x"], before_platforms.get("x", 0) + 1)
        # All four canonical platforms always present, even at zero.
        self.assertEqual(set(after_platforms.keys()), {"linkedin", "x", "instagram", "general"})

    def test_design_and_design_slide_counts(self):
        before = _overview()["totals"]
        guest = self._make_guest()

        design_service.create_design_draft(
            self.db,
            guest.id,
            DesignCreateRequest(
                template_id="template-01",
                slide_count=2,
                slides=[
                    DesignSlideInput(index=1, role="cover", headline="عنوان", body_text=""),
                    DesignSlideInput(index=2, role="main_content", headline="عنوان رئيسي", body_text="شرح."),
                ],
                platform="linkedin",
            ),
        )

        after = _overview()["totals"]
        self.assertEqual(after["designs"], before["designs"] + 1)
        self.assertEqual(after["design_slides"], before["design_slides"] + 2)

    def test_activity_trend_has_no_gaps_over_the_last_30_days(self):
        activity = _overview()["activity"]
        self.assertEqual(len(activity), 30)

        expected_dates = [(date.today() - timedelta(days=offset)).isoformat() for offset in range(29, -1, -1)]
        actual_dates = [point["date"] for point in activity]
        self.assertEqual(actual_dates, expected_dates)
        for point in activity:
            self.assertIsInstance(point["count"], int)
            self.assertGreaterEqual(point["count"], 0)

    def test_activity_trend_reflects_a_guest_created_today(self):
        before = _overview()["activity"][-1]["count"]
        self._make_guest()
        after = _overview()["activity"][-1]["count"]
        self.assertEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
