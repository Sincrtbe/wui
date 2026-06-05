"""Router para la gestión de contenido."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.content import ContentItem
from pydantic import BaseModel
from typing import Optional, Any

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
    
    for key, value in content.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item
