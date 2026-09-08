import unittest

from app.database.session import SessionLocal
from app.schemas.guest import GuestCreate
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import question_service
from app.services.guest_service import create_guest, delete_guest
from tests.db_test_helpers import create_test_owner, delete_test_owner


class ManualAnswerServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, GuestCreate(name="Answer Service Test Guest"), self.owner.id
        )
        self.question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    def test_manual_answer_create(self):
        updated = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="It was funding.")
        )
        self.assertEqual(updated.answer, "It was funding.")
        self.assertEqual(updated.answer_status, "answered")
        self.assertEqual(updated.answer_source, "manual")
        self.assertIsNotNone(updated.answer_updated_at)

    def test_manual_answer_edit(self):
        question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="First answer")
        )
        updated = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="Edited answer")
        )
        self.assertEqual(updated.answer, "Edited answer")
        self.assertEqual(updated.answer_source, "manual")

    def test_manual_answer_clear_with_null(self):
        question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="Some answer")
        )
        cleared = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer=None)
        )
        self.assertIsNone(cleared.answer)
        self.assertEqual(cleared.answer_status, "not_answered")
        self.assertIsNone(cleared.answer_source)

    def test_manual_answer_clear_with_blank_string(self):
        question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="Some answer")
        )
        cleared = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="   ")
        )
        self.assertIsNone(cleared.answer)
        self.assertEqual(cleared.answer_status, "not_answered")
        self.assertIsNone(cleared.answer_source)

    def test_spoken_question_updated_when_provided(self):
        updated = question_service.set_question_answer(
            self.db,
            self.question.id,
            QuestionAnswerUpdate(answer="Answer text", spoken_question="Rephrased spoken form?"),
        )
        self.assertEqual(updated.spoken_question, "Rephrased spoken form?")

    def test_spoken_question_untouched_when_omitted(self):
        question_service.set_question_answer(
            self.db,
            self.question.id,
            QuestionAnswerUpdate(answer="First", spoken_question="Original spoken form?"),
        )
        updated = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="Second")
        )
        self.assertEqual(updated.spoken_question, "Original spoken form?")

    def test_manual_answer_works_without_transcript_or_ai(self):
        """The manual answer endpoint must work completely independently -
        no GuestTranscript, no matcher call, no AI involvement at all."""
        updated = question_service.set_question_answer(
            self.db, self.question.id, QuestionAnswerUpdate(answer="Purely manual answer")
        )
        self.assertEqual(updated.answer_source, "manual")

    def test_answer_on_ai_generated_question_source_still_manual(self):
        ai_question = question_service.create_question(
            self.db,
            self.guest.id,
            QuestionCreate(text="AI-generated question?", source="ai_generated"),
        )
        updated = question_service.set_question_answer(
            self.db, ai_question.id, QuestionAnswerUpdate(answer="Manually answered")
        )
        self.assertEqual(updated.answer_source, "manual")
        self.assertEqual(updated.source, "ai_generated")  # question's own source untouched


if __name__ == "__main__":
    unittest.main()
