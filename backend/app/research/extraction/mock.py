from app.models.guest import Guest
from app.research.extraction.base import ResearchExtractor
from app.research.models import NormalizedResearchSource, ResearchExtractionResult


class MockResearchExtractor(ResearchExtractor):
    """Deterministic stand-in for a real LLM extractor (OpenAI, Anthropic, Gemini, ...).

    Produces obviously synthetic, generic output derived only from fields the
    guest already provided. Never fabricates facts about a real person.
    """

    provider_name = "mock"

    async def extract(
        self, guest: Guest, sources: list[NormalizedResearchSource]
    ) -> ResearchExtractionResult:
        topics: list[str] = ["career", "leadership"]
        if sources:
            topics.append("public presence")

        angles: list[dict] = [
            {
                "title": "Professional Journey",
                "reason": "Explore the guest's career journey based on their provided profile",
                "priority": "high",
            }
        ]
        if guest.company:
            angles.append(
                {
                    "title": f"Working at {guest.company}",
                    "reason": "Discuss the guest's day-to-day role and responsibilities",
                    "priority": "medium",
                }
            )

        return ResearchExtractionResult(
            role_title=guest.job_title,
            company=guest.company,
            career_history=[],
            education=[],
            achievements=[],
            projects=[],
            topics=topics,
            interesting_events=[],
            potential_interview_angles=angles,
        )
