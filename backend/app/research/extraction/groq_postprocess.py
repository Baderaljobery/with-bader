from app.models.guest import Guest
from app.research.extraction.groq_models import GroqExtractionSchema
from app.research.models import NormalizedResearchSource, ResearchExtractionResult


def _resolve_source_ids(
    source_ids: list[str], indexed_sources: dict[str, NormalizedResearchSource]
) -> tuple[list[str], list[str]]:
    """Keep only IDs that were actually supplied to the model; resolve them
    to durable URLs. An LLM-authored URL is never trusted - only IDs we
    ourselves handed out, mapped back through our own source index."""
    valid_ids: list[str] = []
    urls: list[str] = []
    seen_urls: set[str] = set()

    for source_id in source_ids or []:
        source = indexed_sources.get(source_id)
        if source is None:
            continue
        valid_ids.append(source_id)
        url = source.canonical_url or source.url
        if url and url not in seen_urls:
            urls.append(url)
            seen_urls.add(url)

    return valid_ids, urls


def _dedupe(items: list[dict], key_fn, richness_fn) -> list[dict]:
    best: dict[tuple, dict] = {}
    order: list[tuple] = []
    for item in items:
        key = key_fn(item)
        if key not in best:
            order.append(key)
            best[key] = item
        elif richness_fn(item) > richness_fn(best[key]):
            best[key] = item
    return [best[key] for key in order]


def _item_richness(item: dict) -> tuple:
    return (
        len(item.get("source_urls") or []),
        len(item.get("description") or ""),
        item.get("confidence") or 0.0,
    )


def _title_key(item: dict) -> tuple:
    return ((item.get("title") or "").strip().lower(),)


def _career_key(item: dict) -> tuple:
    return (
        (item.get("company") or "").strip().lower(),
        (item.get("role") or "").strip().lower(),
    )


def _education_key(item: dict) -> tuple:
    return (
        (item.get("institution") or "").strip().lower(),
        (item.get("degree") or "").strip().lower(),
    )


def _process_factual_items(
    raw_items: list, indexed_sources: dict[str, NormalizedResearchSource], key_fn
) -> list[dict]:
    """Factual items (career/education/achievements/projects/events) are
    dropped entirely if none of their cited source_ids survive validation -
    an unsourced factual claim is not persisted."""
    processed: list[dict] = []
    for item in raw_items:
        data = item.model_dump()
        valid_ids, urls = _resolve_source_ids(data.pop("source_ids", []), indexed_sources)
        if not valid_ids:
            continue
        data["source_ids"] = valid_ids
        data["source_urls"] = urls
        processed.append(data)
    return _dedupe(processed, key_fn, _item_richness)


def _process_interview_angles(
    raw_items: list, indexed_sources: dict[str, NormalizedResearchSource]
) -> list[dict]:
    """Angles are not dropped for having zero source_ids - a generic angle
    grounded only in guest-provided metadata is allowed to have none."""
    processed: list[dict] = []
    for item in raw_items:
        data = item.model_dump()
        valid_ids, urls = _resolve_source_ids(data.pop("source_ids", []), indexed_sources)
        data["source_ids"] = valid_ids
        data["source_urls"] = urls
        processed.append(data)
    return _dedupe(processed, _title_key, _item_richness)


def build_extraction_result(
    schema_result: GroqExtractionSchema,
    indexed_sources: dict[str, NormalizedResearchSource],
    guest: Guest,
) -> ResearchExtractionResult:
    """Convert the raw (LLM-produced) schema into the trusted, persisted
    shape: invalid source_ids stripped, ungrounded factual claims dropped,
    source_ids resolved to durable source_urls, duplicates collapsed."""
    career_history = _process_factual_items(
        schema_result.career_history, indexed_sources, _career_key
    )
    education = _process_factual_items(schema_result.education, indexed_sources, _education_key)
    achievements = _process_factual_items(schema_result.achievements, indexed_sources, _title_key)
    projects = _process_factual_items(schema_result.projects, indexed_sources, _title_key)
    interesting_events = _process_factual_items(
        schema_result.interesting_events, indexed_sources, _title_key
    )
    public_appearances = _process_factual_items(
        schema_result.public_appearances, indexed_sources, _title_key
    )
    potential_interview_angles = _process_interview_angles(
        schema_result.potential_interview_angles, indexed_sources
    )

    topics = list(dict.fromkeys(topic.strip() for topic in schema_result.topics if topic and topic.strip()))

    return ResearchExtractionResult(
        role_title=schema_result.role_title or guest.job_title,
        company=schema_result.company or guest.company,
        career_history=career_history,
        education=education,
        achievements=achievements,
        projects=projects,
        topics=topics,
        interesting_events=interesting_events,
        public_appearances=public_appearances,
        potential_interview_angles=potential_interview_angles,
    )
