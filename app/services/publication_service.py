"""Servicio de publicaciones."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import PublicationSchedule
from app.schemas.publication import PublicationCreate, PublicationUpdate


class PublicationService:
    """Servicio de gestión de publicaciones."""

    @staticmethod
    def create(db: Session, publication: PublicationCreate) -> PublicationSchedule:
        """Crea una nueva publicación programada."""
        db_publication = PublicationSchedule(
            channel_id=publication.channel_id,
            script_id=publication.script_id,
            scheduled_datetime=publication.scheduled_datetime,
            status="planned",
            notes=publication.notes,
        )
        db.add(db_publication)
        db.commit()
        db.refresh(db_publication)
        return db_publication

    @staticmethod
    def get_all(db: Session, start: datetime | None = None, end: datetime | None = None, channel_id: int | None = None) -> list[PublicationSchedule]:
        """Obtiene publicaciones con filtros opcionales."""
        query = db.query(PublicationSchedule)

        if channel_id is not None:
            query = query.filter(PublicationSchedule.channel_id == channel_id)

        if start is not None:
            query = query.filter(PublicationSchedule.scheduled_datetime >= start)

        if end is not None:
            query = query.filter(PublicationSchedule.scheduled_datetime <= end)

        return query.order_by(PublicationSchedule.scheduled_datetime).all()

    @staticmethod
    def get_by_id(db: Session, publication_id: int) -> PublicationSchedule | None:
        """Obtiene una publicación por ID."""
        return db.query(PublicationSchedule).filter(PublicationSchedule.id == publication_id).first()

    @staticmethod
    def update(db: Session, publication_id: int, publication_update: PublicationUpdate) -> PublicationSchedule | None:
        """Actualiza una publicación."""
        db_publication = db.query(PublicationSchedule).filter(PublicationSchedule.id == publication_id).first()
        if not db_publication:
            return None

        update_data = publication_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_publication, key, value)

        db.commit()
        db.refresh(db_publication)
        return db_publication

    @staticmethod
    def delete(db: Session, publication_id: int) -> bool:
        """Elimina una publicación."""
        db_publication = db.query(PublicationSchedule).filter(PublicationSchedule.id == publication_id).first()
        if not db_publication:
            return False

        db.delete(db_publication)
        db.commit()
        return True
