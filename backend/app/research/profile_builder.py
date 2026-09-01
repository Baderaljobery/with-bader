from app.core.config import settings
from app.research.models import NormalizedResearchSource, ResearchExtractionResult
from app.schemas.guest_research import GuestResearchCreate, ResearchSource


def _truncate(text: str | None, limit: int) -> str | None:
    if text is None:
        return None
    return text if len(text) <= limit else text[:limit]


def _to_research_source(source: NormalizedResearchSource) -> ResearchSource:
    """Persistence shape for one source. Preserves the richer provider-returned
    fields (snippet/content/provider/score/query) so a future LLM extractor
    has something to work with - while URL/title/publisher stay untruncated
    and freeform text is bounded to avoid dumping huge blobs into JSONB."""
    limit = settings.research_source_content_max_chars
    metadata = source.metadata or {}

    return ResearchSource(
        type=source.source_type,
        url=source.canonical_url or source.url,
        title=source.title,
        publisher=source.publisher,
        published_at=source.published_at,
        snippet=_truncate(source.snippet, limit),
        content=_truncate(source.content, limit),
        provider=metadata.get("provider"),
        score=metadata.get("score"),
        query=metadata.get("query"),
        notes=None,
    )


def build_guest_research_payload(
    extraction: ResearchExtractionResult,
    sources: list[NormalizedResearchSource],
) -> GuestResearchCreate:
    """Convert the extraction result + normalized sources into the payload
    shape expected by the existing guest_research storage model."""
    return GuestResearchCreate(
        role_title=extraction.role_title,
        company=extraction.company,
        career_history=extraction.career_history,
        education=extraction.education,
        achievements=extraction.achievements,
        projects=extraction.projects,
        topics=extraction.topics,
        interesting_events=extraction.interesting_events,
        potential_interview_angles=extraction.potential_interview_angles,
        sources=[_to_research_source(source) for source in sources],
        raw_ai_response=extraction.raw_ai_response,
    )
