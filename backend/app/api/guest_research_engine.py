import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.research.extraction.base import (
    ResearchExtractionError,
    ResearchExtractorConfigurationError,
    ResearchExtractorTimeoutError,
)
from app.research.providers.base import (
    ResearchProviderConfigurationError,
    ResearchProviderError,
    ResearchProviderTimeoutError,
)
from app.research.research_engine import ResearchEngine, get_research_engine
from app.schemas.guest_research import GuestResearchResponse
from app.schemas.research_engine import GuestResearchRunResponse
from app.services import guest_service

router = APIRouter(prefix="/api/guests/{guest_id}/research", tags=["guest-research"])


def _resolve_research_engine() -> ResearchEngine:
    """FastAPI-aware wrapper around get_research_engine().

    A misconfigured search provider (e.g. RESEARCH_SEARCH_PROVIDER=tavily
    without TAVILY_API_KEY) or a misconfigured extractor (an unsupported
    RESEARCH_EXTRACTOR_PROVIDER) must fail clearly rather than silently
    falling back, so this converts either into a clean 500 before it ever
    reaches the endpoint body.
    """
    try:
        return get_research_engine()
    except (ResearchProviderConfigurationError, ResearchExtractorConfigurationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post(
    "/run", response_model=GuestResearchRunResponse, status_code=status.HTTP_201_CREATED
)
async def run_guest_research(
    guest_id: uuid.UUID,
    db: Session = Depends(get_db),
    engine: ResearchEngine = Depends(_resolve_research_engine),
) -> GuestResearchRunResponse:
    try:
        result = await engine.run_guest_research(guest_id, db)
    except guest_service.GuestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ResearchProviderTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ResearchProviderConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except ResearchProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except ResearchExtractorTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ResearchExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return GuestResearchRunResponse(
        research_id=result.guest_research.id,
        guest_id=guest_id,
        version=result.guest_research.version,
        search_provider=result.search_provider,
        primary_search_provider=result.primary_search_provider,
        fallback_search_provider=result.fallback_search_provider,
        fallback_queries_used=result.fallback_queries_used,
        extractor_provider=result.extractor_provider,
        extractor_model=result.extractor_model,
        queries_executed=result.queries_executed,
        queries_failed=result.queries_failed,
        total_sources_found=result.total_sources_found,
        total_sources_after_deduplication=result.total_sources_after_deduplication,
        research=GuestResearchResponse.model_validate(result.guest_research),
    )
