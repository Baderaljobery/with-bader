"""Mandatory security tests (Part 39-41 of the auth rework spec): User A
owns a guest and real data across every domain; User B must be denied
access to every single piece of it, and must never see it in scoped
lists/calendar/statistics. Every "denied" assertion expects 404 (or, for
plain list endpoints, an empty/filtered result) - never a 403 that would
confirm the resource exists for someone else.
"""

import unittest
import uuid

from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.block import BlockCreate
from app.schemas.content_draft import ContentDraftCreate
from app.schemas.design_generation import DesignCreateRequest, DesignSlideInput
from app.schemas.guest import GuestUpdate
from app.schemas.guest_link import GuestLinkCreate
from app.schemas.guest_research import GuestResearchCreate
from app.schemas.guest_transcript import GuestTranscriptCreate
from app.schemas.notebook import NotebookCreate
from app.schemas.notebook_page import NotebookPageCreate
from app.schemas.question import QuestionCreate
from app.services import (
    block_service,
    content_service,
    design_service,
    guest_link_service,
    guest_research_service,
    guest_service,
    guest_transcript_service,
    notebook_page_service,
    notebook_service,
    question_service,
)
from tests.auth_test_helpers import make_authenticated_client
from tests.db_test_helpers import make_guest_create

class CrossUserIsolationTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.client_a = make_authenticated_client("User A")
        self.client_b = make_authenticated_client("User B")

        self.guest = guest_service.create_guest(
            self.db, make_guest_create(name="ضيف المستخدم أ", interview_scheduled_at="2026-09-15T10:00:00"),
            created_by=self.client_a.user_id,
        )
        self.question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="سؤال خاص بالمستخدم أ")
        )
        self.research = guest_research_service.create_guest_research(
            self.db, self.guest.id, GuestResearchCreate(role_title="CEO")
        )
        self.transcript = guest_transcript_service.create_guest_transcript(
            self.db, self.guest.id, GuestTranscriptCreate(text="نص مقابلة سري.")
        )
        self.notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="دفتر أ"))
        self.page = notebook_page_service.create_notebook_page(
            self.db, self.notebook.id, NotebookPageCreate(title="صفحة", position=0)
        )
        self.block = block_service.create_block(
            self.db, self.page.id, BlockCreate(type="personal_note", content={"text": "ملاحظة خاصة"}, position=0)
        )
        self.content_draft = content_service.create_content_draft(
            self.db,
            self.guest.id,
            ContentDraftCreate(platform="linkedin", length="short", content="محتوى خاص بالمستخدم أ"),
        )
        self.design = design_service.create_design_draft(
            self.db,
            self.guest.id,
            DesignCreateRequest(
                template_id="template-01",
                slide_count=1,
                slides=[DesignSlideInput(index=1, role="main_content", headline="عنوان", body_text="")],
                platform="linkedin",
            ),
        )
        self.link = guest_link_service.create_guest_link(
            self.db, self.guest.id, GuestLinkCreate(label="لينكدإن", url="https://example.com/a")
        )

    def tearDown(self):
        for user_id in (self.client_a.user_id, self.client_b.user_id):
            user = self.db.get(User, user_id)
            if user is not None:
                self.db.delete(user)
        self.db.commit()
        self.db.close()

    # --- Guest itself ---

    def test_user_b_cannot_get_guest_a(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_patch_guest_a(self):
        response = self.client_b.patch(f"/api/guests/{self.guest.id}", json={"name": "اسم مزوّر"})
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_guest_a(self):
        response = self.client_b.delete(f"/api/guests/{self.guest.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_guest_list_never_includes_guest_a(self):
        response = self.client_b.get("/api/guests")
        self.assertEqual(response.status_code, 200)
        ids = [g["id"] for g in response.json()]
        self.assertNotIn(str(self.guest.id), ids)

    def test_guest_a_still_visible_to_user_a(self):
        response = self.client_a.get(f"/api/guests/{self.guest.id}")
        self.assertEqual(response.status_code, 200)

    # --- Questions (nested list + direct id) ---

    def test_user_b_cannot_list_guest_a_questions(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/questions")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_question_by_id(self):
        response = self.client_b.get(f"/api/questions/{self.question.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_patch_guest_a_question(self):
        response = self.client_b.patch(f"/api/questions/{self.question.id}", json={"text": "نص مزوّر"})
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_guest_a_question(self):
        response = self.client_b.delete(f"/api/questions/{self.question.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_set_answer_on_guest_a_question(self):
        response = self.client_b.patch(
            f"/api/questions/{self.question.id}/answer", json={"answer": "إجابة مزوّرة"}
        )
        self.assertEqual(response.status_code, 404)

    # --- Research ---

    def test_user_b_cannot_list_guest_a_research(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/research")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_research_by_id(self):
        response = self.client_b.get(f"/api/guest-research/{self.research.id}")
        self.assertEqual(response.status_code, 404)

    # --- Transcript ---

    def test_user_b_cannot_get_guest_a_transcript(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/transcript")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_patch_guest_a_transcript(self):
        response = self.client_b.patch(
            f"/api/guests/{self.guest.id}/transcript", json={"text": "نص مزوّر"}
        )
        self.assertEqual(response.status_code, 404)

    # --- Notebook / pages / blocks ---

    def test_user_b_cannot_list_guest_a_notebooks(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/notebooks")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_notebook_by_id(self):
        response = self.client_b.get(f"/api/notebooks/{self.notebook.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_notebook_page(self):
        response = self.client_b.get(f"/api/notebook-pages/{self.page.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_block(self):
        response = self.client_b.get(f"/api/blocks/{self.block.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_list_guest_a_notebook_blocks(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/notebook-blocks")
        self.assertEqual(response.status_code, 404)

    # --- Content ---

    def test_user_b_cannot_list_guest_a_content(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/content")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_content_by_id(self):
        response = self.client_b.get(f"/api/content/{self.content_draft.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_approve_guest_a_content(self):
        response = self.client_b.post(f"/api/content/{self.content_draft.id}/approve")
        self.assertEqual(response.status_code, 404)

    # --- Designs ---

    def test_user_b_cannot_list_guest_a_designs(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/designs")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_design_by_id(self):
        response = self.client_b.get(f"/api/designs/{self.design.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_update_guest_a_design_slide(self):
        response = self.client_b.patch(
            f"/api/designs/{self.design.id}/slides/1", json={"headline": "مزوّر"}
        )
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_call_dormant_legacy_design_generate_endpoint(self):
        """Part 37: even the dormant legacy image-generation endpoints must
        be ownership-checked."""
        response = self.client_b.post(f"/api/designs/{self.design.id}/generate")
        self.assertEqual(response.status_code, 404)

    # --- Guest links ---

    def test_user_b_cannot_list_guest_a_links(self):
        response = self.client_b.get(f"/api/guests/{self.guest.id}/links")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_get_guest_a_link_by_id(self):
        response = self.client_b.get(f"/api/guest-links/{self.link.id}")
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_guest_a_link(self):
        response = self.client_b.delete(f"/api/guest-links/{self.link.id}")
        self.assertEqual(response.status_code, 404)

    # --- Calendar / Statistics (Parts 15/16/40/41) ---

    def test_user_b_calendar_never_shows_guest_a_event(self):
        response = self.client_b.get(
            "/api/calendar/events", params={"start": "2026-09-01", "end": "2026-09-30"}
        )
        self.assertEqual(response.status_code, 200)
        guest_ids = [event["guest_id"] for event in response.json()]
        self.assertNotIn(str(self.guest.id), guest_ids)

    def test_user_a_calendar_does_show_guest_a_event(self):
        response = self.client_a.get(
            "/api/calendar/events", params={"start": "2026-09-01", "end": "2026-09-30"}
        )
        guest_ids = [event["guest_id"] for event in response.json()]
        self.assertIn(str(self.guest.id), guest_ids)

    def test_user_b_statistics_are_all_zero_and_exclude_user_a_data(self):
        response = self.client_b.get("/api/statistics/overview")
        self.assertEqual(response.status_code, 200)
        totals = response.json()["totals"]
        # A brand-new user with zero guests of their own - every total must
        # be exactly zero, never a global count that includes User A's data.
        self.assertEqual(totals["guests"], 0)
        self.assertEqual(totals["questions"], 0)
        self.assertEqual(totals["content_drafts"], 0)
        self.assertEqual(totals["designs"], 0)
        self.assertEqual(totals["design_slides"], 0)
        self.assertEqual(totals["completed_interviews"], 0)
        self.assertEqual(totals["scheduled_interviews"], 0)

    def test_user_a_statistics_reflect_their_own_data(self):
        response = self.client_a.get("/api/statistics/overview")
        totals = response.json()["totals"]
        self.assertGreaterEqual(totals["guests"], 1)
        self.assertGreaterEqual(totals["questions"], 1)
        self.assertGreaterEqual(totals["content_drafts"], 1)
        self.assertGreaterEqual(totals["designs"], 1)

if __name__ == "__main__":
    unittest.main()
