import unittest

from app.research.models import RawResearchSource
from app.research.providers.base import ResearchProviderError, ResearchSearchProvider
from app.research.providers.fallback import FallbackResearchSearchProvider


class _FakeProvider(ResearchSearchProvider):
    """Test double: returns a fixed list, or raises, and counts calls."""

    def __init__(self, name: str, results=None, raise_exc: Exception | None = None):
        self.provider_name = name
        self._results = results if results is not None else []
        self._raise_exc = raise_exc
        self.calls: list[str] = []

    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        self.calls.append(query)
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._results


def _source(provider: str) -> RawResearchSource:
    return RawResearchSource(
        source_type="website",
        url="https://example.org/a",
        title="A",
        metadata={"provider": provider},
    )


class FallbackProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_primary_success_does_not_call_fallback(self):
        primary = _FakeProvider("exa", results=[_source("exa")])
        fallback = _FakeProvider("tavily", results=[_source("tavily")])
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        results = await provider.search("Example", limit=5)

        self.assertEqual(len(primary.calls), 1)
        self.assertEqual(len(fallback.calls), 0)
        self.assertEqual(results[0].metadata["provider"], "exa")
        self.assertEqual(provider.fallback_queries_used, 0)

    async def test_primary_timeout_triggers_fallback(self):
        from app.research.providers.base import ResearchProviderTimeoutError

        primary = _FakeProvider("exa", raise_exc=ResearchProviderTimeoutError("timed out"))
        fallback = _FakeProvider("tavily", results=[_source("tavily")])
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        results = await provider.search("Example", limit=5)

        self.assertEqual(len(fallback.calls), 1)
        self.assertEqual(results[0].metadata["provider"], "tavily")
        self.assertEqual(provider.fallback_queries_used, 1)

    async def test_primary_provider_error_triggers_fallback(self):
        primary = _FakeProvider("exa", raise_exc=ResearchProviderError("upstream 500"))
        fallback = _FakeProvider("tavily", results=[_source("tavily")])
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        results = await provider.search("Example", limit=5)

        self.assertEqual(len(fallback.calls), 1)
        self.assertEqual(results[0].metadata["provider"], "tavily")

    async def test_primary_empty_results_does_not_trigger_fallback(self):
        primary = _FakeProvider("exa", results=[])
        fallback = _FakeProvider("tavily", results=[_source("tavily")])
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        results = await provider.search("Example", limit=5)

        self.assertEqual(results, [])
        self.assertEqual(len(fallback.calls), 0)
        self.assertEqual(provider.fallback_queries_used, 0)

    async def test_both_fail_raises_provider_error(self):
        primary = _FakeProvider("exa", raise_exc=ResearchProviderError("exa down"))
        fallback = _FakeProvider("tavily", raise_exc=ResearchProviderError("tavily down"))
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        with self.assertRaises(ResearchProviderError):
            await provider.search("Example", limit=5)

    async def test_provider_name_and_fallback_provider_name_reported(self):
        primary = _FakeProvider("exa", results=[])
        fallback = _FakeProvider("tavily", results=[])
        provider = FallbackResearchSearchProvider(primary=primary, fallback=fallback)

        self.assertEqual(provider.provider_name, "exa")
        self.assertEqual(provider.fallback_provider_name, "tavily")


if __name__ == "__main__":
    unittest.main()
