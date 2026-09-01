from urllib.parse import urlsplit

from app.core.config import settings
from app.research.models import NormalizedResearchSource

_AUTHORITATIVE_DOMAIN_HINTS = (
    "wikipedia.org",
    "britannica.com",
    ".gov",
    ".edu",
)


def _host(source: NormalizedResearchSource) -> str:
    url = source.canonical_url or source.url
    if not url:
        return ""
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _is_authoritative(source: NormalizedResearchSource) -> bool:
    host = _host(source)
    return any(hint in host for hint in _AUTHORITATIVE_DOMAIN_HINTS)


def _numeric_score(source: NormalizedResearchSource) -> float:
    score = (source.metadata or {}).get("score")
    return float(score) if isinstance(score, (int, float)) else 0.0


def _rank_key(source: NormalizedResearchSource) -> tuple:
    # Sorted descending: real content, real snippet, authoritative domain,
    # provider score, then a populated title. Deliberately simple/deterministic.
    return (
        bool(source.content),
        bool(source.snippet),
        _is_authoritative(source),
        _numeric_score(source),
        bool(source.title),
    )


def select_sources_for_extraction(
    sources: list[NormalizedResearchSource],
    max_sources: int | None = None,
) -> list[NormalizedResearchSource]:
    """Deterministically pick a bounded, useful subset of sources for the
    extractor - no AI call, no complex ranking engine. Prefers sources with
    real content/snippet, provider score, and authoritative domains, then
    prefers domain diversity before allowing repeats from the same host."""
    limit = max_sources if max_sources is not None else settings.research_extractor_max_sources
    if limit <= 0 or not sources:
        return []

    ranked = sorted(sources, key=_rank_key, reverse=True)

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
