"""Servicio de gestión de programación de publicaciones."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.models.channel_schedule import ChannelSchedule
from app.models.publication_schedule import PublicationSchedule
from app.models.script import Script
from app.models.channel import Channel


def get_or_create_channel_schedule(db: Session, channel_id: int) -> ChannelSchedule:
    """Obtiene o crea la programación para un canal."""
    schedule = db.query(ChannelSchedule).filter(
        ChannelSchedule.channel_id == channel_id
    ).first()
    
    if not schedule:
        schedule = ChannelSchedule(
            channel_id=channel_id,
            long_video_enabled=False,
            short_video_enabled=False,
            article_enabled=False,
            is_active=False
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
    
    return schedule


def update_channel_schedule(
    db: Session,
    channel_id: int,
    long_video_enabled: bool = False,
    long_video_frequency: int = 3,
    short_video_enabled: bool = False,
    short_video_frequency: int = 1,
    article_enabled: bool = False,
    article_frequency: int = 2,
    start_date: datetime = None,
    is_active: bool = False
) -> ChannelSchedule:
    """Actualiza la programación de un canal."""
    schedule = get_or_create_channel_schedule(db, channel_id)
    
    schedule.long_video_enabled = long_video_enabled
    schedule.long_video_frequency = long_video_frequency
    schedule.short_video_enabled = short_video_enabled
    schedule.short_video_frequency = short_video_frequency
    schedule.article_enabled = article_enabled
    schedule.article_frequency = article_frequency
    schedule.start_date = start_date or datetime.utcnow()
    schedule.is_active = is_active
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


def generate_publication_dates(
    db: Session,
    channel_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[dict]:
    """Genera las fechas de publicación basadas en la programación del canal."""
    schedule = db.query(ChannelSchedule).filter(
        ChannelSchedule.channel_id == channel_id
    ).first()
    
    if not schedule or not schedule.is_active:
        return []
    
    publications = []
    current_date = start_date.date()
    
    while current_date <= end_date.date():
        # Videos largos
        if schedule.long_video_enabled and schedule.long_video_frequency > 0:
            days_since_start = (current_date - schedule.start_date.date()).days
            if days_since_start >= 0 and days_since_start % schedule.long_video_frequency == 0:
                publications.append({
                    "date": current_date,
                    "content_type": "long_video",
                    "scheduled_datetime": datetime.combine(current_date, datetime.min.time()) + timedelta(hours=10)
                })
        
        # Shorts
        if schedule.short_video_enabled and schedule.short_video_frequency > 0:
            days_since_start = (current_date - schedule.start_date.date()).days
            if days_since_start >= 0 and days_since_start % schedule.short_video_frequency == 0:
                publications.append({
                    "date": current_date,
                    "content_type": "short",
                    "scheduled_datetime": datetime.combine(current_date, datetime.min.time()) + timedelta(hours=18)
                })
        
        # Artículos
        if schedule.article_enabled and schedule.article_frequency > 0:
            days_since_start = (current_date - schedule.start_date.date()).days
            if days_since_start >= 0 and days_since_start % schedule.article_frequency == 0:
                publications.append({
                    "date": current_date,
                    "content_type": "article",
                    "scheduled_datetime": datetime.combine(current_date, datetime.min.time()) + timedelta(hours=14)
                })
        
        current_date += timedelta(days=1)
    
    return publications


def create_publication_schedules(
    db: Session,
    channel_id: int,
    start_date: datetime,
    end_date: datetime
) -> List[PublicationSchedule]:
    """Crea las programaciones de publicación para el período especificado."""
    publications = generate_publication_dates(db, channel_id, start_date, end_date)
    
    created_schedules = []
    for pub in publications:
        # Verificar si ya existe una programación para esa fecha y tipo
        existing = db.query(PublicationSchedule).filter(
            PublicationSchedule.channel_id == channel_id,
            PublicationSchedule.scheduled_datetime == pub["scheduled_datetime"],
            PublicationSchedule.content_type == pub["content_type"]
        ).first()
        
        if not existing:
            schedule = PublicationSchedule(
                channel_id=channel_id,
                content_type=pub["content_type"],
                scheduled_datetime=pub["scheduled_datetime"],
                status="planned"
            )
            db.add(schedule)
            created_schedules.append(schedule)
    
    if created_schedules:
        db.commit()
    
    return created_schedules


def get_calendar_events(
    db: Session,
    channel_id: int,
    year: int,
    month: int
) -> List[dict]:
    """Obtiene los eventos del calendario para un canal y mes."""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Obtener publicaciones planificadas
    publications = db.query(PublicationSchedule).filter(
        PublicationSchedule.channel_id == channel_id,
        PublicationSchedule.scheduled_datetime >= start_date,
        PublicationSchedule.scheduled_datetime < end_date
    ).order_by(PublicationSchedule.scheduled_datetime).all()
    
    events = []
    for pub in publications:
        events.append({
            "id": pub.id,
            "date": pub.scheduled_datetime.date().isoformat(),
            "time": pub.scheduled_datetime.strftime("%H:%M"),
            "content_type": pub.content_type or "unknown",
            "status": pub.status or "planned",
            "notes": pub.notes,
            "has_script": pub.script_id is not None
        })
    
    # Obtener programación del canal
    schedule = db.query(ChannelSchedule).filter(
        ChannelSchedule.channel_id == channel_id
    ).first()
    
    if schedule:
        events.append({
            "type": "schedule_info",
            "is_active": schedule.is_active,
            "long_video_enabled": schedule.long_video_enabled,
            "long_video_frequency": schedule.long_video_frequency,
            "short_video_enabled": schedule.short_video_enabled,
            "short_video_frequency": schedule.short_video_frequency,
            "article_enabled": schedule.article_enabled,
            "article_frequency": schedule.article_frequency
        })
    
    return events


def get_upcoming_publications(
    db: Session,
    channel_id: int,
    limit: int = 30
) -> List[dict]:
    """Obtiene las próximas publicaciones de un canal."""
    publications = db.query(PublicationSchedule).filter(
        PublicationSchedule.channel_id == channel_id,
        PublicationSchedule.scheduled_datetime >= datetime.utcnow(),
        PublicationSchedule.status == "planned"
    ).order_by(PublicationSchedule.scheduled_datetime).limit(limit).all()
    
    return [
        {
            "id": pub.id,
            "date": pub.scheduled_datetime.isoformat(),
            "content_type": pub.content_type or "unknown",
            "status": pub.status,
            "notes": pub.notes,
            "has_script": pub.script_id is not None
        }
        for pub in publications
    ]