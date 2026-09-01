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

_EXA_SEARCH_URL = "https://api.exa.ai/search"
_MAX_TEXT_CHARS = 500


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
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _bounded_text(value: str | None, limit: int = _MAX_TEXT_CHARS) -> str | None:
    if not value:
        return None
    trimmed = value.strip()
    return trimmed[:limit] if trimmed else None


def _first_highlight(result: dict) -> str | None:
    highlights = result.get("highlights")
    if isinstance(highlights, list) and highlights:
        first = highlights[0]
        if isinstance(first, str):
            return _bounded_text(first)
    return None


class ExaResearchSearchProvider(ResearchSearchProvider):
    """Real search provider backed by the Exa Search API (api.exa.ai).

    Converts Exa's response shape into project-internal RawResearchSource
    objects only - no Exa-specific object ever leaves this module. Uses only
    the title/url/highlights/text Exa returns as part of the same search
    call; never fetches the returned URLs itself.
    """

    provider_name = "exa"

    def __init__(self, api_key: str, timeout_seconds: float = 15.0) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    _EXA_SEARCH_URL,
                    headers={
                        "x-api-key": self._api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query,
                        "numResults": limit,
                        "type": "auto",
                        "contents": {
                            "text": {"maxCharacters": _MAX_TEXT_CHARS},
                            "highlights": True,
                        },
                    },
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ResearchProviderTimeoutError(
                f"Exa search timed out for query '{query}'"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ResearchProviderError(
                f"Exa search failed with status {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise ResearchProviderError(
                f"Exa search request failed: {exc.__class__.__name__}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ResearchProviderError("Exa search returned an invalid response") from exc

        results = payload.get("results") or []

        sources: list[RawResearchSource] = []
        for result in results[:limit]:
            url = result.get("url")
            text = _bounded_text(result.get("text"))
            sources.append(
                RawResearchSource(
                    source_type=infer_source_type_from_url(url),
                    url=url,
                    title=result.get("title"),
                    publisher=_extract_publisher(url),
                    published_at=_parse_published_at(result.get("publishedDate")),
                    content=text,
                    snippet=_first_highlight(result) or text,
                    metadata={
                        "provider": "exa",
                        "score": result.get("score"),
                        "query": query,
                    },
                )
            )
        return sources
