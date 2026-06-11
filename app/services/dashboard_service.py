"""Servicio de dashboard."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Script, Video, PublicationSchedule, AutomationRun, AutomationTask, Channel
from app.schemas.dashboard import (
    DashboardSummary,
    UpcomingPublicationSummary,
    ActiveAutomationRunSummary,
    DashboardChannelSummary,
    PublicationCalendarEvent,
)


class DashboardService:
    """Servicio de generación de resumen de dashboard."""

    @staticmethod
    def get_summary(db: Session, channel_id: int | None = None) -> DashboardSummary:
        """Genera el resumen del dashboard."""
        scripts_by_status = {}
        script_query = db.query(Script.status, func.count(Script.id)).group_by(Script.status)
        if channel_id is not None:
            script_query = script_query.filter(Script.channel_id == channel_id)
        for status, count in script_query.all():
            scripts_by_status[status] = count

        videos_by_status = {}
        video_query = db.query(Video.status, func.count(Video.id)).group_by(Video.status)
        if channel_id is not None:
            video_query = video_query.filter(Video.channel_id == channel_id)
        for status, count in video_query.all():
            videos_by_status[status] = count

        channels_query = db.query(Channel)
        if channel_id is not None:
            channels_query = channels_query.filter(Channel.id == channel_id)
        channels = channels_query.all()
        channels_overview = []

        for channel in channels:
            script_count = db.query(func.count(Script.id)).filter(Script.channel_id == channel.id).scalar() or 0
            video_count = db.query(func.count(Video.id)).filter(Video.channel_id == channel.id).scalar() or 0
            upcoming_count = (
                db.query(func.count(PublicationSchedule.id))
                .filter(PublicationSchedule.channel_id == channel.id)
                .filter(PublicationSchedule.scheduled_datetime >= datetime.utcnow())
                .filter(PublicationSchedule.status == "planned")
                .scalar()
                or 0
            )
            pending_count = (
                db.query(func.count(PublicationSchedule.id))
                .filter(PublicationSchedule.channel_id == channel.id)
                .filter(PublicationSchedule.status == "planned")
                .scalar()
                or 0
            )

            thumbnail_url = f"/api/channels/{channel.id}/thumbnail" if channel.thumbnail_file else None

            channels_overview.append(
                DashboardChannelSummary(
                    channel_id=channel.id,
                    channel_name=channel.title,
                    channel_color=channel.color,
                    description=channel.description,
                    customUrl=channel.custom_url,
                    publishedAt=channel.published_at,
                    topicIds=channel.topic_ids,
                    topicCategories=channel.topic_categories,
                    thumbnail_file=channel.thumbnail_file,
                    thumbnail_url=thumbnail_url,
                    total_scripts=script_count,
                    total_videos=video_count,
                    upcoming_publications=upcoming_count,
                    pending_publications=pending_count,
                )
            )

        pub_query = db.query(PublicationSchedule).filter(PublicationSchedule.scheduled_datetime >= datetime.utcnow())
        if channel_id is not None:
            pub_query = pub_query.filter(PublicationSchedule.channel_id == channel_id)
        pub_query = pub_query.order_by(PublicationSchedule.scheduled_datetime).limit(30)
        publication_calendar = []

        for pub in pub_query.all():
            channel = db.query(Channel).filter(Channel.id == pub.channel_id).first()
            script = None
            if pub.script_id is not None:
                script = db.query(Script).filter(Script.id == pub.script_id).first()
            publication_calendar.append(
                PublicationCalendarEvent(
                    id=pub.id,
                    channel_id=pub.channel_id,
                    channel_name=channel.title if channel else "Desconocido",
                    channel_color=channel.color if channel else "#3b82f6",
                    title=script.title if script else pub.notes or "Publicación programada",
                    date=pub.scheduled_datetime,
                    status=pub.status,
                )
            )

        active_runs = db.query(AutomationRun).filter(AutomationRun.status.in_(["pending", "running"])) .all()
        active_automation_runs = []
        for run in active_runs:
            task = db.query(AutomationTask).filter(AutomationTask.id == run.task_id).first()
            active_automation_runs.append(
                ActiveAutomationRunSummary(
                    run_id=run.id,
                    task_name=task.name if task else "Desconocida",
                    status=run.status,
                    started_at=run.started_at,
                )
            )

        return DashboardSummary(
            scripts_by_status=scripts_by_status,
            videos_by_status=videos_by_status,
            channels_overview=channels_overview,
            publication_calendar=publication_calendar,
            active_automation_runs=active_automation_runs,
        )
