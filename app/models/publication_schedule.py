"""Modelo de programación de publicación."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text
from app.core.database import Base


class PublicationSchedule(Base):
    """Modelo de programación de publicación."""

    __tablename__ = "publication_schedules"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    scheduled_datetime = Column(DateTime, nullable=False)
    status = Column(String, default="planned")
    notes = Column(Text)
