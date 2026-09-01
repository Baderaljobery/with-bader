import unittest

from app.database.session import SessionLocal
from app.schemas.guest import GuestCreate
from app.schemas.question import QuestionCreate
from app.services import question_service, question_version_service
from app.services.guest_service import create_guest, delete_guest
from app.services.question_improvement_service import (
    QuestionImprovementNoChangeError,
    accept_question_improvement,
)


class AcceptQuestionImprovementTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Improvement Service Test Guest"))

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_accept_updates_question_text_and_source(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Original question text?", source="manual")
        )

        updated = accept_question_improvement(
            self.db, question.id, "Improved question text, right?"
        )

        self.assertEqual(updated.text_, "Improved question text, right?")
        self.assertEqual(updated.source, "ai_improved")

    def test_accept_creates_two_historical_versions(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Original question text?", source="manual")
        )

        accept_question_improvement(self.db, question.id, "Improved question text?")

        versions = question_version_service.get_question_versions(self.db, question.id)
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0].version, 1)
        self.assertEqual(versions[0].text_, "Original question text?")
        self.assertEqual(versions[0].source, "manual")
        self.assertEqual(versions[1].version, 2)
        self.assertEqual(versions[1].text_, "Improved question text?")
        self.assertEqual(versions[1].source, "ai_improved")

    def test_original_text_remains_recoverable_after_accept(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Recoverable original?", source="manual")
        )
        accept_question_improvement(self.db, question.id, "New improved wording?")

        versions = question_version_service.get_question_versions(self.db, question.id)
        original_version = versions[0]
        self.assertEqual(original_version.text_, "Recoverable original?")

    def test_preserved_version_keeps_manual_source(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Manual one?", source="manual")
        )
        accept_question_improvement(self.db, question.id, "Manual one, improved?")
        versions = question_version_service.get_question_versions(self.db, question.id)
        self.assertEqual(versions[0].source, "manual")

    def test_preserved_version_keeps_ai_generated_source(self):
        question = question_service.create_question(
            self.db,
            self.guest.id,
            QuestionCreate(text="AI generated one?", source="ai_generated"),
        )
        accept_question_improvement(self.db, question.id, "AI generated one, improved?")
        versions = question_version_service.get_question_versions(self.db, question.id)
        self.assertEqual(versions[0].source, "ai_generated")

    def test_double_accept_with_identical_text_raises(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Same text?", source="manual")
        )
        accept_question_improvement(self.db, question.id, "Improved text?")

        with self.assertRaises(QuestionImprovementNoChangeError):
            accept_question_improvement(self.db, question.id, "Improved text?")

    def test_no_duplicate_versions_created_on_rejected_double_accept(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Same text?", source="manual")
        )
        accept_question_improvement(self.db, question.id, "Improved text?")
        try:
            accept_question_improvement(self.db, question.id, "Improved text?")
        except QuestionImprovementNoChangeError:
            pass

        versions = question_version_service.get_question_versions(self.db, question.id)
        self.assertEqual(len(versions), 2)


if __name__ == "__main__":
    unittest.main()
