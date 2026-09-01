import unittest
from unittest.mock import AsyncMock, patch

import httpx

from app.research.providers.base import ResearchProviderError, ResearchProviderTimeoutError
from app.research.providers.tavily import TavilyResearchSearchProvider


class _FakeResponse:
    def __init__(self, json_data=None, raise_exc: Exception | None = None):
        self._json_data = json_data or {}
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc is not None:
            raise self._raise_exc

    def json(self):
        return self._json_data


class _FakeAsyncClient:
    def __init__(self, response=None, side_effect=None):
        self.post = (
            AsyncMock(side_effect=side_effect) if side_effect else AsyncMock(return_value=response)
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def _patch_client(fake_client):
    return patch("app.research.providers.tavily.httpx.AsyncClient", return_value=fake_client)


class TavilyProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_result_mapping(self):
        response = _FakeResponse(
            json_data={
                "results": [
                    {
                        "url": "https://en.wikipedia.org/wiki/Example",
                        "title": "Example - Wikipedia",
                        "content": "Example snippet text.",
                        "score": 0.87,
                    }
                ]
            }
        )
        with _patch_client(_FakeAsyncClient(response=response)):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            results = await provider.search("Example Guest", limit=5)

        self.assertEqual(len(results), 1)
        source = results[0]
        self.assertEqual(source.url, "https://en.wikipedia.org/wiki/Example")
        self.assertEqual(source.title, "Example - Wikipedia")
        self.assertEqual(source.snippet, "Example snippet text.")
        self.assertEqual(source.publisher, "en.wikipedia.org")
        self.assertEqual(source.source_type, "website")
        self.assertEqual(source.metadata["provider"], "tavily")
        self.assertEqual(source.metadata["score"], 0.87)
        self.assertEqual(source.metadata["query"], "Example Guest")

    async def test_source_type_inferred_for_known_domains(self):
        response = _FakeResponse(
            json_data={
                "results": [
                    {"url": "https://www.linkedin.com/in/example", "title": "LinkedIn profile"},
                    {"url": "https://www.youtube.com/watch?v=abc", "title": "A video"},
                ]
            }
        )
        with _patch_client(_FakeAsyncClient(response=response)):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            results = await provider.search("Example", limit=5)

        self.assertEqual(results[0].source_type, "linkedin")
        self.assertEqual(results[1].source_type, "youtube")

    async def test_empty_results(self):
        response = _FakeResponse(json_data={"results": []})
        with _patch_client(_FakeAsyncClient(response=response)):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            results = await provider.search("Nobody In Particular", limit=5)
        self.assertEqual(results, [])

    async def test_api_error_raises_provider_error(self):
        request = httpx.Request("POST", "https://api.tavily.com/search")
        response_obj = httpx.Response(status_code=401, request=request)
        error_response = _FakeResponse(
            raise_exc=httpx.HTTPStatusError(
                "unauthorized", request=request, response=response_obj
            )
        )
        with _patch_client(_FakeAsyncClient(response=error_response)):
            provider = TavilyResearchSearchProvider(api_key="bad-key")
            with self.assertRaises(ResearchProviderError):
                await provider.search("Example", limit=5)

    async def test_timeout_raises_provider_timeout_error(self):
        with _patch_client(_FakeAsyncClient(side_effect=httpx.ConnectTimeout("timed out"))):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            with self.assertRaises(ResearchProviderTimeoutError):
                await provider.search("Example", limit=5)

    async def test_missing_api_key_raises_configuration_error(self):
        from app.core.config import settings
        from app.research.providers.base import ResearchProviderConfigurationError
        from app.research.research_engine import build_search_provider

        original_provider = settings.research_search_provider
        original_key = settings.tavily_api_key
        settings.research_search_provider = "tavily"
        settings.tavily_api_key = None
        try:
            with self.assertRaises(ResearchProviderConfigurationError):
                build_search_provider()
        finally:
            settings.research_search_provider = original_provider
            settings.tavily_api_key = original_key

    async def test_result_missing_optional_fields(self):
        response = _FakeResponse(json_data={"results": [{"url": "https://example.org/a"}]})
        with _patch_client(_FakeAsyncClient(response=response)):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            results = await provider.search("Example", limit=5)

        self.assertEqual(len(results), 1)
        source = results[0]
        self.assertIsNone(source.title)
        self.assertIsNone(source.snippet)
        self.assertIsNone(source.published_at)
        self.assertIsNone(source.metadata.get("score"))

    async def test_limit_is_respected(self):
        response = _FakeResponse(
            json_data={
                "results": [
                    {"url": f"https://example.org/{i}", "title": f"Result {i}"}
                    for i in range(10)
                ]
            }
        )
        with _patch_client(_FakeAsyncClient(response=response)):
            provider = TavilyResearchSearchProvider(api_key="fake-key")
            results = await provider.search("Example", limit=3)

        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
