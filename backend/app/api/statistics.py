from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.statistics import StatisticsOverviewResponse
from app.services import statistics_service

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/overview", response_model=StatisticsOverviewResponse)
def get_statistics_overview(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StatisticsOverviewResponse:
    """Scoped entirely to the authenticated user's own guests/content/
    designs (Part 16) - never a global database total."""
    return statistics_service.get_statistics_overview(db, current_user.id)
