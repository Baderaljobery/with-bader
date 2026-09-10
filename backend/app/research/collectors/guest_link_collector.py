import asyncio
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.research.collectors.link_content_fetcher import fetch_trusted_link_text
from app.research.models import RawResearchSource
from app.services.guest_link_service import get_guest_links

_LABEL_KEYWORDS = (
    ("linkedin", "linkedin"),
    ("youtube", "youtube"),
    ("twitter", "x"),
    ("x.com", "x"),
    ("x (twitter)", "x"),
    ("instagram", "instagram"),
    ("facebook", "facebook"),
    ("interview", "interview"),
    ("podcast", "podcast"),
    ("article", "article"),
    ("organization", "company_website"),
    ("company", "company_website"),
    ("website", "website"),
)


def _infer_source_type(label: str) -> str:
    normalized = label.strip().lower()
    for keyword, source_type in _LABEL_KEYWORDS:
        if keyword in normalized:
            return source_type
    return "other"


async def _fetch_content(url: str) -> str | None:
    if not settings.research_link_fetch_enabled:
        return None
    return await fetch_trusted_link_text(
        url,
        timeout_seconds=settings.research_link_fetch_timeout_seconds,
        max_bytes=settings.research_link_fetch_max_bytes,
        max_redirects=settings.research_link_fetch_max_redirects,
        max_text_chars=settings.research_link_fetch_max_text_chars,
    )


async def collect_guest_link_sources(db: Session, guest_id: uuid.UUID) -> list[RawResearchSource]:
    """Load the guest's existing guest_links and convert them into
    high-identity-confidence source candidates - fetching a bounded amount
    of real page text where safely possible (Phase 12) so a trusted link is
    actually usable evidence, not just a bare URL that ranks below every
    ordinary search result. One link failing to fetch never blocks the
    others or the research run - it just falls back to URL+label only.
    """
    links = get_guest_links(db, guest_id)
    if not links:
        return []

    contents = await asyncio.gather(*(_fetch_content(link.url) for link in links))

    return [
        RawResearchSource(
            source_type=_infer_source_type(link.label),
            url=link.url,
            title=link.label,
            publisher=None,
            published_at=None,
            content=content,
            snippet=None,
            metadata={"origin": "guest_link", "guest_link_id": str(link.id)},
        )
        for link, content in zip(links, contents, strict=True)
    ]
