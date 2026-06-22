"""
app/services/v3/content_service.py
Servicio de contenido para WUI v3.
"""

from typing import Optional

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
    PIPELINE_STAGES,
)


STAGE_ORDER = ["idea", "script", "graphic", "video", "published"]


def get_next_stage(current: str) -> Optional[str]:
    try:
        idx = STAGE_ORDER.index(current)
        if idx + 1 < len(STAGE_ORDER):
            return STAGE_ORDER[idx + 1]
        return None
    except ValueError:
        return None


def get_previous_stage(current: str) -> Optional[str]:
    try:
        idx = STAGE_ORDER.index(current)
        if idx > 0:
            return STAGE_ORDER[idx - 1]
        return None
    except ValueError:
        return None


def advance_stage(
    user_id: str,
    channel_id: str,
    content_id: str,
    create_snapshot: bool = True,
) -> dict:
    """
    Avanza el content_item a la siguiente etapa.
    Si create_snapshot=True, crea una versión antes de avanzar.
    """
    content = get_content_item(user_id, channel_id, content_id)
    if not content:
        raise ValueError(f"ContentItem no encontrado: {content_id}")

    next_stage = get_next_stage(content["stage"])
    if not next_stage:
        raise ValueError(f"No se puede avanzar desde la etapa: {content['stage']}")

    if create_snapshot:
        create_version(user_id, channel_id, content_id)

    updated = update_content_item(user_id, channel_id, content_id, {
        "stage": next_stage,
        "status": "in_progress" if next_stage != "published" else "completed",
    })
    if updated is None:
        raise ValueError(f"ContentItem no encontrado tras advance: {content_id}")
    return updated


def revert_stage(
    user_id: str,
    channel_id: str,
    content_id: str,
    target_stage: Optional[str] = None,
) -> dict:
    """
    Revierte el content_item a la etapa anterior o a target_stage.
    Si no se especifica target_stage, revierte una etapa.
    """
    content = get_content_item(user_id, channel_id, content_id)
    if not content:
        raise ValueError(f"ContentItem no encontrado: {content_id}")

    if target_stage is None:
        target_stage = get_previous_stage(content["stage"])
        if not target_stage:
            raise ValueError(f"No se puede retroceder desde la etapa: {content['stage']}")

    # Buscar la versión más reciente que corresponda a la etapa objetivo
    versions = list_versions(user_id, channel_id, content_id)
    target_version = None
    for v in reversed(versions):
        if v.get("stage_snapshot") == target_stage:
            target_version = v
            break

    if target_version:
        revert_to_version(user_id, channel_id, content_id, target_version["version_number"])

    updated = update_content_item(user_id, channel_id, content_id, {
        "stage": target_stage,
        "status": "in_progress",
    })
    if updated is None:
        raise ValueError(f"ContentItem no encontrado tras revert: {content_id}")
    return updated
