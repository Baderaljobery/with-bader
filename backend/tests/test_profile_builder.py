import unittest

from app.research.models import NormalizedResearchSource, ResearchExtractionResult
from app.research.profile_builder import build_guest_research_payload
from app.schemas.guest_research import GuestResearchResponse


class ProfileBuilderSourceTests(unittest.TestCase):
    def _build(self, sources: list[NormalizedResearchSource]):
        extraction = ResearchExtractionResult(role_title="CEO", company="Example Co")
        payload = build_guest_research_payload(extraction, sources)
        self.assertEqual(len(payload.sources), len(sources))
        return payload.sources

    def test_preserves_snippet(self):
        source = NormalizedResearchSource(source_type="website", snippet="A relevant highlight.")
        [result] = self._build([source])
        self.assertEqual(result.snippet, "A relevant highlight.")

    def test_preserves_content(self):
        source = NormalizedResearchSource(source_type="website", content="Bounded page text.")
        [result] = self._build([source])
        self.assertEqual(result.content, "Bounded page text.")

    def test_preserves_provider(self):
        source = NormalizedResearchSource(source_type="website", metadata={"provider": "exa"})
        [result] = self._build([source])
        self.assertEqual(result.provider, "exa")

    def test_preserves_score(self):
        source = NormalizedResearchSource(source_type="website", metadata={"score": 0.91})
        [result] = self._build([source])
        self.assertEqual(result.score, 0.91)

    def test_preserves_query(self):
        source = NormalizedResearchSource(
            source_type="website", metadata={"query": "Sam Altman OpenAI interview"}
        )
        [result] = self._build([source])
        self.assertEqual(result.query, "Sam Altman OpenAI interview")

    def test_missing_metadata_fields_become_null(self):
        source = NormalizedResearchSource(source_type="website", metadata={})
        [result] = self._build([source])
        self.assertIsNone(result.provider)
        self.assertIsNone(result.score)
        self.assertIsNone(result.query)

    def test_content_is_truncated_to_configured_max_chars(self):
        from app.core.config import settings

        original_limit = settings.research_source_content_max_chars
        settings.research_source_content_max_chars = 10
        try:
            source = NormalizedResearchSource(
                source_type="website",
                content="This text is definitely longer than ten characters.",
                snippet="This snippet is also longer than ten characters.",
            )
            [result] = self._build([source])
            self.assertEqual(len(result.content), 10)
            self.assertEqual(len(result.snippet), 10)
        finally:
            settings.research_source_content_max_chars = original_limit

    def test_url_title_publisher_are_never_truncated(self):
        from app.core.config import settings

        original_limit = settings.research_source_content_max_chars
        settings.research_source_content_max_chars = 5
        try:
            long_url = "https://example.org/" + "a" * 50
            long_title = "A very long title that exceeds five characters"
            source = NormalizedResearchSource(
                source_type="website",
                url=long_url,
                canonical_url=long_url,
                title=long_title,
                publisher="a-long-publisher-domain.example.org",
            )
            [result] = self._build([source])
            self.assertEqual(result.url, long_url)
            self.assertEqual(result.title, long_title)
            self.assertEqual(result.publisher, "a-long-publisher-domain.example.org")
        finally:
            settings.research_source_content_max_chars = original_limit

    def test_exa_normalized_source_maps_correctly(self):
        source = NormalizedResearchSource(
            source_type="news",
            url="https://forbes.com/profile/example",
            canonical_url="https://forbes.com/profile/example",
            title="Example Profile",
            publisher="forbes.com",
            snippet="A highlight from Exa.",
            content="Bounded body text from Exa.",
            metadata={"provider": "exa", "score": 0.93, "query": "Sam Altman OpenAI interview"},
        )
        [result] = self._build([source])
        self.assertEqual(result.type, "news")
        self.assertEqual(result.url, "https://forbes.com/profile/example")
        self.assertEqual(result.snippet, "A highlight from Exa.")
        self.assertEqual(result.content, "Bounded body text from Exa.")
        self.assertEqual(result.provider, "exa")
        self.assertEqual(result.score, 0.93)
        self.assertEqual(result.query, "Sam Altman OpenAI interview")

    def test_tavily_normalized_source_maps_correctly(self):
        # Tavily's provider currently leaves .content = None and puts its
        # returned text into .snippet - profile_builder must preserve that
        # as-is rather than inventing a value for the missing field.
        source = NormalizedResearchSource(
            source_type="article",
            url="https://example-news.test/a",
            canonical_url="https://example-news.test/a",
            title="An Article",
            snippet="Tavily's search snippet text.",
            content=None,
            metadata={"provider": "tavily", "score": 0.82, "query": "Example query"},
        )
        [result] = self._build([source])
        self.assertEqual(result.snippet, "Tavily's search snippet text.")
        self.assertIsNone(result.content)
        self.assertEqual(result.provider, "tavily")
        self.assertEqual(result.score, 0.82)


class BackwardCompatibilityTests(unittest.TestCase):
    def test_old_source_shape_without_new_fields_remains_valid_in_response(self):
        old_style_source = {
            "type": "linkedin",
            "url": "https://linkedin.com/in/example",
            "title": "LinkedIn profile",
            "publisher": None,
            "published_at": None,
            "notes": None,
        }
        response = GuestResearchResponse(
            id="00000000-0000-0000-0000-000000000001",
            guest_id="00000000-0000-0000-0000-000000000002",
            version=1,
            career_history=[],
            education=[],
            achievements=[],
            projects=[],
            topics=[],
            interesting_events=[],
            potential_interview_angles=[],
            sources=[old_style_source],
            created_at="2026-01-01T00:00:00Z",
        )
        self.assertEqual(response.sources, [old_style_source])


if __name__ == "__main__":
    unittest.main()
