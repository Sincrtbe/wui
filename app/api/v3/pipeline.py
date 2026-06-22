"""
app/api/v3/pipeline.py
Rutas de pipeline: consulta y asignación de prompts a etapas.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.schemas.v3.schemas import PipelineAssignmentSet, PipelineAssignmentOut, PipelineStage, PromptOut
from app.api.v3.auth import get_current_user
from app.core.multiuser_dal import (
    get_pipeline_assignments,
    set_pipeline_assignment,
    remove_pipeline_assignment,
    resolve_pipeline_prompt,
    get_prompt,
    get_system_prompt,
    PIPELINE_STAGES,
)

router = APIRouter()


@router.get("/stages", response_model=list[str])
def list_stages(user: dict = Depends(get_current_user)):
    """Lista todas las etapas disponibles del pipeline."""
    return PIPELINE_STAGES


@router.get("/assignments", response_model=dict[str, str])
def get_my_assignments(
    channel_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """Obtiene las asignaciones de prompts para el usuario (o canal específico)."""
    return get_pipeline_assignments(user["id"], channel_id)


@router.post("/assignments", response_model=dict)
def set_my_assignment(
    body: PipelineAssignmentSet,
    user: dict = Depends(get_current_user),
):
    """Asigna un prompt a una etapa del pipeline (global o por canal)."""
    # Verificar que el prompt existe y pertenece al usuario
    prompt = get_prompt(user["id"], body.prompt_id)
    if not prompt:
        prompt = get_system_prompt(body.prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
    if prompt.get("user_id") and prompt["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este prompt")

    try:
        result = set_pipeline_assignment(
            user_id=user["id"],
            stage=body.stage.value,
            prompt_id=body.prompt_id,
            channel_id=body.channel_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.delete("/assignments/{stage}", response_model=dict)
def remove_my_assignment(
    stage: str,
    channel_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """Elimina una asignación de prompt para una etapa."""
    if stage not in PIPELINE_STAGES:
        raise HTTPException(status_code=400, detail=f"Stage inválido. Debe ser uno de: {PIPELINE_STAGES}")
    result = remove_pipeline_assignment(user["id"], stage, channel_id)
    return result


@router.get("/resolve/{stage}", response_model=Optional[PromptOut])
def resolve_stage_prompt(
    stage: str,
    channel_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """
    Resuelve qué prompt se usará para una etapa (canal → usuario → sistema).
    Retorna null si no hay ningún prompt asignado en ningún nivel.
    """
    if stage not in PIPELINE_STAGES:
        raise HTTPException(status_code=400, detail=f"Stage inválido. Debe ser uno de: {PIPELINE_STAGES}")
    prompt = resolve_pipeline_prompt(user["id"], stage, channel_id)
    if not prompt:
        return None
    return PromptOut(**prompt)
