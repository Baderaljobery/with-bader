import uuid
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content_draft import CONTENT_PLATFORMS, ContentDraft
from app.models.design_draft import DesignDraft
from app.models.design_slide import DesignSlide
from app.models.guest import Guest
from app.models.guest_transcript import GuestTranscript
from app.models.question import Question
from app.schemas.statistics import ActivityPoint, PlatformCount, StatisticsOverviewResponse, StatisticsTotals

ACTIVITY_WINDOW_DAYS = 30


def _count_owned(db: Session, model, user_id: uuid.UUID, *extra_where) -> int:
    """Every metric here reaches Guest.created_by through a join - none of
    these tables get their own user_id column (Part 13: ownership flows
    through Guest, not a user_id sprinkled onto every table)."""
    stmt = select(func.count()).select_from(model).join(Guest, model.guest_id == Guest.id).where(
        Guest.created_by == user_id, *extra_where
    )
    return db.scalar(stmt) or 0


def _get_totals(db: Session, user_id: uuid.UUID) -> StatisticsTotals:
    design_slides_count = db.scalar(
        select(func.count())
        .select_from(DesignSlide)
        .join(DesignDraft, DesignSlide.design_draft_id == DesignDraft.id)
        .join(Guest, DesignDraft.guest_id == Guest.id)
        .where(Guest.created_by == user_id)
    ) or 0

    return StatisticsTotals(
        guests=db.scalar(select(func.count()).select_from(Guest).where(Guest.created_by == user_id)) or 0,
        scheduled_interviews=db.scalar(
            select(func.count())
            .select_from(Guest)
            .where(Guest.created_by == user_id, Guest.interview_scheduled_at.is_not(None))
        )
        or 0,
        # "Completed interview" = a guest has a real, persisted transcript
        # (app/models/guest_transcript.py, one row per guest, produced by
        # the actual STT pipeline) - the most concrete existing signal that
        # an interview genuinely happened, unlike the manually-set
        # Guest.preparation_status enum, which nothing in the product
        # actually sets today.
        completed_interviews=_count_owned(db, GuestTranscript, user_id),
        questions=_count_owned(db, Question, user_id),
        content_drafts=_count_owned(db, ContentDraft, user_id),
        approved_content=_count_owned(db, ContentDraft, user_id, ContentDraft.status == "approved"),
        designs=_count_owned(db, DesignDraft, user_id),
        design_slides=design_slides_count,
    )


def _get_content_by_platform(db: Session, user_id: uuid.UUID) -> list[PlatformCount]:
    rows = db.execute(
        select(ContentDraft.platform, func.count())
        .join(Guest, ContentDraft.guest_id == Guest.id)
        .where(Guest.created_by == user_id)
        .group_by(ContentDraft.platform)
    ).all()
    counts = dict(rows)
    # Always return all 4 platforms, in a fixed order, even at zero - a
    # stable shape for the frontend's chart rather than an omission the UI
    # would have to guess the meaning of.
    return [PlatformCount(platform=platform, count=counts.get(platform, 0)) for platform in CONTENT_PLATFORMS]


def _get_activity_trend(db: Session, user_id: uuid.UUID) -> list[ActivityPoint]:
    today = date.today()
    start_day = today - timedelta(days=ACTIVITY_WINDOW_DAYS - 1)
    range_start = datetime.combine(start_day, time.min)

    counts_by_day: dict[date, int] = defaultdict(int)

    # Guest itself is scoped directly by created_by; ContentDraft/DesignDraft
    # reach it through their own guest_id join (same reasoning as _count_owned).
    guest_rows = db.execute(
        select(func.date(Guest.created_at), func.count())
        .where(Guest.created_by == user_id, Guest.created_at >= range_start)
        .group_by(func.date(Guest.created_at))
    ).all()
    content_rows = db.execute(
        select(func.date(ContentDraft.created_at), func.count())
        .join(Guest, ContentDraft.guest_id == Guest.id)
        .where(Guest.created_by == user_id, ContentDraft.created_at >= range_start)
        .group_by(func.date(ContentDraft.created_at))
    ).all()
    design_rows = db.execute(
        select(func.date(DesignDraft.created_at), func.count())
        .join(Guest, DesignDraft.guest_id == Guest.id)
        .where(Guest.created_by == user_id, DesignDraft.created_at >= range_start)
        .group_by(func.date(DesignDraft.created_at))
    ).all()

    for rows in (guest_rows, content_rows, design_rows):
        for day_value, count in rows:
            day = day_value if isinstance(day_value, date) else day_value.date()
            counts_by_day[day] += count

    return [
        ActivityPoint(
            date=(start_day + timedelta(days=offset)).isoformat(),
            count=counts_by_day.get(start_day + timedelta(days=offset), 0),
        )
        for offset in range(ACTIVITY_WINDOW_DAYS)
    ]


def get_statistics_overview(db: Session, user_id: uuid.UUID) -> StatisticsOverviewResponse:
    return StatisticsOverviewResponse(
        totals=_get_totals(db, user_id),
        content_by_platform=_get_content_by_platform(db, user_id),
        activity=_get_activity_trend(db, user_id),
    )
