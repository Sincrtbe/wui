"""Modelo de etiqueta."""
from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Tag(Base):
    """Modelo de etiqueta."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
