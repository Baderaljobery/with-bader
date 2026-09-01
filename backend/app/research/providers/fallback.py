from app.research.models import RawResearchSource
from app.research.providers.base import ResearchProviderError, ResearchSearchProvider


class FallbackResearchSearchProvider(ResearchSearchProvider):
    """Wraps a primary provider with a fallback, per-query.

    For each query: try the primary; if it raises a provider-level error,
    retry that same query on the fallback. If the fallback also fails, the
    query is a genuine failure (surfaces to ResearchEngine's existing
    partial-query-failure handling, same as any other failed query).

    Deliberately does NOT fall back on a primary result that is merely empty
    or "weak" - only on an actual ResearchProviderError from the primary.

    Implements ResearchSearchProvider itself, so ResearchEngine never needs
    to know a fallback mechanism exists - it just sees one provider.
    """

    def __init__(
        self, primary: ResearchSearchProvider, fallback: ResearchSearchProvider
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self.provider_name = primary.provider_name
        self.fallback_provider_name = fallback.provider_name
        self.fallback_queries_used = 0

    async def search(self, query: str, limit: int = 10) -> list[RawResearchSource]:
        try:
            return await self._primary.search(query, limit=limit)
        except ResearchProviderError as primary_exc:
            try:
                results = await self._fallback.search(query, limit=limit)
            except ResearchProviderError as fallback_exc:
                raise ResearchProviderError(
                    f"Both {self.provider_name} and {self.fallback_provider_name} search "
                    f"providers failed for query '{query}': "
                    f"{self.provider_name} error={primary_exc}; "
                    f"{self.fallback_provider_name} error={fallback_exc}"
                ) from fallback_exc

            self.fallback_queries_used += 1
            return results
