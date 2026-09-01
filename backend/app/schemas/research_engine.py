import uuid

from pydantic import BaseModel

from app.schemas.guest_research import GuestResearchResponse


class GuestResearchRunResponse(BaseModel):
    research_id: uuid.UUID
    guest_id: uuid.UUID
    version: int
    search_provider: str
    primary_search_provider: str
    fallback_search_provider: str | None = None
    fallback_queries_used: int = 0
    extractor_provider: str
    extractor_model: str | None = None
    queries_executed: int
    queries_failed: int
    total_sources_found: int
    total_sources_after_deduplication: int
    research: GuestResearchResponse
