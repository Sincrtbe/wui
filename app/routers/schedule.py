"""Router de gestión de programación de canales."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.services.schedule_service import (
    get_or_create_channel_schedule,
    update_channel_schedule,
    generate_publication_dates,
    create_publication_schedules,
    get_calendar_events,
    get_upcoming_publications
)
from app.models.channel_schedule import ChannelSchedule
from app.models.publication_schedule import PublicationSchedule
from app.models.script import Script

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("/channel/{channel_id}")
def get_channel_schedule(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene la programación de un canal."""
    schedule = get_or_create_channel_schedule(db, channel_id)
    
    return {
        "channel_id": schedule.channel_id,
        "long_video_enabled": schedule.long_video_enabled,
        "long_video_frequency": schedule.long_video_frequency,
        "short_video_enabled": schedule.short_video_enabled,
        "short_video_frequency": schedule.short_video_frequency,
        "article_enabled": schedule.article_enabled,
        "article_frequency": schedule.article_frequency,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active,
        "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None
    }


@router.post("/channel/{channel_id}")
def create_channel_schedule(
    channel_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Crea la programación de un canal."""
    schedule = update_channel_schedule(
        db=db,
        channel_id=channel_id,
        long_video_enabled=data.get("long_video_enabled", False),
        long_video_frequency=data.get("long_video_frequency", 3),
        short_video_enabled=data.get("short_video_enabled", False),
        short_video_frequency=data.get("short_video_frequency", 1),
        article_enabled=data.get("article_enabled", False),
        article_frequency=data.get("article_frequency", 2),
        start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else datetime.utcnow(),
        is_active=data.get("is_active", False)
    )
    
    return {
        "channel_id": schedule.channel_id,
        "long_video_enabled": schedule.long_video_enabled,
        "long_video_frequency": schedule.long_video_frequency,
        "short_video_enabled": schedule.short_video_enabled,
        "short_video_frequency": schedule.short_video_frequency,
        "article_enabled": schedule.article_enabled,
        "article_frequency": schedule.article_frequency,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active
    }


@router.put("/channel/{channel_id}")
def update_channel_schedule(
    channel_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Actualiza la programación de un canal."""
    schedule = update_channel_schedule(
        db=db,
        channel_id=channel_id,
        long_video_enabled=data.get("long_video_enabled", False),
        long_video_frequency=data.get("long_video_frequency", 3),
        short_video_enabled=data.get("short_video_enabled", False),
        short_video_frequency=data.get("short_video_frequency", 1),
        article_enabled=data.get("article_enabled", False),
        article_frequency=data.get("article_frequency", 2),
        start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
        is_active=data.get("is_active", False)
    )
    
    return {
        "channel_id": schedule.channel_id,
        "long_video_enabled": schedule.long_video_enabled,
        "long_video_frequency": schedule.long_video_frequency,
        "short_video_enabled": schedule.short_video_enabled,
        "short_video_frequency": schedule.short_video_frequency,
        "article_enabled": schedule.article_enabled,
        "article_frequency": schedule.article_frequency,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "timezone": schedule.timezone,
        "is_active": schedule.is_active
    }


@router.get("/channel/{channel_id}/calendar")
def get_channel_calendar(
    channel_id: int,
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db)
):
    """Obtiene el calendario de publicaciones de un canal."""
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    events = get_calendar_events(db, channel_id, year, month)
    
    # Separar info de programación de eventos del calendario
    schedule_info = None
    calendar_events = []
    
    for event in events:
        if event.get("type") == "schedule_info":
            schedule_info = event
        else:
            calendar_events.append(event)
    
    return {
        "year": year,
        "month": month,
        "schedule_info": schedule_info,
        "events": calendar_events
    }


@router.get("/channel/{channel_id}/calendar/months")
def get_channel_calendar_months(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene los eventos del calendario para el mes actual y el siguiente."""
    from datetime import datetime
    
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Mes actual y siguiente
    events_current = get_calendar_events(db, channel_id, current_year, current_month)
    
    if current_month == 12:
        next_year = current_year + 1
        next_month = 1
    else:
        next_year = current_year
        next_month = current_month + 1
    
    events_next = get_calendar_events(db, channel_id, next_year, next_month)
    
    # Separar info de programación de eventos
    schedule_info = None
    current_events = []
    next_events = []
    
    for event in events_current:
        if event.get("type") == "schedule_info":
            schedule_info = event
        else:
            current_events.append(event)
    
    for event in events_next:
        if event.get("type") != "schedule_info":
            next_events.append(event)
    
    return {
        "current_month": {
            "year": current_year,
            "month": current_month,
            "events": current_events
        },
        "next_month": {
            "year": next_year,
            "month": next_month,
            "events": next_events
        },
        "schedule_info": schedule_info
    }


@router.post("/channel/{channel_id}/generate")
def generate_schedule(
    channel_id: int,
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db)
):
    """Genera programaciones de publicación para un canal y período."""
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    schedules = create_publication_schedules(db, channel_id, start_date, end_date)
    
    return {
        "created": len(schedules),
        "schedules": [
            {
                "id": s.id,
                "date": s.scheduled_datetime.isoformat(),
                "content_type": s.content_type,
                "status": s.status
            }
            for s in schedules
        ]
    }


@router.get("/channel/{channel_id}/upcoming")
def get_upcoming(
    channel_id: int,
    limit: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtiene las próximas publicaciones de un canal."""
    publications = get_upcoming_publications(db, channel_id, limit)
    
    return publications


@router.post("/publication/{publication_id}/assign-script")
def assign_script_to_publication(
    publication_id: int,
    script_id: int,
    db: Session = Depends(get_db)
):
    """Asocia un guion a una programación de publicación."""
    publication = db.query(PublicationSchedule).filter(
        PublicationSchedule.id == publication_id
    ).first()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    publication.script_id = script_id
    publication.status = "planned"
    
    db.commit()
    db.refresh(publication)
    
    return {
        "id": publication.id,
        "script_id": publication.script_id,
        "status": publication.status
    }


@router.put("/publication/{publication_id}")
def update_publication(
    publication_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Actualiza una programación de publicación."""
    publication = db.query(PublicationSchedule).filter(
        PublicationSchedule.id == publication_id
    ).first()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    if "status" in data:
        publication.status = data["status"]
    if "notes" in data:
        publication.notes = data["notes"]
    if "script_id" in data:
        publication.script_id = data["script_id"]
    if "scheduled_datetime" in data:
        publication.scheduled_datetime = datetime.fromisoformat(data["scheduled_datetime"])
    
    db.commit()
    db.refresh(publication)
    
    return {
        "id": publication.id,
        "channel_id": publication.channel_id,
        "content_type": publication.content_type,
        "scheduled_datetime": publication.scheduled_datetime.isoformat(),
        "status": publication.status,
        "notes": publication.notes,
        "script_id": publication.script_id
    }


@router.delete("/publication/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    """Elimina una programación de publicación."""
    publication = db.query(PublicationSchedule).filter(
        PublicationSchedule.id == publication_id
    ).first()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    db.delete(publication)
    db.commit()
    
    return {"message": "Programación eliminada"}