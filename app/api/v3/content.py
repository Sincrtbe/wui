"""
app/api/v3/content.py
Rutas de content items: CRUD + advance/revert + notes + scores + versions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.schemas.v3.schemas import (
    ContentItemCreate,
    ContentItemOut,
    ContentItemUpdate,
    NoteCreate,
    NoteOut,
    NoteUpdate,
    ScoreCreate,
    ScoreOut,
    VersionCreate,
    VersionOut,
    AnalyticsOut,
)
from app.api.v3.auth import get_current_user
from app.core.multiuser_dal import (
    create_content_item,
    get_content_item,
    list_content_items,
    update_content_item,
    delete_content_item,
    create_version,
    get_version,
    list_versions,
    revert_to_version,
    add_note,
    update_note,
    delete_note,
    add_score,
    get_scores,
    get_channel,
    PIPELINE_STAGES,
)
from app.services.v3.content_service import advance_stage, revert_stage

router = APIRouter()


# ─── Content Items ────────────────────────────────────────────────────────────

@router.get("", response_model=list[ContentItemOut])
def list_my_content(
    channel_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    user: dict = Depends(get_current_user),
):
    """Lista content items del usuario actual (opcionalmente filtrados por canal/stage/status)."""
    items = list_content_items(user["id"], channel_id=channel_id, stage=stage, status=status_filter)
    return [ContentItemOut(**item) for item in items]


@router.post("", response_model=ContentItemOut, status_code=status.HTTP_201_CREATED)
def create_my_content(body: ContentItemCreate, user: dict = Depends(get_current_user)):
    """Crea un nuevo content item en el canal indicado."""
    # Verificar que el canal existe y pertenece al usuario
    channel = get_channel(user["id"], body.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    item = create_content_item(
        user_id=user["id"],
        channel_id=body.channel_id,
        title=body.title,
        stage=body.stage,
        tags=body.tags,
        idea_notes=body.idea_notes,
    )
    return ContentItemOut(**item)


@router.get("/{content_id}", response_model=ContentItemOut)
def get_my_content(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Obtiene un content item específico."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    if item["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este contenido")
    return ContentItemOut(**item)


@router.put("/{content_id}", response_model=ContentItemOut)
def update_my_content(
    content_id: str,
    body: ContentItemUpdate,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Actualiza un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    if item["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este contenido")
    updated = update_content_item(user["id"], channel_id, content_id, body.model_dump(exclude_unset=True))
    return ContentItemOut(**updated)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_content(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Elimina un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    if item["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este contenido")
    delete_content_item(user["id"], channel_id, content_id)


# ─── Stage Navigation ────────────────────────────────────────────────────────

@router.post("/{content_id}/advance", response_model=ContentItemOut)
def advance_my_content(
    content_id: str,
    channel_id: str = Query(...),
    create_snapshot: bool = Query(True),
    user: dict = Depends(get_current_user),
):
    """Avanza el content item a la siguiente etapa (idea → script → graphic → video → published)."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    try:
        updated = advance_stage(user["id"], channel_id, content_id, create_snapshot=create_snapshot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ContentItemOut(**updated)


@router.post("/{content_id}/revert", response_model=ContentItemOut)
def revert_my_content(
    content_id: str,
    channel_id: str = Query(...),
    target_stage: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """Revierte el content item a la etapa anterior (o a target_stage si se especifica)."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    try:
        updated = revert_stage(user["id"], channel_id, content_id, target_stage=target_stage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ContentItemOut(**updated)


# ─── Versions ────────────────────────────────────────────────────────────────

@router.get("/{content_id}/versions", response_model=list[VersionOut])
def list_my_versions(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Lista todas las versiones de un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    versions = list_versions(user["id"], channel_id, content_id)
    return [VersionOut(**v) for v in versions]


@router.post("/{content_id}/versions", response_model=VersionOut, status_code=status.HTTP_201_CREATED)
def create_my_version(
    content_id: str,
    channel_id: str = Query(...),
    body: VersionCreate = VersionCreate(),
    user: dict = Depends(get_current_user),
):
    """Crea una nueva versión (snapshot) del content item actual."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    version = create_version(
        user_id=user["id"],
        channel_id=channel_id,
        content_id=content_id,
        prompt_id=body.prompt_id,
        prompt_version_id=body.prompt_version_id,
    )
    return VersionOut(**version)


@router.get("/{content_id}/versions/{version_number}", response_model=VersionOut)
def get_my_version(
    content_id: str,
    version_number: int,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Obtiene una versión específica."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    version = get_version(user["id"], channel_id, content_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Versión no encontrada")
    return VersionOut(**version)


@router.post("/{content_id}/revert/{version_number}", response_model=ContentItemOut)
def revert_my_version(
    content_id: str,
    version_number: int,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Revierte el content item al estado de una versión específica."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    reverted = revert_to_version(user["id"], channel_id, content_id, version_number)
    if not reverted:
        raise HTTPException(status_code=404, detail="Versión no encontrada")
    updated = update_content_item(user["id"], channel_id, content_id, reverted)
    return ContentItemOut(**updated)


# ─── Notes ───────────────────────────────────────────────────────────────────

@router.get("/{content_id}/notes", response_model=list[NoteOut])
def list_my_notes(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Lista las notas de un content item (visibles en todos los stages)."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    return [NoteOut(**n) for n in item.get("notes", [])]


@router.post("/{content_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_my_note(
    content_id: str,
    channel_id: str = Query(...),
    body: NoteCreate = NoteCreate,
    user: dict = Depends(get_current_user),
):
    """Añade una nota al content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    note = add_note(
        user_id=user["id"],
        channel_id=channel_id,
        content_id=content_id,
        note_type=body.note_type,
        content=body.content,
    )
    if not note:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    return NoteOut(**note)


@router.put("/{content_id}/notes/{note_id}", response_model=NoteOut)
def update_my_note(
    content_id: str,
    note_id: str,
    channel_id: str = Query(...),
    body: NoteUpdate = NoteUpdate,
    user: dict = Depends(get_current_user),
):
    """Actualiza una nota."""
    updated = update_note(
        user_id=user["id"],
        channel_id=channel_id,
        content_id=content_id,
        note_id=note_id,
        updates=body.model_dump(exclude_unset=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return NoteOut(**updated)


@router.delete("/{content_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_note(
    content_id: str,
    note_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Elimina una nota."""
    deleted = delete_note(user["id"], channel_id, content_id, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Nota no encontrada")


# ─── Scores ─────────────────────────────────────────────────────────────────

@router.get("/{content_id}/scores", response_model=list[ScoreOut])
def list_my_scores(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Lista los scores de un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    return [ScoreOut(**s) for s in item.get("scores", [])]


@router.post("/{content_id}/scores", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
def create_my_score(
    content_id: str,
    channel_id: str = Query(...),
    body: ScoreCreate = ScoreCreate,
    user: dict = Depends(get_current_user),
):
    """Registra un score para un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    score = add_score(
        user_id=user["id"],
        channel_id=channel_id,
        content_id=content_id,
        metric_type=body.metric_type,
        value=body.value,
        source=body.source,
        notes=body.notes,
    )
    if not score:
        raise HTTPException(status_code=404, detail="Content item no encontrado")
    return ScoreOut(**score)


@router.get("/{content_id}/analytics", response_model=AnalyticsOut)
def get_my_analytics(
    content_id: str,
    channel_id: str = Query(...),
    user: dict = Depends(get_current_user),
):
    """Obtiene analytics agregados de un content item."""
    item = get_content_item(user["id"], channel_id, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item no encontrado")

    scores = item.get("scores", [])
    versions = list_versions(user["id"], channel_id, content_id)

    # latest scores por metric_type
    latest = {}
    for s in scores:
        mt = s["metric_type"]
        if mt not in latest:
            latest[mt] = s["value"]

    # averages
    totals: dict = {}
    counts: dict = {}
    for s in scores:
        mt = s["metric_type"]
        totals[mt] = totals.get(mt, 0) + s["value"]
        counts[mt] = counts.get(mt, 0) + 1
    averages = {mt: totals[mt] / counts[mt] for mt in totals}

    # notes summary
    notes_summary: dict = {}
    for n in item.get("notes", []):
        nt = n["note_type"]
        notes_summary[nt] = notes_summary.get(nt, 0) + 1

    return AnalyticsOut(
        content_id=content_id,
        latest_scores=latest,
        averages=averages,
        version_count=len(versions),
        notes_summary=notes_summary,
    )
