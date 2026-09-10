import asyncio
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.guest_research import GuestResearch
from app.research.collectors.guest_link_collector import collect_guest_link_sources
from app.research.collectors.query_builder import estimate_query_budget
from app.research.extraction.base import ResearchExtractor
from app.research.extraction.factory import build_research_extractor
from app.research.identity_resolution import aggregate_identity_relevance
from app.research.models import RawResearchSource
from app.research.normalization.deduplicator import deduplicate_sources
from app.research.normalization.source_normalizer import normalize_sources
from app.research.profile_builder import build_guest_research_payload
from app.research.providers.base import (
    ResearchProviderConfigurationError,
    ResearchProviderError,
    ResearchProviderTimeoutError,
    ResearchSearchProvider,
)
from app.research.providers.exa import ExaResearchSearchProvider
from app.research.providers.fallback import FallbackResearchSearchProvider
from app.research.providers.mock import MockResearchSearchProvider
from app.research.providers.tavily import TavilyResearchSearchProvider
from app.research.research_planner import plan_research_queries
from app.services import guest_research_service, guest_service


@dataclass
class ResearchRunResult:
    guest_research: GuestResearch
    search_provider: str
    primary_search_provider: str
    fallback_search_provider: str | None
    fallback_queries_used: int
    extractor_provider: str
    extractor_model: str | None
    queries_executed: int
    queries_failed: int
    total_sources_found: int
    total_sources_after_deduplication: int
    identity_confidence: float
    needs_identity_confirmation: bool


class ResearchEngine:
    """Core research orchestration.

    Knows only about the ResearchSearchProvider and ResearchExtractor
    abstractions - never about a specific vendor (Tavily, Google, OpenAI,
    Anthropic, ...). Vendor-specific implementations plug in from outside.
    """

    def __init__(
        self,
        search_provider: ResearchSearchProvider,
        extractor: ResearchExtractor,
        quality_fallback_provider: ResearchSearchProvider | None = None,
        max_queries: int | None = None,
        results_per_query: int | None = None,
        max_concurrent_searches: int = 5,
    ) -> None:
        self._search_provider = search_provider
        self._extractor = extractor
        # A second handle on the fallback provider, used only for the
        # quality-based backfill below (Phase 14) - distinct from the
        # exception-triggered per-query fallback FallbackResearchSearchProvider
        # already performs transparently inside `search_provider` itself.
        self._quality_fallback_provider = quality_fallback_provider
        self._hard_max_queries = max_queries or settings.research_max_queries
        self._results_per_query = results_per_query or settings.research_results_per_query
        self._semaphore = asyncio.Semaphore(max_concurrent_searches)

    async def _run_query(
        self, query: str, provider: ResearchSearchProvider | None = None
    ) -> list[RawResearchSource]:
        async with self._semaphore:
            return await (provider or self._search_provider).search(
                query, limit=self._results_per_query
            )

    def _needs_quality_fallback(self, sources: list[RawResearchSource]) -> bool:
        """Weak-primary-results signal (Phase 14) - distinct from the
        exception-only trigger the wrapped provider already handles.
        Considers result count and domain diversity; identity relevance is
        evaluated later (once sources are deduplicated) via
        needs_identity_confirmation, which the caller also acts on."""
        if len(sources) < settings.research_quality_fallback_min_sources:
            return True
        hosts: set[str] = set()
        for source in sources:
            if source.url:
                hosts.add(source.url.split("/")[2] if "//" in source.url else source.url)
        return len(hosts) < settings.research_quality_fallback_min_domains

    async def run_guest_research(self, guest_id: uuid.UUID, db: Session) -> ResearchRunResult:
        guest = guest_service.get_guest_by_id(db, guest_id)

        link_sources = await collect_guest_link_sources(db, guest_id)

        budget = estimate_query_budget(
            guest,
            trusted_link_count=len(link_sources),
            minimum=settings.research_min_queries,
            maximum=self._hard_max_queries,
        )
        queries = await plan_research_queries(guest, max_queries=budget)

        outcomes = await asyncio.gather(
            *(self._run_query(query.query) for query in queries), return_exceptions=True
        )

        search_sources: list[RawResearchSource] = []
        failure_errors: list[BaseException] = []
        for outcome in outcomes:
            if isinstance(outcome, BaseException):
                failure_errors.append(outcome)
                continue
            search_sources.extend(outcome)

        queries_failed = len(failure_errors)
        if queries and queries_failed == len(queries):
            # Partial failure is tolerated (some queries succeeding is enough
            # to proceed); only a total wipeout aborts the run.
            if all(isinstance(err, ResearchProviderTimeoutError) for err in failure_errors):
                raise ResearchProviderTimeoutError(
                    f"All {queries_failed} research search queries timed out"
                )
            raise ResearchProviderError(
                "All research search queries failed: "
                + "; ".join(str(err) for err in failure_errors[:3])
            )

        fallback_backfill_used = 0
        if (
            self._quality_fallback_provider is not None
            and queries
            and self._needs_quality_fallback(search_sources)
        ):
            # Primary results look weak in aggregate (not just "one query
            # technically errored") - backfill with the highest-priority
            # queries against the fallback provider directly, bounded so
            # this never silently doubles the run's cost.
            backfill_queries = sorted(queries, key=lambda q: q.priority or 99)[
                : settings.research_quality_fallback_max_queries
            ]
            backfill_outcomes = await asyncio.gather(
                *(
                    self._run_query(q.query, provider=self._quality_fallback_provider)
                    for q in backfill_queries
                ),
                return_exceptions=True,
            )
            for outcome in backfill_outcomes:
                if isinstance(outcome, BaseException):
                    continue
                search_sources.extend(outcome)
                fallback_backfill_used += 1

        all_raw_sources = link_sources + search_sources
        normalized = normalize_sources(all_raw_sources)
        deduplicated = deduplicate_sources(normalized)

        identity_confidence = aggregate_identity_relevance(deduplicated, guest)
        needs_identity_confirmation = (
            identity_confidence < settings.research_identity_confirmation_threshold
        )

        extraction = await self._extractor.extract(guest, deduplicated)

        research_payload = build_guest_research_payload(
            extraction, deduplicated, identity_confidence=identity_confidence
        )
        research = guest_research_service.create_guest_research(db, guest_id, research_payload)

        fallback_queries_used = (
            getattr(self._search_provider, "fallback_queries_used", 0) + fallback_backfill_used
        )

        return ResearchRunResult(
            guest_research=research,
            search_provider=self._search_provider.provider_name,
            primary_search_provider=self._search_provider.provider_name,
            fallback_search_provider=getattr(
                self._search_provider, "fallback_provider_name", None
            )
            or (
                self._quality_fallback_provider.provider_name
                if self._quality_fallback_provider
                else None
            ),
            fallback_queries_used=fallback_queries_used,
            extractor_provider=self._extractor.provider_name,
            extractor_model=self._extractor.model_name,
            queries_executed=len(queries),
            queries_failed=queries_failed,
            total_sources_found=len(all_raw_sources),
            total_sources_after_deduplication=len(deduplicated),
            identity_confidence=round(identity_confidence, 3),
            needs_identity_confirmation=needs_identity_confirmation,
        )


def _build_single_provider(name: str) -> ResearchSearchProvider:
    if name == "tavily":
        if not settings.tavily_api_key:
            raise ResearchProviderConfigurationError(
                "Provider 'tavily' requires TAVILY_API_KEY, which is not configured"
            )
        return TavilyResearchSearchProvider(
            api_key=settings.tavily_api_key,
            timeout_seconds=settings.research_search_timeout_seconds,
        )
    if name == "exa":
        if not settings.exa_api_key:
            raise ResearchProviderConfigurationError(
                "Provider 'exa' requires EXA_API_KEY, which is not configured"
            )
        return ExaResearchSearchProvider(
            api_key=settings.exa_api_key,
            timeout_seconds=settings.research_search_timeout_seconds,
        )
    if name == "mock":
        return MockResearchSearchProvider()
    raise ResearchProviderConfigurationError(
        f"Unknown search provider '{name}' (supported: mock, tavily, exa)"
    )


def build_search_provider() -> ResearchSearchProvider:
    """Resolve the configured search provider (+ optional fallback).

    RESEARCH_SEARCH_PROVIDER: "mock" (default), "tavily", or "exa".
    RESEARCH_FALLBACK_PROVIDER: optional, same set of values. Only takes
    effect when explicitly set - never assumed silently.

    Mock mode always stays isolated (no fallback wrapping), so unit tests and
    offline development remain deterministic regardless of fallback config.

    If the primary provider can't even be constructed (e.g. a missing API
    key) and a fallback is configured, the fallback is used directly in its
    place - there is no working primary to wrap in that case. If no fallback
    is configured (or the fallback is also unusable), this raises rather
    than silently using the mock - a silent fallback would make it look like
    real research ran when it did not.
    """
    provider_name = (settings.research_search_provider or "mock").strip().lower()

    if provider_name == "mock":
        return MockResearchSearchProvider()

    fallback_name = (settings.research_fallback_provider or "").strip().lower() or None

    try:
        primary = _build_single_provider(provider_name)
    except ResearchProviderConfigurationError:
        if not fallback_name:
            raise
        return _build_single_provider(fallback_name)

    if not fallback_name:
        return primary

    fallback = _build_single_provider(fallback_name)
    return FallbackResearchSearchProvider(primary=primary, fallback=fallback)


def build_quality_fallback_provider() -> ResearchSearchProvider | None:
    """A standalone handle on the configured fallback provider (Phase 14's
    quality-based backfill, distinct from the exception-triggered wrapping
    build_search_provider() already does). None when no fallback is
    configured, or when the primary provider IS the "fallback" provider
    (mock mode, or fallback == primary name) - nothing useful to backfill
    with in that case."""
    provider_name = (settings.research_search_provider or "mock").strip().lower()
    fallback_name = (settings.research_fallback_provider or "").strip().lower() or None
    if provider_name == "mock" or not fallback_name or fallback_name == provider_name:
        return None
    try:
        return _build_single_provider(fallback_name)
    except ResearchProviderConfigurationError:
        return None


def get_research_engine() -> ResearchEngine:
    """Single wiring point for provider/extractor implementations.

    Swap the search provider via RESEARCH_SEARCH_PROVIDER and the extractor
    via RESEARCH_EXTRACTOR_PROVIDER - ResearchEngine itself never changes and
    never knows about a concrete extractor implementation.
    """
    return ResearchEngine(
        search_provider=build_search_provider(),
        extractor=build_research_extractor(),
        quality_fallback_provider=build_quality_fallback_provider(),
    )
