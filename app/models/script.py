"""Modelo de guión."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base


ScriptTag = Table(
    "script_tags",
    Base.metadata,
    Column("script_id", Integer, ForeignKey("scripts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Script(Base):
    """Modelo de guión."""

    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    voice_script = Column(Text)
    graphic_script = Column(Text)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = relationship("Tag", secondary=ScriptTag, backref="scripts")
