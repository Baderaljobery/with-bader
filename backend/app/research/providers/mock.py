import asyncio

from app.research.models import RawResearchSource
from app.research.providers.base import ResearchSearchProvider

_FAKE_RESULT_TEMPLATES = [
    {
        "source_type": "company_website",
        "title_fmt": "{query} - Company Profile",
        "url_fmt": "https://example.test/profile/{slug}",
        "publisher": "Example Directory",
        "snippet_fmt": "Mock company profile result for '{query}'.",
    },
    {
        "source_type": "news",
        "title_fmt": "{query} shares insights in a recent feature",
        "url_fmt": "https://example-news.test/articles/{slug}",
        "publisher": "Example News",
        "snippet_fmt": "Mock news article snippet mentioning '{query}'.",
    },
    {
        "source_type": "website",
        "title_fmt": "{query} - Personal Website",
        "url_fmt": "https://example-personal.test/{slug}",
        "publisher": None,
        "snippet_fmt": "Mock personal website result for '{query}'.",
    },
    {
        "source_type": "interview",
        "title_fmt": "An interview with {query}",
        "url_fmt": "https://example-media.test/interviews/{slug}",
        "publisher": "Example Media",
        "snippet_fmt": "Mock interview article snippet referencing '{query}'.",
    },
]


def _slugify(value: str) -> str:
    return "-".join(value.lower().split()) or "guest"


class MockResearchSearchProvider(ResearchSearchProvider):
    """Deterministic, offline stand-in for a real provider (Tavily, Google, Bing, ...).

    Makes no network calls. Exists only so the orchestration pipeline can be
    developed and tested before a paid search API is wired in.
    """

    provider_name = "mock"

    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        await asyncio.sleep(0)

        slug = _slugify(query)
        results = [
            RawResearchSource(
                source_type=template["source_type"],
                url=template["url_fmt"].format(slug=slug),
                title=template["title_fmt"].format(query=query),
                publisher=template["publisher"],
                published_at=None,
                content=None,
                snippet=template["snippet_fmt"].format(query=query),
                metadata={"origin": "mock_search_provider", "query": query},
            )
            for template in _FAKE_RESULT_TEMPLATES
        ]
        return results[:limit]
