"""
app/api/v3/prompts.py
Rutas de prompts: CRUD + renderizado + validación.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from typing import Optional

from app.schemas.v3.schemas import (
    PromptCreate,
    PromptOut,
    PromptUpdate,
    PromptRenderRequest,
    PromptRenderResponse,
    PromptValidateResponse,
)
from app.api.v3.auth import get_current_user
from app.core.multiuser_dal import (
    create_prompt,
    get_prompt,
    list_prompts,
    update_prompt,
    delete_prompt,
    extract_variables,
    validate_variables,
    render_prompt,
    build_render_context,
    list_system_prompts,
    get_system_prompt,
)
from app.services.v3.prompt_service import create_user_prompt

router = APIRouter()


@router.get("", response_model=list[PromptOut])
def list_my_prompts(
    category: str = Query(None),
    tag: str = Query(None),
    user: dict = Depends(get_current_user),
):
    """Lista los prompts del usuario actual, opcionalmente filtrados."""
    prompts = list_prompts(user["id"], category=category, tag=tag)
    return [PromptOut(**p) for p in prompts]


@router.get("/templates", response_model=list[PromptOut])
def list_system_prompt_templates(
    category: str = Query(None),
    user: dict = Depends(get_current_user),
):
    """Lista los prompts default del sistema (plantillas)."""
    prompts = list_system_prompts(category=category)
    return [PromptOut(**p) for p in prompts]


@router.post("", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
def create_my_prompt(body: PromptCreate, user: dict = Depends(get_current_user)):
    """Crea un nuevo prompt para el usuario actual."""
    prompt = create_user_prompt(
        user_id=user["id"],
        name=body.name,
        content=body.content,
        category=body.category,
        description=body.description,
        tags=body.tags,
        variables_schema=[v.model_dump() for v in body.variables_schema],
    )
    return PromptOut(**prompt)


@router.get("/{prompt_id}", response_model=PromptOut)
def get_my_prompt(prompt_id: str, user: dict = Depends(get_current_user)):
    """Obtiene un prompt específico del usuario actual."""
    prompt = get_prompt(user["id"], prompt_id)
    if not prompt:
        # Buscar en system prompts
        prompt = get_system_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
    if prompt.get("user_id") and prompt["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este prompt")
    return PromptOut(**prompt)


@router.put("/{prompt_id}", response_model=PromptOut)
def update_my_prompt(
    prompt_id: str,
    body: PromptUpdate,
    user: dict = Depends(get_current_user),
):
    """Actualiza un prompt del usuario actual."""
    prompt = get_prompt(user["id"], prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    if prompt["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No puedes editar prompts del sistema")
    updates = body.model_dump(exclude_unset=True)
    if "variables_schema" in updates:
        updates["variables_schema"] = [v if isinstance(v, dict) else v.model_dump() for v in updates["variables_schema"]]
    updated = update_prompt(user["id"], prompt_id, updates)
    return PromptOut(**updated)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_prompt(prompt_id: str, user: dict = Depends(get_current_user)):
    """Elimina un prompt del usuario actual."""
    prompt = get_prompt(user["id"], prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt no encontrado")
    if prompt["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No puedes eliminar prompts del sistema")
    delete_prompt(user["id"], prompt_id)


@router.post("/validate", response_model=PromptValidateResponse)
def validate_prompt_variables(body: PromptRenderRequest):
    """Valida las {{{variables}}} de un prompt sin renderizarlo."""
    valid_vars, invalid_vars = validate_variables(body.prompt_content)
    return PromptValidateResponse(
        valid=len(invalid_vars) == 0,
        valid_variables=valid_vars,
        invalid_variables=invalid_vars,
    )


@router.post("/render", response_model=PromptRenderResponse)
def render_prompt_endpoint(
    body: PromptRenderRequest,
    user: dict = Depends(get_current_user),
):
    """Renderiza un prompt con el contexto dado."""
    context = body.context
    valid_vars, invalid_vars = validate_variables(body.prompt_content)
    rendered = render_prompt(body.prompt_content, context)
    return PromptRenderResponse(
        rendered=rendered,
        variables_used=valid_vars,
        variables_missing=[],
    )


@router.post("/render/{channel_id}", response_model=PromptRenderResponse)
def render_prompt_for_channel(
    channel_id: str,
    prompt_id: str,
    content_id: str = Query(None),
    extra_context: Optional[dict] = Body(None),
    user: dict = Depends(get_current_user),
):
    """Renderiza un prompt para un canal y content item específico."""
    # Obtener prompt (usuario o sistema)
    prompt = get_prompt(user["id"], prompt_id)
    if not prompt:
        prompt = get_system_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")

    context = build_render_context(user["id"], channel_id, content_id)
    if extra_context:
        context.update(extra_context)

    valid_vars, _ = validate_variables(prompt["content"])
    rendered = render_prompt(prompt["content"], context)
    return PromptRenderResponse(
        rendered=rendered,
        variables_used=valid_vars,
        variables_missing=[],
    )
