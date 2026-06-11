"""Router de automatización."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.automation import (
    AutomationTaskCreate,
    AutomationTaskUpdate,
    AutomationTaskResponse,
    AutomationRunResponse,
    AutomationRunDetailResponse,
)
from app.services.automation_service import AutomationService
from app.models import AutomationRunStep

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.post("/tasks", response_model=AutomationTaskResponse)
def create_task(task: AutomationTaskCreate, db: Session = Depends(get_db)):
    """Crea una nueva tarea de automatización."""
    return AutomationService.create(db, task)


@router.get("/tasks", response_model=list[AutomationTaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """Obtiene todas las tareas de automatización."""
    return AutomationService.get_all(db)


@router.get("/tasks/{task_id}", response_model=AutomationTaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Obtiene una tarea de automatización por ID."""
    task = AutomationService.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@router.put("/tasks/{task_id}", response_model=AutomationTaskResponse)
def update_task(task_id: int, task_update: AutomationTaskUpdate, db: Session = Depends(get_db)):
    """Actualiza una tarea de automatización."""
    task = AutomationService.update(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Elimina una tarea de automatización."""
    success = AutomationService.delete(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"detail": "Tarea eliminada"}


@router.post("/tasks/{task_id}/run", response_model=AutomationRunResponse)
def run_task(task_id: int, db: Session = Depends(get_db)):
    """Lanza la ejecución de una tarea de automatización."""
    try:
        run = AutomationService.run_task(task_id, db)
        return run
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/runs", response_model=list[AutomationRunResponse])
def get_runs(task_id: int | None = Query(None), db: Session = Depends(get_db)):
    """Obtiene ejecuciones de automatización con filtro opcional por tarea."""
    return AutomationService.get_runs(db, task_id)


@router.get("/runs/{run_id}", response_model=AutomationRunDetailResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    """Obtiene una ejecución por ID con sus pasos."""
    run = AutomationService.get_run_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")

    steps = (
        db.query(AutomationRunStep)
        .filter(AutomationRunStep.run_id == run_id)
        .order_by(AutomationRunStep.step_index)
        .all()
    )

    return AutomationRunDetailResponse(
        id=run.id,
        task_id=run.task_id,
        status=run.status,
        started_at=run.started_at,
        finished_at=run.finished_at,
        steps=steps,
    )


@router.post("/runs/{run_id}/retry", response_model=AutomationRunResponse)
def retry_run(run_id: int, db: Session = Depends(get_db)):
    """Reintenta una ejecución fallida."""
    run = AutomationService.retry_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Ejecución no encontrada")
    return run
