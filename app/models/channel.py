"""Modelo de canal."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base


class Channel(Base):
    """Modelo de canal de YouTube."""

    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    # Campos del JSON del script
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    custom_url = Column(String, nullable=True, unique=True)
    published_at = Column(DateTime, nullable=True)
    topic_ids = Column(JSON, default=list)
    topic_categories = Column(JSON, default=list)
    # Archivo de miniatura (nombre del archivo .jpg en channels_data/)
    thumbnail_file = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)