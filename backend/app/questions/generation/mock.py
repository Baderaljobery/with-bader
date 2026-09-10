from app.models.guest import Guest
from app.questions.generation.base import QuestionGenerator
from app.questions.generation.models import (
    ExistingQuestionItem,
    GeneratedQuestionItem,
    QuestionGenerationOptions,
    QuestionGenerationResult,
    ResearchContextItem,
)
from app.questions.generation.similarity import normalize_question_text

_ITEM_TYPE_TO_CATEGORY = {
    "career_history": "career_journey",
    "education": "education",
    "achievement": "achievement",
    "project": "project",
    "interesting_event": "turning_point",
    "public_appearance": "public_appearance",
    "topic": "expertise",
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
        existing_questions: list[ExistingQuestionItem] | None = None,
    ) -> QuestionGenerationResult:
        questions: list[GeneratedQuestionItem] = []
        existing_texts = {
            normalize_question_text(item.text) for item in (existing_questions or [])
        }

        if guest.job_title:
            text = f"What first drew you to work as a {guest.job_title}?"
            if normalize_question_text(text) not in existing_texts:
                questions.append(
                    GeneratedQuestionItem(
                    text=text,
                    category="career_journey",
                    intent_summary=f"motivation to work as {guest.job_title}",
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
                    intent_summary=f"explore {item.fact}",
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
