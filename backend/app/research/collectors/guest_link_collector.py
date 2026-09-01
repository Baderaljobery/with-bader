import uuid

from sqlalchemy.orm import Session

from app.research.models import RawResearchSource
from app.services.guest_link_service import get_guest_links

_LABEL_KEYWORDS = (
    ("linkedin", "linkedin"),
    ("youtube", "youtube"),
    ("twitter", "x"),
    ("x.com", "x"),
    ("interview", "interview"),
    ("article", "article"),
    ("company", "company_website"),
    ("website", "website"),
)


def _infer_source_type(label: str) -> str:
    normalized = label.strip().lower()
    for keyword, source_type in _LABEL_KEYWORDS:
        if keyword in normalized:
            return source_type
    return "other"


def collect_guest_link_sources(db: Session, guest_id: uuid.UUID) -> list[RawResearchSource]:
    """Load the guest's existing guest_links and convert them into source candidates.

    Does not fetch the linked pages' contents - it only turns known links into
    research source records for the pipeline to normalize/dedupe later.
    """
    links = get_guest_links(db, guest_id)
    return [
        RawResearchSource(
            source_type=_infer_source_type(link.label),
            url=link.url,
            title=link.label,
            publisher=None,
            published_at=None,
            content=None,
            snippet=None,
            metadata={"origin": "guest_link", "guest_link_id": str(link.id)},
        )
        for link in links
    ]
