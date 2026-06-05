"""Modelo de vídeo."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base


class Video(Base):
    """Modelo de vídeo."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=True)
    title = Column(String, nullable=False)
    duration = Column(Integer)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)
