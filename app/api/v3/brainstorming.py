"""
app/api/v3/brainstorming.py
Ruta para generar lluvias de ideas para un canal.
POST /api/v3/brainstorm/{channel_id}
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v3.auth import get_current_user
from app.services.v3.brainstorming_service import brainstorm_channel


router = APIRouter(prefix="/brainstorm", tags=["brainstorming"])


@router.post("/{channel_id}")
def brainstorm_for_channel(
    channel_id: str,
    provider: str = Query("minimax"),
    extra_topic: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """
    Genera una lluvia de ideas para el canal dado.
    Usa el topic del canal (o extra_topic si se proporciona)
    y el prompt de storming del sistema.
    """
    try:
        content = brainstorm_channel(
            user_id=user["id"],
            channel_id=channel_id,
            provider=provider,
            extra_topic=extra_topic,
        )
        return {"ok": True, "content": content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en brainstorming: {e}")
