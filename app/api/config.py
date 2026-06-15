"""
app/api/config.py
API para gestionar configuración, prompts personalizados y personajes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

from app.api.dependencies import get_current_active_user
from app.services.config_service import (
    get_api_config,
    update_api_config,
    create_custom_prompt,
    get_custom_prompt,
    list_custom_prompts,
    update_custom_prompt,
    delete_custom_prompt,
    assign_prompt_to_tab,
    unassign_prompt_from_tab,
    get_prompts_for_tab,
    create_character,
    get_character,
    list_characters,
    update_character,
    delete_character,
    add_prompt_to_character,
    remove_prompt_from_character,
    get_character_with_prompts,
)

router = APIRouter(prefix="/api/config", tags=["Configuration"])


# ── SCHEMAS ──────────────────────────────────────────────────────────────────

class APIConfigRequest(BaseModel):
    """Configuración de APIs."""
    youtube_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_endpoint: Optional[str] = None
    llm_model: Optional[str] = None
    flux_endpoint: Optional[str] = None
    wan_endpoint: Optional[str] = None
    qwen_endpoint: Optional[str] = None


class APIConfigResponse(BaseModel):
    """Respuesta con configuración de APIs."""
    youtube_api_key: str
    llm_api_key: str
    llm_endpoint: str
    llm_model: str
    flux_endpoint: str
    wan_endpoint: str
    qwen_endpoint: str


class CustomPromptRequest(BaseModel):
    """Solicitud para crear/actualizar un prompt personalizado."""
    name: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    category: str = "general"
    description: str = ""
    assigned_to: List[str] = []


class CustomPromptResponse(BaseModel):
    """Respuesta con datos de un prompt personalizado."""
    id: str
    name: str
    content: str
    category: str
    description: str
    assigned_to: List[str]
    created_at: str
    updated_at: str


class CharacterRequest(BaseModel):
    """Solicitud para crear/actualizar un personaje."""
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    personality: str = ""
    appearance: str = ""
    background: str = ""
    associated_prompts: List[str] = []


class CharacterResponse(BaseModel):
    """Respuesta con datos de un personaje."""
    id: str
    name: str
    description: str
    personality: str
    appearance: str
    background: str
    associated_prompts: List[str]
    created_at: str
    updated_at: str


# ── ENDPOINTS: CONFIGURACIÓN DE APIs ─────────────────────────────────────────

@router.get("/api-config", response_model=APIConfigResponse)
async def get_api_configuration(_user: dict = Depends(get_current_active_user)):
    """Obtiene la configuración actual de APIs."""
    config = get_api_config()
    return APIConfigResponse(**config)


@router.post("/api-config", response_model=APIConfigResponse)
async def update_api_configuration(
    request: APIConfigRequest,
    _user: dict = Depends(get_current_active_user)
):
    """Actualiza la configuración de APIs."""
    config_dict = request.model_dump(exclude_none=True)
    updated = update_api_config(config_dict)
    return APIConfigResponse(**updated)


# ── ENDPOINTS: PROMPTS PERSONALIZADOS ────────────────────────────────────────

@router.post("/prompts", response_model=CustomPromptResponse)
async def create_prompt(
    request: CustomPromptRequest,
    _user: dict = Depends(get_current_active_user)
):
    """Crea un nuevo prompt personalizado."""
    prompt = create_custom_prompt(
        name=request.name,
        content=request.content,
        category=request.category,
        description=request.description,
        assigned_to=request.assigned_to,
    )
    return CustomPromptResponse(**prompt)


@router.get("/prompts", response_model=List[CustomPromptResponse])
async def list_prompts(_user: dict = Depends(get_current_active_user)):
    """Lista todos los prompts personalizados."""
    prompts = list_custom_prompts()
    return [CustomPromptResponse(**p) for p in prompts]


@router.get("/prompts/{prompt_id}", response_model=CustomPromptResponse)
async def get_prompt(
    prompt_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Obtiene un prompt personalizado específico."""
    prompt = get_custom_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return CustomPromptResponse(**prompt)


@router.put("/prompts/{prompt_id}", response_model=CustomPromptResponse)
async def update_prompt(
    prompt_id: str,
    request: CustomPromptRequest,
    _user: dict = Depends(get_current_active_user)
):
    """Actualiza un prompt personalizado."""
    prompt = update_custom_prompt(
        prompt_id,
        name=request.name,
        content=request.content,
        category=request.category,
        description=request.description,
        assigned_to=request.assigned_to,
    )
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return CustomPromptResponse(**prompt)


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Elimina un prompt personalizado."""
    if not delete_custom_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return {"message": "Prompt eliminado"}


@router.post("/prompts/{prompt_id}/assign/{tab_name}")
async def assign_prompt(
    prompt_id: str,
    tab_name: str,
    _user: dict = Depends(get_current_active_user)
):
    """Asigna un prompt a una pestaña."""
    prompt = assign_prompt_to_tab(prompt_id, tab_name)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return CustomPromptResponse(**prompt)


@router.post("/prompts/{prompt_id}/unassign/{tab_name}")
async def unassign_prompt(
    prompt_id: str,
    tab_name: str,
    _user: dict = Depends(get_current_active_user)
):
    """Desasigna un prompt de una pestaña."""
    prompt = unassign_prompt_from_tab(prompt_id, tab_name)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    return CustomPromptResponse(**prompt)


@router.get("/prompts/tab/{tab_name}", response_model=List[CustomPromptResponse])
async def get_tab_prompts(
    tab_name: str,
    _user: dict = Depends(get_current_active_user)
):
    """Obtiene todos los prompts asignados a una pestaña."""
    prompts = get_prompts_for_tab(tab_name)
    return [CustomPromptResponse(**p) for p in prompts]


# ── ENDPOINTS: PERSONAJES ────────────────────────────────────────────────────

@router.post("/characters", response_model=CharacterResponse)
async def create_char(
    request: CharacterRequest,
    _user: dict = Depends(get_current_active_user)
):
    """Crea un nuevo personaje."""
    character = create_character(
        name=request.name,
        description=request.description,
        personality=request.personality,
        appearance=request.appearance,
        background=request.background,
        associated_prompts=request.associated_prompts,
    )
    return CharacterResponse(**character)


@router.get("/characters", response_model=List[CharacterResponse])
async def list_chars(_user: dict = Depends(get_current_active_user)):
    """Lista todos los personajes."""
    characters = list_characters()
    return [CharacterResponse(**c) for c in characters]


@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_char(
    character_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Obtiene un personaje específico."""
    character = get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return CharacterResponse(**character)


@router.put("/characters/{character_id}", response_model=CharacterResponse)
async def update_char(
    character_id: str,
    request: CharacterRequest,
    _user: dict = Depends(get_current_active_user)
):
    """Actualiza un personaje."""
    character = update_character(
        character_id,
        name=request.name,
        description=request.description,
        personality=request.personality,
        appearance=request.appearance,
        background=request.background,
        associated_prompts=request.associated_prompts,
    )
    if not character:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return CharacterResponse(**character)


@router.delete("/characters/{character_id}")
async def delete_char(
    character_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Elimina un personaje."""
    if not delete_character(character_id):
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return {"message": "Personaje eliminado"}


@router.post("/characters/{character_id}/prompts/{prompt_id}")
async def add_char_prompt(
    character_id: str,
    prompt_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Añade un prompt a un personaje."""
    character = add_prompt_to_character(character_id, prompt_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return CharacterResponse(**character)


@router.delete("/characters/{character_id}/prompts/{prompt_id}")
async def remove_char_prompt(
    character_id: str,
    prompt_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Elimina un prompt de un personaje."""
    character = remove_prompt_from_character(character_id, prompt_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return CharacterResponse(**character)


@router.get("/characters/{character_id}/with-prompts")
async def get_char_with_prompts(
    character_id: str,
    _user: dict = Depends(get_current_active_user)
):
    """Obtiene un personaje con todos sus prompts asociados."""
    character = get_character_with_prompts(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return character
