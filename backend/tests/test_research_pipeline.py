import unittest

from app.research.models import NormalizedResearchSource, RawResearchSource
from app.research.normalization.deduplicator import deduplicate_sources
from app.research.normalization.source_normalizer import normalize_source


class _FakeGuest:
    """Minimal stand-in for a Guest ORM instance - the query builder only
    reads .name / .job_title / .company, so a full model isn't needed here."""

    def __init__(self, name: str, job_title: str | None = None, company: str | None = None):
        self.name = name
        self.job_title = job_title
        self.company = company


class QueryBuilderTests(unittest.TestCase):
    def test_no_duplicate_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name="Ahmed Example", job_title="CEO", company="Example Co")
        queries = build_research_queries(guest, max_queries=20)
        texts = [q.query for q in queries]
        self.assertEqual(len(texts), len(set(texts)))

    def test_skips_empty_optional_fields(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name="Solo Guest")
        queries = build_research_queries(guest, max_queries=20)
        self.assertTrue(queries)
        for q in queries:
            self.assertNotIn("  ", q.query)
            self.assertTrue(q.query.startswith("Solo Guest"))

    def test_respects_max_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name="Ahmed Example", job_title="CEO", company="Example Co")
        queries = build_research_queries(guest, max_queries=3)
        self.assertLessEqual(len(queries), 3)

    def test_blank_name_returns_no_queries(self):
        from app.research.collectors.query_builder import build_research_queries

        guest = _FakeGuest(name="")
        self.assertEqual(build_research_queries(guest, max_queries=8), [])


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
        from app.schemas.guest import GuestCreate
        from app.services.guest_service import create_guest, delete_guest

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
        try:
            guest = create_guest(db, GuestCreate(name="Unit Test Guest - Research Engine"))

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
            db.close()


if __name__ == "__main__":
    unittest.main()
