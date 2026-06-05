"""Modelo de programación de publicación."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text, Date
from app.core.database import Base


class PublicationSchedule(Base):
    """Modelo de programación de publicación."""

    __tablename__ = "publication_schedules"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    content_type = Column(String, nullable=True)  # 'long_video', 'short', 'article'
    scheduled_datetime = Column(DateTime, nullable=False)
    status = Column(String, default="planned")  # planned, published, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
