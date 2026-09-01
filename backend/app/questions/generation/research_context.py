from app.core.config import settings
from app.models.guest_research import GuestResearch
from app.questions.generation.models import ResearchContextItem


def _join_fields(*parts: str | None) -> str | None:
    cleaned = [str(p).strip() for p in parts if p and str(p).strip()]
    return " | ".join(cleaned) if cleaned else None


def _career_fact(item: dict) -> str | None:
    if not isinstance(item, dict):
        return None
    role, company = item.get("role"), item.get("company")
    start, end = item.get("start_date"), item.get("end_date")
    dates = f"{start or '?'} to {end or 'present'}" if (start or end) else None
    return _join_fields(
        f"Role: {role}" if role else None,
        f"Company: {company}" if company else None,
        f"Dates: {dates}" if dates else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
    )


def _achievement_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Achievement: {item['title']}",
        f"Date: {item.get('date')}" if item.get("date") else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
    )


def _project_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Project: {item['title']}",
        f"Role: {item.get('role')}" if item.get("role") else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
    )


def _event_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Event: {item['title']}",
        f"Date: {item.get('date')}" if item.get("date") else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
        f"Why interesting: {item.get('why_interesting')}" if item.get("why_interesting") else None,
    )


def _angle_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Suggested angle: {item['title']}",
        f"Reason: {item.get('reason')}" if item.get("reason") else None,
    )


def _source_urls(item: dict) -> list[str]:
    if not isinstance(item, dict):
        return []
    urls = item.get("source_urls")
    return [url for url in urls if isinstance(url, str)] if isinstance(urls, list) else []


_ITEM_BUILDERS = (
    ("career_history", "career_history", _career_fact),
    ("achievement", "achievements", _achievement_fact),
    ("project", "projects", _project_fact),
    ("interesting_event", "interesting_events", _event_fact),
    ("potential_interview_angle", "potential_interview_angles", _angle_fact),
)


def build_research_context(
    research: GuestResearch,
    max_items: int | None = None,
    max_chars: int | None = None,
) -> list[ResearchContextItem]:
    """Deterministically compact the latest GuestResearch's already-extracted
    structured fields into a bounded, ID-tagged research context. Reads only
    career_history/achievements/projects/interesting_events/
    potential_interview_angles - never GuestResearch.sources (the raw
    Exa/Tavily retrieval corpus), per the rule that question generation must
    not re-consume raw search content, only completed research."""
    limit_items = (
        max_items if max_items is not None else settings.question_generation_max_research_items
    )
    limit_chars = (
        max_chars if max_chars is not None else settings.question_generation_max_input_chars
    )

    candidates: list[tuple[str, str, list[str]]] = []
    for item_type, field_name, builder in _ITEM_BUILDERS:
        for raw_item in getattr(research, field_name, None) or []:
            fact = builder(raw_item)
            if fact:
                candidates.append((item_type, fact, _source_urls(raw_item)))

    bounded: list[ResearchContextItem] = []
    total_chars = 0
    for item_type, fact, urls in candidates[:limit_items]:
        total_chars += len(fact)
        if bounded and total_chars > limit_chars:
            break
        bounded.append(
            ResearchContextItem(
                id=f"R{len(bounded) + 1}", item_type=item_type, fact=fact, source_urls=urls
            )
        )

    return bounded
