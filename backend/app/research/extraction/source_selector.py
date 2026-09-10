from urllib.parse import urlsplit

from app.core.config import settings
from app.models.guest import Guest
from app.research.identity_resolution import score_identity_relevance
from app.research.models import NormalizedResearchSource

# Source quality tiers (Phase 16) - a coarse authority signal, not a
# universal ranking on its own (claim type still matters more than tier;
# this is one input among several in _rank_key below, not the deciding one).
_TIER_A_HINTS = (".gov", ".edu")  # official/government/education
_TIER_B_HINTS = (
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "wsj.com",
    "forbes.com",
    "aljazeera.net",
    "aljazeera.com",
    "bbc.com",
    "cnbc.com",
    "arabianbusiness.com",
    "thenationalnews.com",
)
_TIER_C_HINTS = ("wikipedia.org", "britannica.com", "linkedin.com", "crunchbase.com")


def _host(source: NormalizedResearchSource) -> str:
    url = source.canonical_url or source.url
    if not url:
        return ""
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _source_tier(source: NormalizedResearchSource) -> int:
    """3 (best) .. 0 (unclassified/low). Directness beats tier - a direct
    official/company source or a trusted user link outranks a Tier A/B
    publication about the same fact, which is why this is only one signal
    in _rank_key, not the primary sort key."""
    if (source.metadata or {}).get("origin") == "guest_link":
        return 3  # user-vouched-for, first-class evidence (Phase 12)
    host = _host(source)
    if any(hint in host for hint in _TIER_A_HINTS):
        return 3
    if any(hint in host for hint in _TIER_B_HINTS):
        return 2
    if any(hint in host for hint in _TIER_C_HINTS):
        return 1
    return 0


def _numeric_score(source: NormalizedResearchSource) -> float:
    score = (source.metadata or {}).get("score")
    return float(score) if isinstance(score, (int, float)) else 0.0


def _rank_key(source: NormalizedResearchSource, guest: Guest) -> tuple:
    # Sorted descending. Identity relevance leads - a source that isn't
    # actually about this guest should never outrank one that is, no matter
    # how "authoritative" its domain looks (Phase 15: "do not automatically
    # rank Wikipedia above a strong primary source" cuts both ways - a
    # mismatched-identity Wikipedia page ranks below a well-matched one).
    return (
        round(score_identity_relevance(source, guest), 2),
        bool(source.content),
        bool(source.snippet),
        _source_tier(source),
        _numeric_score(source),
        bool(source.title),
    )


def select_sources_for_extraction(
    sources: list[NormalizedResearchSource],
    guest: Guest,
    max_sources: int | None = None,
    min_identity_relevance: float | None = None,
) -> list[NormalizedResearchSource]:
    """Deterministically pick a bounded, useful subset of sources for the
    extractor - no AI ranking call, no complex ranking engine. Drops
    sources whose identity relevance falls below the configured floor
    (Phase 11 - "do not treat every search result containing the same name
    as valid"), then prefers identity-matched, content-rich, higher-tier
    sources, with domain diversity before allowing repeats from the same
    host."""
    limit = max_sources if max_sources is not None else settings.research_extractor_max_sources
    if limit <= 0 or not sources:
        return []

    floor = (
        min_identity_relevance
        if min_identity_relevance is not None
        else settings.research_identity_min_relevance
    )
    plausible = [s for s in sources if score_identity_relevance(s, guest) >= floor]
    if not plausible:
        # Nothing cleared the identity bar - better to extract from nothing
        # (the caller/engine surfaces "identity confirmation required") than
        # to hand the extractor a set of likely-wrong-person sources.
        return []

    ranked = sorted(plausible, key=lambda s: _rank_key(s, guest), reverse=True)

    selected: list[NormalizedResearchSource] = []
    selected_ids: set[int] = set()
    seen_hosts: set[str] = set()

    for source in ranked:
        if len(selected) >= limit:
            break
        host = _host(source)
        if host and host in seen_hosts:
            continue
        selected.append(source)
        selected_ids.add(id(source))
        if host:
            seen_hosts.add(host)

    if len(selected) < limit:
        for source in ranked:
            if len(selected) >= limit:
                break
            if id(source) in selected_ids:
                continue
            selected.append(source)
            selected_ids.add(id(source))

    return selected


def assign_source_ids(
    sources: list[NormalizedResearchSource],
) -> dict[str, NormalizedResearchSource]:
    """Deterministic S1..Sn IDs, in selection order. These IDs are only ever
    meaningful within one extraction call - the LLM cites them, never a URL."""
    return {f"S{index + 1}": source for index, source in enumerate(sources)}


def bounded_source_text(source: NormalizedResearchSource, max_chars: int | None = None) -> str | None:
    """Content first, snippet only if content is unavailable - never both,
    to avoid sending the same text twice."""
    limit = max_chars if max_chars is not None else settings.research_extractor_max_source_chars
    text = source.content or source.snippet
    if not text:
        return None
    return text if len(text) <= limit else text[:limit]
