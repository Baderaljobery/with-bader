import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.interview_intelligence.base import (
    InterviewMatcherTranscriptTooLongError,
    QuestionAnswerMatcher,
)
from app.interview_intelligence.models import MatchedAnswer, QuestionContext
from app.models.question import Question
from app.services import guest_service, question_service


@dataclass
class QuestionMatchOutcome:
    """One question's post-match state. `question` always reflects what is
    now persisted. The other fields normally mirror `question`'s columns,
    EXCEPT for an "uncertain" outcome, where `answer`/`spoken_question` may
    carry a suggested value that was deliberately NOT written to the DB
    (preview-only, per the uncertain-match rule)."""

    question: Question
    spoken_question: str | None
    answer: str | None
    answer_status: str
    answer_source: str | None
    confidence: float | None


class InterviewIntelligenceService:
    """Orchestrates matching a transcript against a guest's saved questions
    and applying the manual-first persistence rule. Depends only on
    QuestionAnswerMatcher - never a concrete provider - and never touches
    Exa/Tavily or the search/research layer at all."""

    def __init__(self, matcher: QuestionAnswerMatcher) -> None:
        self._matcher = matcher

    async def match_and_apply(
        self, db: Session, guest_id: uuid.UUID, transcript: str
    ) -> list[QuestionMatchOutcome]:
        guest_service.get_guest_by_id(db, guest_id)

        max_chars = settings.interview_matcher_max_transcript_chars
        if len(transcript) > max_chars:
            raise InterviewMatcherTranscriptTooLongError(
                f"Transcript is {len(transcript)} characters, which exceeds the "
                f"configured matcher limit of {max_chars} characters "
                "(INTERVIEW_MATCHER_MAX_TRANSCRIPT_CHARS). Shorten the transcript or "
                "raise the limit for a higher-tier Groq plan."
            )

        questions = question_service.get_questions(db, guest_id)
        # A hard question-count cap is a much softer failure mode than
        # truncating the transcript (see the char-limit check above) - a
        # guest with more than this many saved questions is an edge case,
        # so the extra ones are simply not sent this run rather than
        # rejecting the whole request.
        bounded_questions = questions[: settings.interview_matcher_max_questions]

        contexts = [
            QuestionContext(ref=f"Q{index + 1}", question_id=str(question.id), text=question.text_)
            for index, question in enumerate(bounded_questions)
        ]

        result = await self._matcher.match(transcript, contexts)
        matches_by_ref = {match.question_ref: match for match in result.matches}
        ref_by_question_id = {context.question_id: context.ref for context in contexts}

        threshold = settings.interview_matcher_auto_save_confidence
        outcomes = [
            self._apply_match(question, matches_by_ref.get(ref_by_question_id.get(str(question.id))), threshold)
            for question in questions
        ]

        db.commit()
        for outcome in outcomes:
            db.refresh(outcome.question)

        return outcomes

    def _apply_match(
        self, question: Question, match: MatchedAnswer | None, threshold: float
    ) -> QuestionMatchOutcome:
        # Manual answers are authoritative - never touched by matching,
        # regardless of what this run's match says.
        if question.answer_source == "manual":
            return QuestionMatchOutcome(
                question=question,
                spoken_question=question.spoken_question,
                answer=question.answer,
                answer_status=question.answer_status,
                answer_source=question.answer_source,
                confidence=None,
            )

        # No match object at all means the transcript never addressed this
        # question this run - treated the same as an explicit not_answered
        # (see Part 25: never create a fake match).
        status = match.status if match is not None else "not_answered"
        confidence = match.confidence if match is not None else None
        spoken = match.spoken_question if match is not None else None
        answer_text = match.answer if match is not None else None

        if status == "answered" and answer_text and (confidence or 0.0) >= threshold:
            question_service.apply_answer_match(
                question,
                answer=answer_text,
                answer_status="answered",
                answer_source="ai_extracted",
                spoken_question=spoken,
            )
            return QuestionMatchOutcome(
                question=question,
                spoken_question=question.spoken_question,
                answer=question.answer,
                answer_status=question.answer_status,
                answer_source=question.answer_source,
                confidence=confidence,
            )

        if status == "not_answered":
            # ai_extracted (or empty) state is always refreshable - only
            # "manual" is protected, and that was already handled above.
            question_service.apply_answer_match(
                question,
                answer=None,
                answer_status="not_answered",
                answer_source=None,
                spoken_question=spoken,
            )
            return QuestionMatchOutcome(
                question=question,
                spoken_question=question.spoken_question,
                answer=question.answer,
                answer_status=question.answer_status,
                answer_source=question.answer_source,
                confidence=confidence,
            )

        # status == "uncertain", or "answered" below the auto-save
        # threshold: flag the question for review but do NOT persist the
        # candidate text as the active answer - only the flag is saved.
        question_service.apply_answer_match(
            question,
            answer=question.answer,
            answer_status="uncertain",
            answer_source=question.answer_source,
        )
        return QuestionMatchOutcome(
            question=question,
            spoken_question=spoken or question.spoken_question,
            answer=answer_text,
            answer_status="uncertain",
            answer_source=question.answer_source,
            confidence=confidence,
        )


def get_interview_intelligence_service() -> InterviewIntelligenceService:
    """Single wiring point for the matcher implementation. Swap via
    INTERVIEW_MATCHER_PROVIDER - InterviewIntelligenceService itself never
    changes."""
    from app.interview_intelligence.factory import build_question_answer_matcher

    return InterviewIntelligenceService(matcher=build_question_answer_matcher())
