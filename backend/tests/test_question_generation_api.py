import unittest

from fastapi.testclient import TestClient

from app.api.question_generation import _resolve_engine
from app.database.session import SessionLocal
from app.main import app
from app.models.question import Question
from app.questions.generation.engine import QuestionGenerationEngine
from app.questions.generation.mock import MockQuestionGenerator
from app.schemas.guest import GuestCreate
from app.schemas.guest_research import GuestResearchCreate
from app.schemas.question import QuestionCreate
from app.services import guest_research_service, question_service
from app.services.guest_service import create_guest, delete_guest

client = TestClient(app)


def _override_with_mock_engine():
    app.dependency_overrides[_resolve_engine] = lambda: QuestionGenerationEngine(
        generator=MockQuestionGenerator()
    )


def _clear_overrides():
    app.dependency_overrides.pop(_resolve_engine, None)


class QuestionGenerationApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(
            self.db, GuestCreate(name="API Test Guest", job_title="CEO", company="Example Co")
        )
        _override_with_mock_engine()

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_generate_requires_research_first(self):
        response = client.post(f"/api/guests/{self.guest.id}/questions/generate", json={})
        self.assertEqual(response.status_code, 409)

    def test_generate_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/guests/{fake_id}/questions/generate", json={})
        self.assertEqual(response.status_code, 404)

    def test_generate_does_not_persist_questions(self):
        guest_research_service.create_guest_research(
            self.db,
            self.guest.id,
            GuestResearchCreate(
                achievements=[
                    {"title": "Founded Example Co", "source_urls": ["https://example.org/a"]}
                ]
            ),
        )
        before = question_service.get_questions(self.db, self.guest.id)

        response = client.post(
            f"/api/guests/{self.guest.id}/questions/generate",
            json={"count": 3, "language": "en", "include_followups": True},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["generator_provider"], "mock")
        self.assertGreater(len(body["questions"]), 0)

        after = question_service.get_questions(self.db, self.guest.id)
        self.assertEqual(len(before), len(after))

    def test_count_validation_rejects_over_max(self):
        guest_research_service.create_guest_research(
            self.db, self.guest.id, GuestResearchCreate()
        )
        response = client.post(
            f"/api/guests/{self.guest.id}/questions/generate", json={"count": 999}
        )
        self.assertEqual(response.status_code, 422)


class QuestionGenerationSaveApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Save Test Guest"))

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_save_creates_ai_generated_questions(self):
        response = client.post(
            f"/api/guests/{self.guest.id}/questions/generated/save",
            json={
                "questions": [
                    {"text": "Question one?", "topic": "career"},
                    {"text": "Question two?", "topic": "leadership"},
                    {"text": "Question three?", "topic": None},
                ]
            },
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["saved_count"], 3)
        for question in body["questions"]:
            self.assertEqual(question["source"], "ai_generated")
            self.assertEqual(question["status"], "draft")
            self.assertEqual(question["guest_id"], str(self.guest.id))

    def test_saved_questions_get_positions_after_existing(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Manual Q1", position=0)
        )
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Manual Q2", position=1)
        )

        response = client.post(
            f"/api/guests/{self.guest.id}/questions/generated/save",
            json={"questions": [{"text": "AI Q1"}, {"text": "AI Q2"}]},
        )
        self.assertEqual(response.status_code, 201)
        positions = [q["position"] for q in response.json()["questions"]]
        self.assertEqual(positions, [2, 3])

    def test_existing_manual_questions_are_not_modified(self):
        manual = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Untouched manual question", position=0)
        )
        manual_id = manual.id

        client.post(
            f"/api/guests/{self.guest.id}/questions/generated/save",
            json={"questions": [{"text": "New AI question"}]},
        )

        refreshed = self.db.get(Question, manual_id)
        self.assertEqual(refreshed.text_, "Untouched manual question")
        self.assertEqual(refreshed.source, "manual")
        self.assertEqual(refreshed.position, 0)

    def test_save_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/guests/{fake_id}/questions/generated/save",
            json={"questions": [{"text": "Orphan question"}]},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
