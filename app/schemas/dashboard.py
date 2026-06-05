"""Schemas de dashboard."""
from pydantic import BaseModel
from datetime import datetime


class UpcomingPublicationSummary(BaseModel):
    id: int
    channel_name: str
    channel_color: str
    script_title: str | None
    scheduled_datetime: datetime
    status: str


class ActiveAutomationRunSummary(BaseModel):
    run_id: int
    task_name: str
    status: str
    started_at: datetime | None


class DashboardChannelSummary(BaseModel):
    channel_id: int
    channel_name: str
    channel_color: str | None = None
    description: str | None
    customUrl: str | None
    publishedAt: datetime | None
    topicIds: list[str] | None
    topicCategories: list[str] | None
    thumbnail_file: str | None
    thumbnail_url: str | None
    total_scripts: int
    total_videos: int
    upcoming_publications: int
    pending_publications: int


class PublicationCalendarEvent(BaseModel):
    id: int
    channel_id: int
    channel_name: str
    channel_color: str
    title: str
    date: datetime
    status: str


class DashboardSummary(BaseModel):
    scripts_by_status: dict[str, int]
    videos_by_status: dict[str, int]
    channels_overview: list[DashboardChannelSummary]
    publication_calendar: list[PublicationCalendarEvent]
    active_automation_runs: list[ActiveAutomationRunSummary]

    class Config:
        from_attributes = True
