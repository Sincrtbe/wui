"""
app/api/creative.py
API del módulo Creative Studio.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.api.dependencies import get_current_active_user
from app.services.creative_service import (
    list_available_templates,
    get_prompt_template,
    render_template,
    get_model_config,
)

router = APIRouter(prefix="/api/creative", tags=["Creative Studio"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class PromptRequest(BaseModel):
    """Solicitud para generar un prompt."""
    template_name: str = Field(..., min_length=1, description="Nombre de la plantilla (ej: 'storming')")
    variables: dict = Field(default_factory=dict, description="Variables para la plantilla")
    custom_prompt_id: Optional[str] = None
    character_id: Optional[str] = None
    
    # Campos opcionales según el tipo de template
    tema: Optional[str] = None
    titulo: Optional[str] = None
    concepto: Optional[str] = None
    ideas: Optional[str] = None
    descripcion_escena: Optional[str] = None
    momento: Optional[str] = None
    prompt_imagen: Optional[str] = None
    texto_a_visualizar: Optional[str] = None
    lista_ideas: Optional[str] = None


class PromptResponse(BaseModel):
    """Respuesta con el prompt generado."""
    template_name: str
    display_name: str
    prompt: str
    model_suggested: str  # qwen, flux, o wan


class TemplateInfo(BaseModel):
    """Información de una plantilla."""
    name: str
    display_name: str
    description: str
    content: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/templates", response_model=list[TemplateInfo])
async def list_templates(_user: dict = Depends(get_current_active_user)):
    """Lista todas las plantillas de prompts disponibles."""
    templates = list_available_templates()
    return [TemplateInfo(**t) for t in templates]


@router.get("/templates/{template_name}", response_model=TemplateInfo)
async def get_template(template_name: str, _user: dict = Depends(get_current_active_user)):
    """Obtiene una plantilla específica con su contenido."""
    template = get_prompt_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Plantilla no encontrada: {template_name}")
    
    return TemplateInfo(
        name=template_name,
        display_name=f"🎨 {template_name.replace('_', ' ').title()}",
        description=f"Plantilla para {template_name}",
        content=template,
    )


@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(request: PromptRequest, _user: dict = Depends(get_current_active_user)):
    """
    Genera un prompt rellenando una plantilla con variables.
    Soporta inyección de prompts personalizados y contexto de personajes.
    
    Los prompts generados están optimizados para:
    - Qwen3 35B A3B → Textos, guiones, lluvia de ideas
    - Flux 2.0 → Imágenes estáticas
    - Wan 2.2 → Videos cortos
    """
    from app.services.config_service import get_custom_prompt, get_character
    
    # Construir variables completas
    variables = {**request.variables}
    for key, value in request.model_dump().items():
        if key not in ("template_name", "variables", "custom_prompt_id", "character_id") and value is not None:
            variables[key] = value
    
    # Inyectar contexto de personaje si está disponible
    context_prefix = ""
    if request.character_id:
        character = get_character(request.character_id)
        if character:
            context_prefix = f"""Personaje: {character.get('name', '')}
            Descripción: {character.get('description', '')}
            Personalidad: {character.get('personality', '')}
            Apariencia: {character.get('appearance', '')}
            Trasfondo: {character.get('background', '')}
            
            """
    
    # Inyectar prompt personalizado si está disponible
    if request.custom_prompt_id:
        custom_prompt = get_custom_prompt(request.custom_prompt_id)
        if custom_prompt:
            context_prefix += f"Instrucción personalizada: {custom_prompt.get('content', '')}\n\n"
    
    # Generar el prompt
    try:
        prompt = render_template(request.template_name, variables)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Agregar contexto al inicio del prompt
    if context_prefix:
        prompt = context_prefix + prompt
    
    # Determinar modelo sugerido
    model_map = {
        "storming": "qwen",
        "development": "qwen",
        "classification": "qwen",
        "scene_graphic": "flux",
        "scene_video": "wan",
        "conversation_to_visual": "qwen+flux+wan",
    }
    model_suggested = model_map.get(request.template_name, "qwen")
    
    return PromptResponse(
        template_name=request.template_name,
        display_name=f"🎨 {request.template_name.replace('_', ' ').title()}",
        prompt=prompt,
        model_suggested=model_suggested,
    )


@router.get("/models", response_model=dict)
async def get_models(_user: dict = Depends(get_current_active_user)):
    """Devuelve la configuración de modelos disponibles."""
    return get_model_config()
