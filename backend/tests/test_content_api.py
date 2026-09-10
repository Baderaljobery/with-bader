import unittest

from app.api.content import _resolve_engine
from app.content.generation.engine import ContentGenerationEngine
from app.content.generation.mock import MockContentGenerator
from app.database.session import SessionLocal
from app.main import app

from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import content_service, question_service
from app.services.guest_service import create_guest, delete_guest
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client
from tests.db_test_helpers import make_guest_create

client = make_authenticated_client()

def _override_with_mock_engine():
    app.dependency_overrides[_resolve_engine] = lambda: ContentGenerationEngine(
        generator=MockContentGenerator()
    )

def _clear_overrides():
    app.dependency_overrides.pop(_resolve_engine, None)

def _give_guest_answered_context(db, guest_id):
    question = question_service.create_question(
        db, guest_id, QuestionCreate(text="What was your biggest challenge?")
    )
    question_service.set_question_answer(
        db, question.id, QuestionAnswerUpdate(answer="Funding was the hardest part.")
    )

class ContentGenerationApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, make_guest_create(name="Content Generation API Test Guest"), created_by=client.user_id)
        _override_with_mock_engine()

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_generate_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/guests/{fake_id}/content/generate",
            json={"platform": "linkedin", "length": "medium"},
        )
        self.assertEqual(response.status_code, 404)

    def test_generate_returns_409_for_insufficient_context(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/content/generate",
            json={"platform": "linkedin", "length": "medium"},
        )
        self.assertEqual(response.status_code, 409)

    def test_generate_does_not_persist_anything(self):
        _give_guest_answered_context(self.db, self.guest.id)
        before = content_service.get_content_drafts(self.db, self.guest.id)

        response = client.post(
            f"/api/guests/{self.guest.id}/content/generate",
            json={"platform": "linkedin", "length": "medium"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["ai_provider"], "mock")
        self.assertIn("answers", body["sources_used"])
        self.assertTrue(body["content"])

        after = content_service.get_content_drafts(self.db, self.guest.id)
        self.assertEqual(len(before), len(after))

    def test_generate_defaults_language_to_arabic(self):
        _give_guest_answered_context(self.db, self.guest.id)
        response = client.post(
            f"/api/guests/{self.guest.id}/content/generate",
            json={"platform": "x", "length": "short"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["language"], "ar")

    def test_generate_rejects_invalid_platform(self):
        _give_guest_answered_context(self.db, self.guest.id)
        response = client.post(
            f"/api/guests/{self.guest.id}/content/generate",
            json={"platform": "facebook", "length": "medium"},
        )
        self.assertEqual(response.status_code, 422)

    def test_generate_rejects_invalid_length(self):
        _give_guest_answered_context(self.db, self.guest.id)
        response = client.post(
            f"/api/guests/{self.guest.id}/content/generate",
            json={"platform": "linkedin", "length": "very_long"},
        )
        self.assertEqual(response.status_code, 422)

class ContentDraftCrudApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, make_guest_create(name="Content CRUD API Test Guest"), created_by=client.user_id)
        self.other_guest = create_guest(self.db, make_guest_create(name="Other Guest"), created_by=client.user_id)

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_guest(self.db, self.other_guest.id)
        self.db.close()

    def _create_draft(self, **overrides):
        payload = {
            "platform": "linkedin",
            "length": "medium",
            "content": "مسودة تجريبية للمحتوى.",
            "source_context": ["answers", "notebook"],
            "ai_provider": "mock",
            "ai_model": None,
        }
        payload.update(overrides)
        return client.post(f"/api/guests/{self.guest.id}/content", json=payload)

    def test_create_and_get_draft(self):
        response = self._create_draft()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["guest_id"], str(self.guest.id))

        fetched = client.get(f"/api/content/{body['id']}")
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["content"], "مسودة تجريبية للمحتوى.")

    def test_list_drafts_for_guest(self):
        self._create_draft()
        self._create_draft(platform="x", length="short")
        response = client.get(f"/api/guests/{self.guest.id}/content")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_update_draft_content_persists(self):
        created = self._create_draft().json()
        response = client.patch(
            f"/api/content/{created['id']}", json={"content": "نص محدث بعد التعديل اليدوي."}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "نص محدث بعد التعديل اليدوي.")

        refetched = client.get(f"/api/content/{created['id']}")
        self.assertEqual(refetched.json()["content"], "نص محدث بعد التعديل اليدوي.")

    def test_delete_draft(self):
        created = self._create_draft().json()
        response = client.delete(f"/api/content/{created['id']}")
        self.assertEqual(response.status_code, 204)

        fetched = client.get(f"/api/content/{created['id']}")
        self.assertEqual(fetched.status_code, 404)

    def test_approve_draft_persists_status(self):
        created = self._create_draft().json()
        self.assertEqual(created["status"], "draft")

        response = client.post(f"/api/content/{created['id']}/approve")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "approved")

        refetched = client.get(f"/api/content/{created['id']}")
        self.assertEqual(refetched.json()["status"], "approved")

    def test_guest_isolation_drafts_do_not_leak_across_guests(self):
        self._create_draft()
        other_response = client.get(f"/api/guests/{self.other_guest.id}/content")
        self.assertEqual(other_response.status_code, 200)
        self.assertEqual(other_response.json(), [])

    def test_create_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/guests/{fake_id}/content",
            json={"platform": "linkedin", "length": "medium", "content": "x"},
        )
        self.assertEqual(response.status_code, 404)

    def test_get_returns_404_for_unknown_content_id(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/content/{fake_id}")
        self.assertEqual(response.status_code, 404)

    def test_create_rejects_empty_content(self):
        response = self._create_draft(content="")
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()

def tearDownModule():
    cleanup_client_user(client)
