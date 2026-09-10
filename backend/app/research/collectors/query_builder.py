from app.models.guest import Guest
from app.research.models import ResearchQuery

DEFAULT_MAX_QUERIES = 8

# Bilingual concept phrases per allowed research objective (Phase 9 -
# multilingual search). Deliberately gender-neutral, noun-based Arabic
# phrasing (e.g. "المسيرة المهنية" rather than a gendered possessive like
# "مسيرته") so it reads naturally regardless of the guest's gender. These are
# search-query fragments, not full sentences.
_AR_CONCEPTS = {
    "career": "المسيرة المهنية",
    "achievements": "إنجازات",
    "projects": "مشاريع",
    "public_appearances": "لقاء",
    "recent": "آخر الأخبار",
}
_EN_CONCEPTS = {
    "career": "career",
    "achievements": "achievements",
    "projects": "projects",
    "public_appearances": "interview",
    "recent": "latest news",
}


def _bilingual_name(guest: Guest) -> tuple[str, str]:
    """The guest's Arabic/English name - the only bilingual identity field.
    Falls back to the legacy single-language `name` column for guests
    created before name_ar/name_en existed, so both language slots carry a
    usable value rather than one going empty."""
    name_ar = (getattr(guest, "name_ar", None) or "").strip()
    name_en = (getattr(guest, "name_en", None) or "").strip()
    legacy = (guest.name or "").strip()
    return (name_ar or legacy, name_en or legacy)


def estimate_query_budget(
    guest: Guest, trusted_link_count: int = 0, *, minimum: int = 6, maximum: int = 16
) -> int:
    """Adaptive search budget (Phase 10) - not a fixed number for every
    guest. A guest with little identity information gets a smaller budget
    (less to search for, and less to spend on); a guest with a fuller
    profile and multiple trusted links - a higher-public-profile signal -
    gets a larger one. Always bounded by [minimum, maximum]."""
    name_ar, name_en = _bilingual_name(guest)
    richness = 0
    if name_ar and name_en:
        richness += 1
    if (guest.company or "").strip():
        richness += 1
    if (guest.job_title or "").strip():
        richness += 1
    if (guest.biography or "").strip():
        richness += 1
    richness += min(trusted_link_count, 3)

    if richness <= 2:
        budget = 7  # simple guest: 6-8
    elif richness <= 4:
        budget = 10  # normal guest: 8-12
    else:
        budget = 14  # high-public-profile guest: 12-16

    return max(minimum, min(maximum, budget))


def build_research_queries(
    guest: Guest, max_queries: int = DEFAULT_MAX_QUERIES
) -> list[ResearchQuery]:
    """Build deterministic, rule-based search queries from guest information.

    No AI involved - just simple, reproducible string combinations from
    already-known guest fields. Covers BOTH Arabic and English identity
    (Phase 9) via the guest's bilingual name: an Arabic guest gets
    Arabic-phrased queries, not English suffixes like "interview"/
    "biography" bolted onto an Arabic name. job_title/company are plain
    single-value identity context (not bilingual) appended as-is to both
    language variants. This is the deterministic half of the hybrid
    planner - see app/research/research_planner.py for the AI-assisted
    expansion half.
    """
    name_ar, name_en = _bilingual_name(guest)
    job_title = (guest.job_title or "").strip()
    company = (guest.company or "").strip()

    if not name_ar and not name_en:
        return []

    seen: set[str] = set()
    queries: list[ResearchQuery] = []

    def add(query: str, objective: str, language: str, priority: int) -> None:
        query = " ".join(query.split())
        if query and query not in seen:
            seen.add(query)
            queries.append(
                ResearchQuery(
                    query=query,
                    reason=f"{objective} ({language})",
                    priority=priority,
                    objective=objective,
                    language=language,
                    source="deterministic",
                )
            )

    def add_bilingual(build, objective: str, priority: int) -> None:
        if name_ar:
            add(build(name_ar), objective, "ar", priority)
        if name_en and name_en != name_ar:
            add(build(name_en), objective, "en", priority)

    # Objective: identity - the guest's name alone, and paired with company/role.
    add_bilingual(lambda name: name, "identity", 1)
    add_bilingual(lambda name: f"{name} {company}" if company else name, "identity", 2)
    add_bilingual(lambda name: f"{name} {job_title}" if job_title else name, "identity", 2)

    # Objective: career / achievements / projects / public_appearances / recent -
    # one query per available language per concept.
    for objective in ("career", "achievements", "projects", "public_appearances", "recent"):
        if name_ar:
            add(f"{name_ar} {_AR_CONCEPTS[objective]}", objective, "ar", 3)
        if name_en and name_en != name_ar:
            add(f"{name_en} {_EN_CONCEPTS[objective]}", objective, "en", 3)

    # A combined role+company query, per language, ranks a little lower -
    # useful but the most specific/least likely to surface new sources.
    add_bilingual(
        lambda name: f"{name} {company} {job_title}".strip() if company and job_title else "",
        "identity",
        4,
    )

    queries = [q for q in queries if q.query]
    queries.sort(key=lambda q: q.priority or 0)
    return queries[:max_queries]
