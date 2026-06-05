"""Dependencias comunes de la aplicación."""
from sqlalchemy.orm import Session
from app.core.database import get_db


def get_session(db: Session = None) -> Session:
    """Obtiene la sesión de BD."""
    return db or next(get_db())
