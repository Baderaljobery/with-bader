import unittest

from app.database.session import SessionLocal
from app.interview_intelligence.base import QuestionAnswerMatcher
from app.interview_intelligence.models import (
    MatchedAnswer,
    QuestionAnswerMatchResult,
    QuestionContext,
)
from app.interview_intelligence.service import InterviewIntelligenceService
from app.schemas.guest import GuestCreate
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import question_service
from app.services.guest_service import create_guest, delete_guest


class _ScriptedMatcher(QuestionAnswerMatcher):
    """Returns exactly the matches given, keyed by ref - lets tests control
    precisely what the "AI" claims without needing a real Groq call."""

    provider_name = "scripted"

    def __init__(self, matches: list[MatchedAnswer]):
        self._matches = matches
        self.received_questions: list[QuestionContext] = []

    async def match(self, transcript, questions):
        self.received_questions = questions
        return QuestionAnswerMatchResult(matches=self._matches, raw_ai_response=None)


class InterviewIntelligenceServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Matching Service Test Guest"))

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    async def test_confident_answered_match_is_auto_saved(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        matcher = _ScriptedMatcher(
            [
                MatchedAnswer(
                    question_ref="Q1",
                    spoken_question="وش أصعب شي واجهته؟",
                    answer="كانت مشكلة التمويل.",
                    status="answered",
                    confidence=0.9,
                )
            ]
        )
        service = InterviewIntelligenceService(matcher=matcher)

        outcomes = await service.match_and_apply(self.db, self.guest.id, "transcript text")

        [outcome] = outcomes
        self.assertEqual(outcome.answer, "كانت مشكلة التمويل.")
        self.assertEqual(outcome.answer_status, "answered")
        self.assertEqual(outcome.answer_source, "ai_extracted")
        self.assertEqual(outcome.spoken_question, "وش أصعب شي واجهته؟")

        refreshed = question_service.get_question_by_id(self.db, question.id)
        self.assertEqual(refreshed.answer_source, "ai_extracted")

    async def test_uncertain_match_not_auto_saved_as_active_answer(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        matcher = _ScriptedMatcher(
            [
                MatchedAnswer(
                    question_ref="Q1",
                    answer="maybe this is about it",
                    status="uncertain",
                    confidence=0.4,
                )
            ]
        )
        service = InterviewIntelligenceService(matcher=matcher)

        outcomes = await service.match_and_apply(self.db, self.guest.id, "transcript text")

        [outcome] = outcomes
        self.assertEqual(outcome.answer_status, "uncertain")
        # The DB itself must NOT have the candidate persisted as the answer.
        refreshed = question_service.get_question_by_id(self.db, outcome.question.id)
        self.assertIsNone(refreshed.answer)
        self.assertNotEqual(refreshed.answer_source, "ai_extracted")

    async def test_answered_below_confidence_threshold_not_auto_saved(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        matcher = _ScriptedMatcher(
            [
                MatchedAnswer(
                    question_ref="Q1",
                    answer="low confidence answer",
                    status="answered",
                    confidence=0.5,  # below default 0.75 threshold
                )
            ]
        )
        service = InterviewIntelligenceService(matcher=matcher)

        outcomes = await service.match_and_apply(self.db, self.guest.id, "transcript text")

        refreshed = question_service.get_question_by_id(self.db, outcomes[0].question.id)
        self.assertIsNone(refreshed.answer)

    async def test_not_answered_remains_empty(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="A question never asked")
        )
        matcher = _ScriptedMatcher([])  # no matches at all for Q1
        service = InterviewIntelligenceService(matcher=matcher)

        outcomes = await service.match_and_apply(self.db, self.guest.id, "unrelated transcript")

        [outcome] = outcomes
        self.assertIsNone(outcome.answer)
        self.assertEqual(outcome.answer_status, "not_answered")

    async def test_manual_answer_never_overwritten_by_match_rerun(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        question_service.set_question_answer(
            self.db, question.id, QuestionAnswerUpdate(answer="My manually typed answer")
        )

        matcher = _ScriptedMatcher(
            [
                MatchedAnswer(
                    question_ref="Q1",
                    answer="a completely different AI-found answer",
                    status="answered",
                    confidence=0.99,
                )
            ]
        )
        service = InterviewIntelligenceService(matcher=matcher)

        outcomes = await service.match_and_apply(self.db, self.guest.id, "transcript text")

        [outcome] = outcomes
        self.assertEqual(outcome.answer, "My manually typed answer")
        self.assertEqual(outcome.answer_source, "manual")

        refreshed = question_service.get_question_by_id(self.db, question.id)
        self.assertEqual(refreshed.answer, "My manually typed answer")
        self.assertEqual(refreshed.answer_source, "manual")

    async def test_ai_extracted_answer_may_be_replaced_on_rerun(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        first_matcher = _ScriptedMatcher(
            [MatchedAnswer(question_ref="Q1", answer="first AI answer", status="answered", confidence=0.9)]
        )
        await InterviewIntelligenceService(matcher=first_matcher).match_and_apply(
            self.db, self.guest.id, "transcript v1"
        )
        refreshed = question_service.get_question_by_id(self.db, question.id)
        self.assertEqual(refreshed.answer, "first AI answer")

        second_matcher = _ScriptedMatcher(
            [MatchedAnswer(question_ref="Q1", answer="updated AI answer", status="answered", confidence=0.9)]
        )
        outcomes = await InterviewIntelligenceService(matcher=second_matcher).match_and_apply(
            self.db, self.guest.id, "transcript v2"
        )

        self.assertEqual(outcomes[0].answer, "updated AI answer")
        refreshed_again = question_service.get_question_by_id(self.db, question.id)
        self.assertEqual(refreshed_again.answer, "updated AI answer")

    async def test_unmatched_saved_questions_remain_untouched_and_empty(self):
        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Asked question"))
        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Never asked question"))

        matcher = _ScriptedMatcher(
            [MatchedAnswer(question_ref="Q1", answer="found it", status="answered", confidence=0.9)]
        )
        outcomes = await InterviewIntelligenceService(matcher=matcher).match_and_apply(
            self.db, self.guest.id, "transcript"
        )

        outcomes_by_text = {o.question.text_: o for o in outcomes}
        self.assertEqual(outcomes_by_text["Asked question"].answer_status, "answered")
        self.assertEqual(outcomes_by_text["Never asked question"].answer_status, "not_answered")
        self.assertIsNone(outcomes_by_text["Never asked question"].answer)

    async def test_stable_local_refs_assigned_in_position_order(self):
        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="First", position=0))
        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Second", position=1))
        matcher = _ScriptedMatcher([])
        await InterviewIntelligenceService(matcher=matcher).match_and_apply(
            self.db, self.guest.id, "transcript"
        )
        self.assertEqual([q.ref for q in matcher.received_questions], ["Q1", "Q2"])
        self.assertEqual([q.text for q in matcher.received_questions], ["First", "Second"])

    async def test_transcript_too_long_raises_clear_error(self):
        from app.core.config import settings
        from app.interview_intelligence.base import InterviewMatcherTranscriptTooLongError

        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Q"))
        original_limit = settings.interview_matcher_max_transcript_chars
        settings.interview_matcher_max_transcript_chars = 10
        try:
            matcher = _ScriptedMatcher([])
            with self.assertRaises(InterviewMatcherTranscriptTooLongError):
                await InterviewIntelligenceService(matcher=matcher).match_and_apply(
                    self.db, self.guest.id, "this transcript is definitely too long"
                )
        finally:
            settings.interview_matcher_max_transcript_chars = original_limit


if __name__ == "__main__":
    unittest.main()
