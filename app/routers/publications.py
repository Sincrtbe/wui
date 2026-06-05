"""Router de publicaciones."""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.publication import PublicationCreate, PublicationUpdate, PublicationResponse
from app.services.publication_service import PublicationService

router = APIRouter(prefix="/api/publications", tags=["publications"])


@router.post("", response_model=PublicationResponse)
def create_publication(publication: PublicationCreate, db: Session = Depends(get_db)):
    """Crea una nueva publicación programada."""
    return PublicationService.create(db, publication)


@router.get("", response_model=list[PublicationResponse])
def get_publications(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    channel_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """Obtiene publicaciones con filtros opcionales."""
    return PublicationService.get_all(db, start, end, channel_id)


@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    """Obtiene una publicación por ID."""
    publication = PublicationService.get_by_id(db, publication_id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return publication


@router.put("/{publication_id}", response_model=PublicationResponse)
def update_publication(publication_id: int, publication_update: PublicationUpdate, db: Session = Depends(get_db)):
    """Actualiza una publicación."""
    publication = PublicationService.update(db, publication_id, publication_update)
    if not publication:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return publication


@router.delete("/{publication_id}")
def delete_publication(publication_id: int, db: Session = Depends(get_db)):
    """Elimina una publicación."""
    success = PublicationService.delete(db, publication_id)
    if not success:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return {"detail": "Publicación eliminada"}
