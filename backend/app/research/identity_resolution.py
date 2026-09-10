"""Identity resolution (Phase 11): scores how likely a candidate source is
actually ABOUT this specific guest, rather than a same-named stranger.

Deterministic and explainable on purpose - no AI call, so it's cheap enough
to run over every candidate before ranking/extraction ever sees them. A
trusted user-provided link (app/research/collectors/guest_link_collector.py)
is treated as high-confidence identity evidence by construction: the user
vouched for it directly, so it does not need to pass the same text-matching
bar a search-engine result does.
"""

import re

from app.models.guest import Guest
from app.research.models import NormalizedResearchSource

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _words(value: str | None) -> list[str]:
    if not value:
        return []
    return [w.lower() for w in _WORD_RE.findall(value) if len(w) >= 2]


def _identity_anchors(guest: Guest) -> dict[str, list[str]]:
    """Named anchor groups so a match can be weighted by what it matched -
    a name match matters far more than a company/title match. Only the name
    is bilingual; company/job_title are the existing single-value fields."""
    return {
        "name": _words(guest.name_ar) + _words(guest.name_en) + _words(guest.name),
        "company": _words(guest.company),
        "job_title": _words(guest.job_title),
    }


def _source_text(source: NormalizedResearchSource) -> str:
    parts = [source.title, source.snippet, source.content, source.publisher]
    return " ".join(p for p in parts if p).lower()


def _fraction_matched(anchor_words: list[str], text_words: set[str]) -> float:
    if not anchor_words:
        return 0.0
    unique = set(anchor_words)
    matched = sum(1 for w in unique if w in text_words)
    return matched / len(unique)


def score_identity_relevance(source: NormalizedResearchSource, guest: Guest) -> float:
    """0.0 (unrelated) .. 1.0 (strong identity match). A user-provided
    trusted link (Phase 12) starts from a high floor regardless of text
    content - the guest_link origin itself is the identity signal."""
    if (source.metadata or {}).get("origin") == "guest_link":
        base = 0.9
    else:
        base = 0.0

    text = _source_text(source)
    if not text:
        return base

    text_words = set(_WORD_RE.findall(text))
    anchors = _identity_anchors(guest)

    # Weighted so a name match dominates - a source that never mentions the
    # guest's name at all should never score as a strong identity match no
    # matter how well company/title happen to align.
    name_score = _fraction_matched(anchors["name"], text_words) * 0.7
    company_score = _fraction_matched(anchors["company"], text_words) * 0.2
    title_score = _fraction_matched(anchors["job_title"], text_words) * 0.1

    computed = name_score + company_score + title_score
    return max(base, min(1.0, computed))


def aggregate_identity_relevance(
    sources: list[NormalizedResearchSource], guest: Guest
) -> float:
    """Average identity relevance across a set of sources - used as the
    run-level "is this guest actually identifiable from what we found"
    signal (app/research/research_engine.py)."""
    if not sources:
        return 0.0
    scores = [score_identity_relevance(source, guest) for source in sources]
    return sum(scores) / len(scores)
