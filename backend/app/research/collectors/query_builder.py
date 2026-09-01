from app.models.guest import Guest
from app.research.models import ResearchQuery

DEFAULT_MAX_QUERIES = 8


def build_research_queries(
    guest: Guest, max_queries: int = DEFAULT_MAX_QUERIES
) -> list[ResearchQuery]:
    """Build deterministic, rule-based search queries from guest information.

    No AI involved - just simple, reproducible string combinations from
    already-known guest fields.
    """
    name = (guest.name or "").strip()
    job_title = (guest.job_title or "").strip()
    company = (guest.company or "").strip()

    if not name:
        return []

    seen: set[str] = set()
    queries: list[ResearchQuery] = []

    def add(query: str, reason: str, priority: int) -> None:
        query = query.strip()
        if query and query not in seen:
            seen.add(query)
            queries.append(ResearchQuery(query=query, reason=reason, priority=priority))

    add(name, "Basic guest identity search", 1)
    if company:
        add(f"{name} {company}", "Guest and company association", 2)
    if job_title:
        add(f"{name} {job_title}", "Guest role search", 2)
    add(f"{name} interview", "Existing interview coverage", 3)
    add(f"{name} biography", "Biographical background", 3)
    add(f"{name} achievements", "Notable achievements", 4)
    if company and job_title:
        add(f"{name} {company} {job_title}", "Combined role and company", 4)
    if company:
        add(f"{name} {company} interview", "Company-specific interview coverage", 5)
    add(f"{name} news", "Recent news coverage", 5)

    queries.sort(key=lambda q: q.priority or 0)
    return queries[:max_queries]
