from app.research.models import NormalizedResearchSource


def _dedup_key(source: NormalizedResearchSource) -> tuple[str, str]:
    if source.canonical_url:
        return ("url", source.canonical_url)
    if source.url:
        return ("url", source.url)
    return (
        "title_publisher",
        f"{(source.title or '').lower()}|{(source.publisher or '').lower()}",
    )


def _richness_score(source: NormalizedResearchSource) -> int:
    score = 0
    if source.content:
        score += 1
    if source.title:
        score += 1
    if source.publisher:
        score += 1
    if source.published_at:
        score += 1
    score += len(source.metadata or {})
    return score


def deduplicate_sources(
    sources: list[NormalizedResearchSource],
) -> list[NormalizedResearchSource]:
    """Collapse duplicate sources, keeping the richest record per duplicate group.

    Duplicate detection priority: canonical URL, then raw URL, then a
    title+publisher fallback for sources without any URL at all.
    """
    best_by_key: dict[tuple[str, str], NormalizedResearchSource] = {}

    for source in sources:
        key = _dedup_key(source)
        existing = best_by_key.get(key)
        if existing is None or _richness_score(source) > _richness_score(existing):
            best_by_key[key] = source

    return list(best_by_key.values())
