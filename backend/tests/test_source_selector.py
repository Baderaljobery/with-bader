import unittest

from app.research.extraction.source_selector import (
    assign_source_ids,
    bounded_source_text,
    select_sources_for_extraction,
)
from app.research.models import NormalizedResearchSource
from tests.db_test_helpers import FakeGuestIdentity

# These tests exercise pure ranking/selection mechanics (content richness,
# domain diversity, max_sources), independent of identity relevance - a
# blank guest + min_identity_relevance=0.0 disables the identity floor so
# every candidate is eligible for ranking. IdentityFloorTests below covers
# the floor itself.
_BLANK_GUEST = FakeGuestIdentity()


class SourceSelectorTests(unittest.TestCase):
    def test_prefers_sources_with_content_and_higher_score(self):
        weak = NormalizedResearchSource(source_type="website", url="https://a.example/1")
        strong = NormalizedResearchSource(
            source_type="website",
            url="https://b.example/1",
            content="Useful body text",
            metadata={"score": 0.9},
        )
        selected = select_sources_for_extraction(
            [weak, strong], _BLANK_GUEST, max_sources=1, min_identity_relevance=0.0
        )
        self.assertEqual(selected, [strong])

    def test_respects_max_sources(self):
        sources = [
            NormalizedResearchSource(source_type="website", url=f"https://example{i}.org/a")
            for i in range(20)
        ]
        selected = select_sources_for_extraction(
            sources, _BLANK_GUEST, max_sources=5, min_identity_relevance=0.0
        )
        self.assertEqual(len(selected), 5)

    def test_prefers_domain_diversity_before_repeats(self):
        same_domain = [
            NormalizedResearchSource(
                source_type="website",
                url=f"https://repeated.example/{i}",
                content="text",
                metadata={"score": 1.0 - i * 0.01},
            )
            for i in range(5)
        ]
        distinct_domain = NormalizedResearchSource(
            source_type="website",
            url="https://distinct.example/a",
            content="text",
            metadata={"score": 0.1},
        )
        selected = select_sources_for_extraction(
            same_domain + [distinct_domain], _BLANK_GUEST, max_sources=2, min_identity_relevance=0.0
        )
        selected_urls = {s.url for s in selected}
        self.assertIn(distinct_domain.url, selected_urls)

    def test_empty_input_returns_empty(self):
        self.assertEqual(
            select_sources_for_extraction([], _BLANK_GUEST, max_sources=15), []
        )

    def test_zero_max_sources_returns_empty(self):
        sources = [NormalizedResearchSource(source_type="website", url="https://a.example/1")]
        self.assertEqual(
            select_sources_for_extraction(
                sources, _BLANK_GUEST, max_sources=0, min_identity_relevance=0.0
            ),
            [],
        )


class IdentityFloorTests(unittest.TestCase):
    def test_sources_below_identity_floor_are_excluded(self):
        guest = FakeGuestIdentity(name_ar="أحمد مثال", name_en="Ahmed Example")
        unrelated = NormalizedResearchSource(
            source_type="website",
            url="https://a.example/1",
            title="Completely unrelated page",
            content="Nothing about this guest at all.",
        )
        selected = select_sources_for_extraction(
            [unrelated], guest, max_sources=5, min_identity_relevance=0.2
        )
        self.assertEqual(selected, [])

    def test_trusted_guest_link_always_passes_the_floor(self):
        guest = FakeGuestIdentity(name_ar="أحمد مثال", name_en="Ahmed Example")
        trusted = NormalizedResearchSource(
            source_type="linkedin",
            url="https://linkedin.com/in/someone",
            metadata={"origin": "guest_link"},
        )
        selected = select_sources_for_extraction(
            [trusted], guest, max_sources=5, min_identity_relevance=0.5
        )
        self.assertEqual(selected, [trusted])


class AssignSourceIdsTests(unittest.TestCase):
    def test_assigns_sequential_ids_in_order(self):
        sources = [
            NormalizedResearchSource(source_type="website", url="https://a.example/1"),
            NormalizedResearchSource(source_type="website", url="https://b.example/1"),
        ]
        indexed = assign_source_ids(sources)
        self.assertEqual(list(indexed.keys()), ["S1", "S2"])
        self.assertEqual(indexed["S1"].url, "https://a.example/1")
        self.assertEqual(indexed["S2"].url, "https://b.example/1")


class BoundedSourceTextTests(unittest.TestCase):
    def test_prefers_content_over_snippet(self):
        source = NormalizedResearchSource(
            source_type="website", content="Full content text", snippet="Just a snippet"
        )
        self.assertEqual(bounded_source_text(source, max_chars=100), "Full content text")

    def test_falls_back_to_snippet_when_no_content(self):
        source = NormalizedResearchSource(source_type="website", snippet="Just a snippet")
        self.assertEqual(bounded_source_text(source, max_chars=100), "Just a snippet")

    def test_truncates_to_max_chars(self):
        source = NormalizedResearchSource(source_type="website", content="x" * 2000)
        text = bounded_source_text(source, max_chars=50)
        self.assertEqual(len(text), 50)

    def test_returns_none_when_no_text_available(self):
        source = NormalizedResearchSource(source_type="website")
        self.assertIsNone(bounded_source_text(source, max_chars=100))


if __name__ == "__main__":
    unittest.main()
