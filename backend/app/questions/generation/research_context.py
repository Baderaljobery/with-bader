from dataclasses import dataclass
from itertools import zip_longest

from app.core.config import settings
from app.models.guest_research import GuestResearch
from app.questions.generation.models import ResearchContextItem
from app.questions.generation.similarity import meaningful_tokens, normalize_question_text


def _join_fields(*parts: str | None) -> str | None:
    cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
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


def _education_fact(item: dict) -> str | None:
    if not isinstance(item, dict):
        return None
    return _join_fields(
        f"Institution: {item.get('institution')}" if item.get("institution") else None,
        f"Degree: {item.get('degree')}" if item.get("degree") else None,
        f"Field: {item.get('field')}" if item.get("field") else None,
        f"Year: {item.get('year')}" if item.get("year") else None,
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


def _topic_fact(item: object) -> str | None:
    if isinstance(item, str) and item.strip():
        return f"Expertise/topic: {item.strip()}"
    if isinstance(item, dict):
        label = item.get("title") or item.get("name") or item.get("topic")
        if label:
            return _join_fields(
                f"Expertise/topic: {label}",
                f"Details: {item.get('description')}" if item.get("description") else None,
            )
    return None


def _event_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Event: {item['title']}",
        f"Date: {item.get('date')}" if item.get("date") else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
        f"Why interesting: {item.get('why_interesting')}"
        if item.get("why_interesting")
        else None,
    )


def _appearance_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Public appearance: {item['title']}",
        f"Type: {item.get('appearance_type')}" if item.get("appearance_type") else None,
        f"Venue: {item.get('venue')}" if item.get("venue") else None,
        f"Date: {item.get('date')}" if item.get("date") else None,
        f"Details: {item.get('description')}" if item.get("description") else None,
    )


def _angle_fact(item: dict) -> str | None:
    if not isinstance(item, dict) or not item.get("title"):
        return None
    return _join_fields(
        f"Suggested angle: {item['title']}",
        f"Reason: {item.get('reason')}" if item.get("reason") else None,
    )


def _source_urls(item: object) -> list[str]:
    if not isinstance(item, dict):
        return []
    urls = item.get("source_urls")
    return [url for url in urls if isinstance(url, str)] if isinstance(urls, list) else []


_ITEM_BUILDERS = (
    ("career_history", "career_history", _career_fact),
    ("education", "education", _education_fact),
    ("achievement", "achievements", _achievement_fact),
    ("project", "projects", _project_fact),
    ("topic", "topics", _topic_fact),
    ("interesting_event", "interesting_events", _event_fact),
    ("public_appearance", "public_appearances", _appearance_fact),
    ("potential_interview_angle", "potential_interview_angles", _angle_fact),
)


@dataclass
class _ContextCandidate:
    item_type: str
    fact: str
    source_urls: list[str]


def _balanced_candidates(research: GuestResearch) -> list[_ContextCandidate]:
    """Round-robin areas so one long field cannot crowd out other evidence."""
    buckets: list[list[_ContextCandidate]] = []
    for item_type, field_name, builder in _ITEM_BUILDERS:
        bucket: list[_ContextCandidate] = []
        for raw_item in getattr(research, field_name, None) or []:
            fact = builder(raw_item)
            if fact:
                bucket.append(_ContextCandidate(item_type, fact, _source_urls(raw_item)))
        buckets.append(bucket)

    balanced: list[_ContextCandidate] = []
    for row in zip_longest(*buckets):
        balanced.extend(item for item in row if item is not None)
    return balanced


def _overlap(candidate: _ContextCandidate, existing: _ContextCandidate) -> tuple[int, float]:
    left = meaningful_tokens(candidate.fact)
    right = meaningful_tokens(existing.fact)
    if not left or not right:
        return 0, 0.0
    intersection = len(left & right)
    return intersection, intersection / min(len(left), len(right))


def _same_underlying_story(candidate: _ContextCandidate, existing: _ContextCandidate) -> bool:
    if normalize_question_text(candidate.fact) == normalize_question_text(existing.fact):
        return True

    intersection, containment = _overlap(candidate, existing)
    shared_sources = bool(set(candidate.source_urls) & set(existing.source_urls))
    includes_angle = "potential_interview_angle" in {
        candidate.item_type,
        existing.item_type,
    }

    # Angles intentionally restate factual stories. Same-type career/project
    # items require much stronger evidence so distinct roles survive.
    if includes_angle and intersection >= 3 and containment >= 0.33:
        return True
    if candidate.item_type == existing.item_type and candidate.item_type in {
        "career_history",
        "education",
        "project",
        "topic",
    }:
        return False
    if shared_sources and intersection >= 3 and containment >= 0.58:
        return True
    if candidate.item_type != existing.item_type and intersection >= 4 and containment >= 0.72:
        return True
    return False


def _merge_candidate(existing: _ContextCandidate, incoming: _ContextCandidate) -> None:
    existing.source_urls = list(dict.fromkeys([*existing.source_urls, *incoming.source_urls]))
    if (
        existing.item_type == "potential_interview_angle"
        and incoming.item_type != "potential_interview_angle"
    ):
        angle = existing.fact.replace("Suggested angle:", "Related angle:", 1)
        existing.fact = f"{incoming.fact} | {angle}"
        existing.item_type = incoming.item_type
        return
    if incoming.item_type == "potential_interview_angle":
        addition = incoming.fact.replace("Suggested angle:", "Related angle:", 1)
        if normalize_question_text(addition) not in normalize_question_text(existing.fact):
            existing.fact = f"{existing.fact} | {addition}"
    elif len(incoming.fact) > len(existing.fact):
        existing.fact = incoming.fact
        existing.item_type = incoming.item_type


def _cluster_candidates(candidates: list[_ContextCandidate]) -> list[_ContextCandidate]:
    clustered: list[_ContextCandidate] = []
    for candidate in candidates:
        match = next(
            (existing for existing in clustered if _same_underlying_story(candidate, existing)),
            None,
        )
        if match is None:
            clustered.append(candidate)
        else:
            _merge_candidate(match, candidate)
    return clustered


def build_research_context(
    research: GuestResearch,
    max_items: int | None = None,
    max_chars: int | None = None,
) -> list[ResearchContextItem]:
    """Build bounded, diversified context from structured research only.

    Overlapping angle/event representations are merged while distinct roles,
    projects and possible questions about one broad topic remain available.
    Raw provider source bodies are never consumed here.
    """
    limit_items = (
        max_items if max_items is not None else settings.question_generation_max_research_items
    )
    limit_chars = (
        max_chars if max_chars is not None else settings.question_generation_max_input_chars
    )

    candidates = _cluster_candidates(_balanced_candidates(research))
    bounded: list[ResearchContextItem] = []
    total_chars = 0
    for candidate in candidates:
        if len(bounded) >= limit_items:
            break
        next_total = total_chars + len(candidate.fact)
        if bounded and next_total > limit_chars:
            continue
        bounded.append(
            ResearchContextItem(
                id=f"R{len(bounded) + 1}",
                item_type=candidate.item_type,
                fact=candidate.fact,
                source_urls=candidate.source_urls,
            )
        )
        total_chars = next_total
    return bounded
