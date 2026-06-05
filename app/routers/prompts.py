"""Router para la gestión de biblioteca de prompts."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.prompt import Prompt
from app.services.prompt_service import PromptService
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

class PromptCreate(BaseModel):
    title: str
    content: str
    prompt_type: str  # lluvia_ideas, guion, audio, video, seo
    description: Optional[str] = None
    meta_data: Optional[Any] = None

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None

class PromptResponse(BaseModel):
    id: int
    title: str
    content: str
    prompt_type: str
    description: Optional[str]
    variables: list[str]
    rating: float
    usage_count: int
    version: int
    is_active: str
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/")
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    """Crea un nuevo prompt."""
    db_prompt = PromptService.create_prompt(
        db,
        title=prompt.title,
        content=prompt.content,
        prompt_type=prompt.prompt_type,
        description=prompt.description,
        meta_data=prompt.meta_data
    )
    return db_prompt

@router.get("/")
def list_prompts(
    prompt_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los prompts, opcionalmente filtrados por tipo."""
    prompts = PromptService.get_all_prompts(db, prompt_type)
    return prompts

@router.get("/top")
def get_top_prompts(limit: int = 10, db: Session = Depends(get_db)):
    """Obtiene los prompts mejor puntuados."""
    prompts = PromptService.get_top_prompts(db, limit)
    return prompts

@router.get("/search")
def search_prompts(q: str, db: Session = Depends(get_db)):
    """Busca prompts por título o descripción."""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Búsqueda muy corta")
    
    prompts = PromptService.search_prompts(db, q)
    return prompts

@router.get("/{prompt_id}")
def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Obtiene un prompt específico."""
    prompt = PromptService.get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return prompt

@router.patch("/{prompt_id}")
def update_prompt(prompt_id: int, prompt: PromptUpdate, db: Session = Depends(get_db)):
    """Actualiza un prompt."""
    db_prompt = PromptService.update_prompt(
        db,
        prompt_id,
        title=prompt.title,
        content=prompt.content,
        description=prompt.description,
        rating=prompt.rating
    )
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return db_prompt

@router.post("/{prompt_id}/rate")
def rate_prompt(prompt_id: int, rating: float, db: Session = Depends(get_db)):
    """Califica un prompt (0-5)."""
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="La calificación debe estar entre 0 y 5")
    
    db_prompt = PromptService.rate_prompt(db, prompt_id, rating)
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return db_prompt

@router.post("/{prompt_id}/use")
def use_prompt(
    prompt_id: int,
    variables: dict,
    db: Session = Depends(get_db)
):
    """Usa un prompt sustituyendo sus variables."""
    prompt = PromptService.get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    
    # Validar variables
    validation = PromptService.validate_variables(prompt.content, variables)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Variables faltantes: {validation['missing']}"
        )
    
    # Sustituir variables
    final_content = PromptService.substitute_variables(prompt.content, variables)
    
    # Incrementar contador de uso
    PromptService.increment_usage(db, prompt_id)
    
    return {
        "prompt_id": prompt_id,
        "title": prompt.title,
        "original_content": prompt.content,
        "final_content": final_content,
        "variables_used": variables
    }

@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Elimina (marca como inactivo) un prompt."""
    success = PromptService.delete_prompt(db, prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return {"message": "Prompt eliminado"}

@router.post("/{prompt_id}/validate")
def validate_prompt_variables(
    prompt_id: int,
    variables: dict,
    db: Session = Depends(get_db)
):
    """Valida que todas las variables requeridas estén proporcionadas."""
    prompt = PromptService.get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    
    validation = PromptService.validate_variables(prompt.content, variables)
    return validation
