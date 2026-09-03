from app.content.generation.base import ContentGenerator
from app.content.generation.models import (
    ContentContextItem,
    ContentGenerationOptions,
    ContentGenerationResult,
)
from app.models.guest import Guest


class MockContentGenerator(ContentGenerator):
    """Deterministic stand-in for a real LLM content generator. Derives a
    minimal, safe draft only from the guest's name and the supplied context
    items - never invents facts. For tests and offline development,
    mirroring MockQuestionGenerator's role in the question-generation layer.
    """

    provider_name = "mock"

    async def generate(
        self,
        guest: Guest,
        context_items: list[ContentContextItem],
        options: ContentGenerationOptions,
    ) -> ContentGenerationResult:
        lines = [f"{guest.name} ({options.platform}/{options.length} mock draft)"]
        for item in context_items[:3]:
            lines.append(f"- {item.text[:160]}")

        return ContentGenerationResult(title=None, content="\n".join(lines))
