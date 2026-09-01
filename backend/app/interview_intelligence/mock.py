from app.interview_intelligence.base import QuestionAnswerMatcher
from app.interview_intelligence.models import (
    MatchedAnswer,
    QuestionAnswerMatchResult,
    QuestionContext,
)


class MockQuestionAnswerMatcher(QuestionAnswerMatcher):
    """Deterministic stand-in for a real LLM matcher: a saved question is
    considered "answered" only when its exact text appears (case-
    insensitively) inside the transcript - the "answer" is then the whole
    transcript. Never invents anything beyond what's literally present. For
    tests and offline development, mirroring MockQuestionGenerator's role.
    """

    provider_name = "mock"

    async def match(
        self, transcript: str, questions: list[QuestionContext]
    ) -> QuestionAnswerMatchResult:
        matches: list[MatchedAnswer] = []
        lowered_transcript = transcript.lower()

        for question in questions:
            if question.text.strip() and question.text.strip().lower() in lowered_transcript:
                matches.append(
                    MatchedAnswer(
                        question_ref=question.ref,
                        spoken_question=question.text,
                        answer=transcript.strip(),
                        status="answered",
                        confidence=1.0,
                    )
                )

        return QuestionAnswerMatchResult(matches=matches, raw_ai_response=None)
