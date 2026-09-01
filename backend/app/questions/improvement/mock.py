from app.models.question import Question
from app.questions.improvement.base import QuestionImprover
from app.questions.improvement.models import (
    QuestionImprovementContext,
    QuestionImprovementOptions,
    QuestionImprovementResult,
)


class MockQuestionImprover(QuestionImprover):
    """Deterministic stand-in for a real LLM improver. Never invents facts -
    it only appends a generic, open-ended reflective clause to the original
    question. For tests and offline development."""

    provider_name = "mock"

    async def improve(
        self,
        question: Question,
        options: QuestionImprovementOptions,
        context: QuestionImprovementContext | None = None,
    ) -> QuestionImprovementResult:
        original = question.text_.strip()
        core = original.rstrip("؟?").strip()

        if options.language == "ar":
            improved = f"{core}، وكيف تعاملت مع ذلك؟"
        else:
            improved = f"{core}, and how did you deal with it?"

        changes = (
            ["Made the question more open-ended and conversational"]
            if improved != original
            else []
        )

        return QuestionImprovementResult(
            original_text=original,
            improved_text=improved,
            reason="Mock deterministic improvement for tests/offline development.",
            changes=changes,
        )
