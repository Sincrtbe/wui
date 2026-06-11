"""Router para la gestión de contenido."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.content import ContentItem
from pydantic import BaseModel
from typing import Optional, Any
from app.services.file_service import FileService
from app.services.log_service import LogService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/content", tags=["content"])

class ContentCreate(BaseModel):
    channel_id: int
    title: str
    stage: str = "idea"
    idea_notes: Optional[str] = None

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[str] = None
    idea_notes: Optional[str] = None
    script_content: Optional[str] = None
    article_content: Optional[str] = None
    developed_data: Optional[Any] = None
    status: Optional[str] = None

@router.post("/")
def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_item = ContentItem(**content.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Guardar archivo inicial
    if db_item.stage == "idea" and db_item.idea_notes:
        FileService.save_idea(db_item.channel_id, db_item.id, db_item.title, db_item.idea_notes)
    
    LogService.log_content_created(db, db_item.channel_id, db_item.stage, db_item.title)
    
    return db_item

@router.get("/{channel_id}")
def get_channel_content(channel_id: int, stage: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ContentItem).filter(ContentItem.channel_id == channel_id)
    if stage:
        query = query.filter(ContentItem.stage == stage)
    return query.all()

@router.patch("/{item_id}")
def update_content(item_id: int, content: ContentUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    old_stage = db_item.stage
    
    for key, value in content.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    # Guardar archivos físicos según la etapa
    if db_item.stage == "idea" and db_item.idea_notes:
        FileService.save_idea(db_item.channel_id, db_item.id, db_item.title, db_item.idea_notes)
    elif db_item.stage == "script" and db_item.script_content:
        FileService.save_script(db_item.channel_id, db_item.id, db_item.title, db_item.script_content, db_item.article_content)
    elif db_item.stage == "developed" and db_item.developed_data:
        FileService.save_developed(db_item.channel_id, db_item.id, db_item.title, db_item.developed_data)
    
    # Registrar avance de etapa
    if old_stage != db_item.stage:
        LogService.log_content_advanced(db, db_item.channel_id, db_item.title, old_stage, db_item.stage)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.post("/{item_id}/generate-script")
def generate_script_from_idea(item_id: int, db: Session = Depends(get_db)):
    """Genera automáticamente un guión a partir de una idea usando LLM."""
    db_item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    if db_item.stage != "idea":
        raise HTTPException(status_code=400, detail="Solo se pueden generar guiones desde ideas")
    
    result = LLMService.generate_script_from_idea(db, db_item.title, db_item.idea_notes or "")
    
    if not result["success"]:
        LogService.log_event(db, "llm_error", f"Error al generar guión: {result['error']}", "error", channel_id=db_item.channel_id)
        raise HTTPException(status_code=500, detail=f"Error LLM: {result['error']}")
    
    # Actualizar contenido
    db_item.stage = "script"
    db_item.script_content = result["data"].get("script_content", "")
    db_item.article_content = result["data"].get("article_content", "")
    
    # Guardar archivos
    FileService.save_script(db_item.channel_id, db_item.id, db_item.title, db_item.script_content, db_item.article_content)
    
    LogService.log_content_advanced(db, db_item.channel_id, db_item.title, "idea", "script")
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{channel_id}/files/{stage}")
def list_stage_files(channel_id: int, stage: str, db: Session = Depends(get_db)):
    """Lista los archivos físicos en una etapa del canal."""
    if stage not in ["idea", "script", "developed", "video"]:
        raise HTTPException(status_code=400, detail="Etapa inválida")
    
    files = FileService.list_files_in_stage(channel_id, stage)
    return {"stage": stage, "files": files}
