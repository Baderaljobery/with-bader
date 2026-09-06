from pydantic import BaseModel


class StatisticsTotals(BaseModel):
    guests: int
    scheduled_interviews: int
    completed_interviews: int
    questions: int
    content_drafts: int
    approved_content: int
    designs: int
    design_slides: int


class PlatformCount(BaseModel):
    platform: str
    count: int


class ActivityPoint(BaseModel):
    date: str
    count: int


class StatisticsOverviewResponse(BaseModel):
    totals: StatisticsTotals
    content_by_platform: list[PlatformCount]
    activity: list[ActivityPoint]
