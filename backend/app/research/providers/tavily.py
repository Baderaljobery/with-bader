from datetime import datetime
from urllib.parse import urlsplit

import httpx

from app.research.models import RawResearchSource
from app.research.normalization.source_normalizer import infer_source_type_from_url
from app.research.providers.base import (
    ResearchProviderError,
    ResearchProviderTimeoutError,
    ResearchSearchProvider,
)

_TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def _extract_publisher(url: str | None) -> str | None:
    if not url:
        return None
    host = urlsplit(url).netloc.lower()
    if host.startswith("www."):
        host = host[len("www.") :]
    return host or None


def _parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class TavilyResearchSearchProvider(ResearchSearchProvider):
    """Real search provider backed by the Tavily Search API.

    Converts Tavily's response shape into project-internal RawResearchSource
    objects only - no Tavily-specific object (response dict, status code,
    etc.) ever leaves this module. Does not fetch the returned URLs itself;
    it only uses the title/url/snippet Tavily returns directly.
    """

    provider_name = "tavily"

    def __init__(self, api_key: str, timeout_seconds: float = 15.0) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    _TAVILY_SEARCH_URL,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "query": query,
                        "max_results": limit,
                        "search_depth": "basic",
                    },
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ResearchProviderTimeoutError(
                f"Tavily search timed out for query '{query}'"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ResearchProviderError(
                f"Tavily search failed with status {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise ResearchProviderError(
                f"Tavily search request failed: {exc.__class__.__name__}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ResearchProviderError("Tavily search returned an invalid response") from exc

        results = payload.get("results") or []

        sources: list[RawResearchSource] = []
        for result in results[:limit]:
            url = result.get("url")
            sources.append(
                RawResearchSource(
                    source_type=infer_source_type_from_url(url),
                    url=url,
                    title=result.get("title"),
                    publisher=_extract_publisher(url),
                    published_at=_parse_published_at(result.get("published_date")),
                    content=None,
                    snippet=result.get("content"),
                    metadata={
                        "provider": "tavily",
                        "score": result.get("score"),
                        "query": query,
                    },
                )
            )
        return sources
