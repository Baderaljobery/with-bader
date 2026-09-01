from app.models.guest import Guest
from app.questions.generation.base import QuestionGenerator
from app.questions.generation.models import (
    GeneratedQuestionItem,
    QuestionGenerationOptions,
    QuestionGenerationResult,
    ResearchContextItem,
)

_ITEM_TYPE_TO_CATEGORY = {
    "career_history": "career_journey",
    "achievement": "achievement",
    "project": "project",
    "interesting_event": "turning_point",
    "potential_interview_angle": "personal_perspective",
}


class MockQuestionGenerator(QuestionGenerator):
    """Deterministic stand-in for a real LLM question generator.

    Derives generic-but-safe questions only from guest fields and the
    research items it is given - never invents facts. For tests and offline
    development, mirroring MockResearchExtractor's role in the research layer.
    """

    provider_name = "mock"

    async def generate(
        self,
        guest: Guest,
        research_items: list[ResearchContextItem],
        options: QuestionGenerationOptions,
    ) -> QuestionGenerationResult:
        questions: list[GeneratedQuestionItem] = []

        if guest.job_title:
            questions.append(
                GeneratedQuestionItem(
                    text=f"What first drew you to work as a {guest.job_title}?",
                    category="career_journey",
                    priority="medium",
                )
            )

        for item in research_items:
            if len(questions) >= options.count:
                break
            questions.append(
                GeneratedQuestionItem(
                    text=f"Can you walk us through this: {item.fact}?",
                    category=_ITEM_TYPE_TO_CATEGORY.get(item.item_type, "career_journey"),
                    priority="medium",
                    research_item_ids=[item.id],
                    source_urls=list(item.source_urls),
                    follow_up_questions=(
                        ["What would you do differently today?"]
                        if options.include_followups
                        else []
                    ),
                )
            )

        return QuestionGenerationResult(questions=questions[: options.count], raw_ai_response=None)
