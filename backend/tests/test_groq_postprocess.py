import unittest

from app.research.extraction.groq_models import (
    AchievementItem,
    CareerHistoryItem,
    GroqExtractionSchema,
    InterviewAngleItem,
)
from app.research.extraction.groq_postprocess import build_extraction_result
from app.research.models import NormalizedResearchSource


class _FakeGuest:
    def __init__(self, name="Test Guest", job_title="CEO", company="Example Co"):
        self.name = name
        self.job_title = job_title
        self.company = company


def _indexed(*urls: str) -> dict[str, NormalizedResearchSource]:
    return {
        f"S{i + 1}": NormalizedResearchSource(
            source_type="website", url=url, canonical_url=url, title=f"Source {i + 1}"
        )
        for i, url in enumerate(urls)
    }


class SourceIdValidationTests(unittest.TestCase):
    def test_valid_source_ids_are_kept_and_resolved_to_urls(self):
        indexed = _indexed("https://example.org/a", "https://example.org/b")
        schema = GroqExtractionSchema(
            achievements=[AchievementItem(title="Did a thing", source_ids=["S1", "S2"])]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        [item] = result.achievements
        self.assertEqual(item["source_ids"], ["S1", "S2"])
        self.assertEqual(
            item["source_urls"], ["https://example.org/a", "https://example.org/b"]
        )

    def test_invalid_source_ids_are_removed(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(
            achievements=[AchievementItem(title="Did a thing", source_ids=["S1", "S999", "UNKNOWN"])]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        [item] = result.achievements
        self.assertEqual(item["source_ids"], ["S1"])
        self.assertEqual(item["source_urls"], ["https://example.org/a"])

    def test_claim_with_zero_valid_source_ids_is_dropped(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(
            achievements=[AchievementItem(title="Fabricated claim", source_ids=["S999"])]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(result.achievements, [])

    def test_claim_with_no_source_ids_at_all_is_dropped(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(
            achievements=[AchievementItem(title="No citation given", source_ids=[])]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(result.achievements, [])

    def test_interview_angle_may_have_zero_source_ids(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(
            potential_interview_angles=[
                InterviewAngleItem(
                    title="Career journey",
                    reason="Generic angle from profile metadata",
                    priority="high",
                    source_ids=[],
                )
            ]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(len(result.potential_interview_angles), 1)
        self.assertEqual(result.potential_interview_angles[0]["source_ids"], [])


class DuplicateCleanupTests(unittest.TestCase):
    def test_duplicate_career_entries_collapse_keeping_richer(self):
        indexed = _indexed("https://example.org/a", "https://example.org/b")
        schema = GroqExtractionSchema(
            career_history=[
                CareerHistoryItem(company="Acme", role="CEO", source_ids=["S1"]),
                CareerHistoryItem(
                    company="Acme",
                    role="CEO",
                    description="Richer duplicate with more detail",
                    source_ids=["S1", "S2"],
                ),
            ]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(len(result.career_history), 1)
        self.assertEqual(
            result.career_history[0]["description"], "Richer duplicate with more detail"
        )

    def test_distinct_achievements_are_preserved(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(
            achievements=[
                AchievementItem(title="Achievement A", source_ids=["S1"]),
                AchievementItem(title="Achievement B", source_ids=["S1"]),
            ]
        )
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(len(result.achievements), 2)


class RoleTitleCompanyFallbackTests(unittest.TestCase):
    def test_guest_metadata_used_when_llm_provides_no_better_value(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(role_title=None, company=None)
        guest = _FakeGuest(job_title="Founder", company="Startup Inc")
        result = build_extraction_result(schema, indexed, guest)
        self.assertEqual(result.role_title, "Founder")
        self.assertEqual(result.company, "Startup Inc")

    def test_llm_sourced_value_is_preferred_over_guest_metadata(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(role_title="Chief Executive Officer", company="Acme Corp")
        guest = _FakeGuest(job_title="Founder", company="Startup Inc")
        result = build_extraction_result(schema, indexed, guest)
        self.assertEqual(result.role_title, "Chief Executive Officer")
        self.assertEqual(result.company, "Acme Corp")


class EmptySourceSetTests(unittest.TestCase):
    def test_empty_source_set_drops_all_factual_claims_but_keeps_generic_angle(self):
        schema = GroqExtractionSchema(
            achievements=[AchievementItem(title="Unsupported", source_ids=["S1"])],
            potential_interview_angles=[
                InterviewAngleItem(
                    title="Career journey", reason="Based on profile only", source_ids=[]
                )
            ],
        )
        result = build_extraction_result(schema, {}, _FakeGuest())
        self.assertEqual(result.achievements, [])
        self.assertEqual(len(result.potential_interview_angles), 1)


class TopicsTests(unittest.TestCase):
    def test_topics_deduplicated_and_trimmed(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqExtractionSchema(topics=["  leadership ", "leadership", "AI"])
        result = build_extraction_result(schema, indexed, _FakeGuest())
        self.assertEqual(result.topics, ["leadership", "AI"])


if __name__ == "__main__":
    unittest.main()
