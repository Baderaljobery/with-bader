import unittest
from unittest.mock import AsyncMock, patch

from app.api.question_improvement import _resolve_improver
from app.database.session import SessionLocal
from app.main import app
from app.questions.improvement.mock import MockQuestionImprover
from app.schemas.guest import GuestCreate
from app.schemas.question import QuestionCreate
from app.services import question_service, question_version_service
from app.services.guest_service import create_guest, delete_guest

from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


def _override_with_mock_improver():
    app.dependency_overrides[_resolve_improver] = lambda: MockQuestionImprover()


def _clear_overrides():
    app.dependency_overrides.pop(_resolve_improver, None)


class QuestionImprovementPreviewApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Improve API Test Guest"), created_by=client.user_id)
        self.question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        _override_with_mock_improver()

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_preview_returns_original_and_improved_text(self):
        response = client.post(
            f"/api/questions/{self.question.id}/improve", json={"language": "en"}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["original_text"], "What was your biggest challenge?")
        self.assertEqual(
            body["improved_text"],
            "What was your biggest challenge, and how did you deal with it?",
        )

    def test_preview_works_with_empty_body(self):
        response = client.post(f"/api/questions/{self.question.id}/improve")
        self.assertEqual(response.status_code, 200)

    def test_preview_does_not_modify_question_text(self):
        client.post(f"/api/questions/{self.question.id}/improve", json={"language": "en"})
        refreshed = question_service.get_question_by_id(self.db, self.question.id)
        self.assertEqual(refreshed.text_, "What was your biggest challenge?")
        self.assertEqual(refreshed.source, "manual")

    def test_preview_does_not_create_question_version(self):
        client.post(f"/api/questions/{self.question.id}/improve", json={"language": "en"})
        versions = question_version_service.get_question_versions(self.db, self.question.id)
        self.assertEqual(versions, [])

    def test_preview_returns_404_for_unknown_question(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/questions/{fake_id}/improve", json={"language": "en"})
        self.assertEqual(response.status_code, 404)

    def test_preview_works_without_guest_research(self):
        # No GuestResearch was created for self.guest - improvement must
        # still succeed with a None optional context.
        response = client.post(
            f"/api/questions/{self.question.id}/improve", json={"language": "en"}
        )
        self.assertEqual(response.status_code, 200)

    def test_exa_and_tavily_are_never_called_during_preview(self):
        with (
            patch(
                "app.research.providers.exa.ExaResearchSearchProvider.search",
                new_callable=AsyncMock,
            ) as exa_mock,
            patch(
                "app.research.providers.tavily.TavilyResearchSearchProvider.search",
                new_callable=AsyncMock,
            ) as tavily_mock,
        ):
            response = client.post(
                f"/api/questions/{self.question.id}/improve", json={"language": "en"}
            )
            self.assertEqual(response.status_code, 200)
            exa_mock.assert_not_called()
            tavily_mock.assert_not_called()

    def test_arabic_preview(self):
        arabic_question = question_service.create_question(
            self.db,
            self.guest.id,
            QuestionCreate(text="وش اكبر تحدي واجهته في حياتك المهنية"),
        )
        response = client.post(
            f"/api/questions/{arabic_question.id}/improve", json={"language": "ar"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["improved_text"].endswith("؟"))


class QuestionImprovementAcceptApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Improve Accept API Test Guest"), created_by=client.user_id)

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_accept_updates_question_and_returns_it(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Original text?")
        )
        response = client.post(
            f"/api/questions/{question.id}/improve/accept",
            json={"improved_text": "Improved text?"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["text"], "Improved text?")
        self.assertEqual(body["source"], "ai_improved")

    def test_accept_returns_404_for_unknown_question(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/questions/{fake_id}/improve/accept", json={"improved_text": "Whatever?"}
        )
        self.assertEqual(response.status_code, 404)

    def test_accept_rejects_identical_text_with_409(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Same text?")
        )
        response = client.post(
            f"/api/questions/{question.id}/improve/accept",
            json={"improved_text": "Same text?"},
        )
        self.assertEqual(response.status_code, 409)

    def test_accept_rejects_blank_text_with_422(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Original text?")
        )
        response = client.post(
            f"/api/questions/{question.id}/improve/accept", json={"improved_text": "   "}
        )
        self.assertEqual(response.status_code, 422)

    def test_accept_works_for_ai_generated_question(self):
        question = question_service.create_question(
            self.db,
            self.guest.id,
            QuestionCreate(text="AI generated question?", source="ai_generated"),
        )
        response = client.post(
            f"/api/questions/{question.id}/improve/accept",
            json={"improved_text": "AI generated question, improved?"},
        )
        self.assertEqual(response.status_code, 200)
        versions = question_version_service.get_question_versions(self.db, question.id)
        self.assertEqual(versions[0].source, "ai_generated")
        self.assertEqual(versions[1].source, "ai_improved")


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
