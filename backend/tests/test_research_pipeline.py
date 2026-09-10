import unittest

from app.research.models import NormalizedResearchSource, RawResearchSource
from app.research.normalization.deduplicator import deduplicate_sources
from app.research.normalization.source_normalizer import normalize_source
from tests.db_test_helpers import make_guest_create


class _FakeGuest:
    """Minimal stand-in for a Guest ORM instance - the query builder only
    reads the bilingual name (+ legacy name/job_title/company/biography as a
    getattr-safe fallback), so a full model isn't needed here. Only the name
    is bilingual - job_title/company/biography are plain single-value
    fields, exactly like the real Guest model."""

    def __init__(
        self,
        name_ar: str = "",
        name_en: str = "",
        name: str | None = None,
        job_title: str | None = None,
        company: str | None = None,
        biography: str | None = None,
    ):
        self.name_ar = name_ar
        self.name_en = name_en
        self.name = name
        self.job_title = job_title
        self.company = company
        self.biography = biography


class QueryBuilderTests(unittest.TestCase):
    def test_no_duplicate_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(
            name_ar="أحمد مثال",
            name_en="Ahmed Example",
            job_title="CEO",
            company="Example Co",
        )
        queries = build_research_queries(guest, max_queries=20)
        texts = [q.query for q in queries]
        self.assertEqual(len(texts), len(set(texts)))

    def test_arabic_guest_gets_arabic_phrased_queries_not_english_suffixes(self):
        """Phase 9 - an Arabic guest must not get English suffixes like
        "interview"/"biography" bolted onto the Arabic name."""
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="أحمد مثال", name_en="")
        queries = build_research_queries(guest, max_queries=20)
        self.assertTrue(queries)
        for q in queries:
            self.assertEqual(q.language, "ar")
            self.assertNotIn("interview", q.query.lower())
            self.assertNotIn("biography", q.query.lower())
            self.assertTrue(q.query.startswith("أحمد مثال"))

    def test_bilingual_guest_gets_both_language_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="أحمد مثال", name_en="Ahmed Example")
        queries = build_research_queries(guest, max_queries=20)
        languages = {q.language for q in queries}
        self.assertEqual(languages, {"ar", "en"})

    def test_skips_empty_optional_fields(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="", name_en="Solo Guest")
        queries = build_research_queries(guest, max_queries=20)
        self.assertTrue(queries)
        for q in queries:
            self.assertNotIn("  ", q.query)
            self.assertTrue(q.query.startswith("Solo Guest"))

    def test_respects_max_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="أحمد مثال", name_en="Ahmed Example", company="Example Co")
        queries = build_research_queries(guest, max_queries=3)
        self.assertLessEqual(len(queries), 3)

    def test_blank_name_returns_no_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="", name_en="")
        self.assertEqual(build_research_queries(guest, max_queries=8), [])

    def test_legacy_guest_falls_back_to_single_language_column(self):
        """A pre-bilingual-profile guest (name_ar/name_en both blank, only
        the legacy `name` column populated) still gets a usable query set."""
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name_ar="", name_en="", name="Legacy Guest")
        queries = build_research_queries(guest, max_queries=20)
        self.assertTrue(queries)
        self.assertTrue(all(q.query.startswith("Legacy Guest") for q in queries))


class QueryBudgetTests(unittest.TestCase):
    def test_budget_scales_with_profile_richness(self):
        from app.research.collectors.query_builder import estimate_query_budget

        thin_guest = _FakeGuest(name_ar="", name_en="Thin Guest")
        rich_guest = _FakeGuest(
            name_ar="أحمد مثال",
            name_en="Ahmed Example",
            job_title="CEO",
            company="Example Co",
            biography="A rich biography.",
        )
        thin_budget = estimate_query_budget(thin_guest, trusted_link_count=0)
        rich_budget = estimate_query_budget(rich_guest, trusted_link_count=3)
        self.assertLess(thin_budget, rich_budget)

    def test_budget_always_bounded(self):
        from app.research.collectors.query_builder import estimate_query_budget

        guest = _FakeGuest(name_ar="أحمد", name_en="Ahmed")
        budget = estimate_query_budget(guest, trusted_link_count=99, minimum=6, maximum=16)
        self.assertGreaterEqual(budget, 6)
        self.assertLessEqual(budget, 16)


class NormalizerTests(unittest.TestCase):
    def test_trims_values(self):
        raw = RawResearchSource(source_type="  Website  ", title="  Hello  ")
        normalized = normalize_source(raw)
        self.assertEqual(normalized.title, "Hello")
        self.assertEqual(normalized.source_type, "website")

    def test_unknown_type_falls_back_to_other(self):
        raw = RawResearchSource(source_type="totally_unrecognized_type")
        self.assertEqual(normalize_source(raw).source_type, "other")

    def test_canonical_url_strips_www_and_trailing_slash(self):
        raw = RawResearchSource(source_type="website", url="https://WWW.Example.com/Page/")
        normalized = normalize_source(raw)
        self.assertEqual(normalized.canonical_url, "https://example.com/Page")
        self.assertEqual(normalized.url, "https://WWW.Example.com/Page/")

    def test_blank_string_becomes_none(self):
        raw = RawResearchSource(source_type="website", title="   ")
        self.assertIsNone(normalize_source(raw).title)

class DeduplicatorTests(unittest.TestCase):
    def test_duplicate_urls_collapse(self):
        a = NormalizedResearchSource(source_type="article", canonical_url="https://example.com/a")
        b = NormalizedResearchSource(
            source_type="article", canonical_url="https://example.com/a", title="Has a title"
        )
        self.assertEqual(len(deduplicate_sources([a, b])), 1)

    def test_richer_source_wins(self):
        thin = NormalizedResearchSource(
            source_type="article", canonical_url="https://example.com/a"
        )
        rich = NormalizedResearchSource(
            source_type="article",
            canonical_url="https://example.com/a",
            title="Full title",
            publisher="Example Publisher",
            content="Full content",
        )
        result = deduplicate_sources([thin, rich])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Full title")

    def test_distinct_sources_are_preserved(self):
        a = NormalizedResearchSource(source_type="article", canonical_url="https://example.com/a")
        b = NormalizedResearchSource(source_type="article", canonical_url="https://example.com/b")
        self.assertEqual(len(deduplicate_sources([a, b])), 2)

    def test_sources_without_url_fall_back_to_title_publisher(self):
        a = NormalizedResearchSource(source_type="article", title="Same Title", publisher="Pub")
        b = NormalizedResearchSource(source_type="article", title="Same Title", publisher="Pub")
        c = NormalizedResearchSource(
            source_type="article", title="Different Title", publisher="Pub"
        )
        self.assertEqual(len(deduplicate_sources([a, b, c])), 2)

class ResearchEngineTests(unittest.IsolatedAsyncioTestCase):
    """Exercises the real orchestration against the real database, using only
    the mock provider/extractor - no network calls, no AI, no external APIs."""

    async def test_engine_calls_provider_and_extractor_and_saves_version(self):
        from app.database.session import SessionLocal
        from app.research.extraction.base import ResearchExtractor
        from app.research.extraction.mock import MockResearchExtractor
        from app.research.providers.base import ResearchSearchProvider
        from app.research.providers.mock import MockResearchSearchProvider
        from app.research.research_engine import ResearchEngine
        from app.services.guest_service import create_guest, delete_guest
        from tests.db_test_helpers import create_test_owner, delete_test_owner, make_guest_create

        class _SpySearchProvider(ResearchSearchProvider):
            provider_name = "mock"

            def __init__(self, inner):
                self.inner = inner
                self.calls = 0

            async def search(self, query, limit=10):
                self.calls += 1
                return await self.inner.search(query, limit=limit)

        class _SpyExtractor(ResearchExtractor):
            provider_name = "mock"

            def __init__(self, inner):
                self.inner = inner
                self.calls = 0

            async def extract(self, guest, sources):
                self.calls += 1
                return await self.inner.extract(guest, sources)

        db = SessionLocal()
        guest = None
        owner = None
        try:
            owner = create_test_owner(db)
            guest = create_guest(
                db, make_guest_create(name="Unit Test Guest - Research Engine"), owner.id
            )

            search_spy = _SpySearchProvider(MockResearchSearchProvider())
            extractor_spy = _SpyExtractor(MockResearchExtractor())
            engine = ResearchEngine(search_provider=search_spy, extractor=extractor_spy)

            result = await engine.run_guest_research(guest.id, db)

            self.assertGreater(search_spy.calls, 0)
            self.assertEqual(extractor_spy.calls, 1)
            self.assertEqual(result.guest_research.version, 1)
            self.assertEqual(result.guest_research.guest_id, guest.id)
        finally:
            if guest is not None:
                delete_guest(db, guest.id)
            if owner is not None:
                delete_test_owner(db, owner)
            db.close()

if __name__ == "__main__":
    unittest.main()
