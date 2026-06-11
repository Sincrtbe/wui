"""Router de guiones."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.script import ScriptCreate, ScriptUpdate, ScriptResponse
from app.services.script_service import ScriptService

router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.post("", response_model=ScriptResponse)
def create_script(script: ScriptCreate, db: Session = Depends(get_db)):
    """Crea un nuevo guión."""
    return ScriptService.create(db, script)


@router.get("", response_model=list[ScriptResponse])
def get_scripts(
    channel_id: int | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Obtiene guiones con filtros opcionales."""
    return ScriptService.get_all(db, channel_id, status, search)


@router.get("/{script_id}", response_model=ScriptResponse)
def get_script(script_id: int, db: Session = Depends(get_db)):
    """Obtiene un guión por ID."""
    script = ScriptService.get_by_id(db, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Guión no encontrado")
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
def update_script(script_id: int, script_update: ScriptUpdate, db: Session = Depends(get_db)):
    """Actualiza un guión."""
    script = ScriptService.update(db, script_id, script_update)
    if not script:
        raise HTTPException(status_code=404, detail="Guión no encontrado")
    return script


@router.delete("/{script_id}")
def delete_script(script_id: int, db: Session = Depends(get_db)):
    """Elimina un guión."""
    success = ScriptService.delete(db, script_id)
    if not success:
        raise HTTPException(status_code=404, detail="Guión no encontrado")
    return {"detail": "Guión eliminado"}
