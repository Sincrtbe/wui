"""Configuración del scheduler de APScheduler."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.core.database import SessionLocal, engine
from app.models import AutomationTask
from app.services.automation_service import AutomationService

scheduler = None


def init_scheduler():
    """Inicializa el scheduler con tareas persistentes."""
    global scheduler

    jobstores = {
        "default": SQLAlchemyJobStore(engine=engine),
    }

    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.start()

    db = SessionLocal()
    try:
        active_tasks = db.query(AutomationTask).filter(AutomationTask.is_active == True).all()
        for task in active_tasks:
            if task.schedule_expression:
                try:
                    scheduler.add_job(
                        _run_automation_task,
                        "cron",
                        args=[task.id],
                        id=f"task_{task.id}",
                        replace_existing=True,
                        **_parse_cron(task.schedule_expression),
                    )
                except ValueError as e:
                    print(f"Advertencia: No se pudo programar tarea {task.id}: {e}")
    finally:
        db.close()


def _parse_cron(cron_expr: str) -> dict:
    """Convierte una expresión cron a argumentos de APScheduler.
    
    Valida que la expresión cron tenga entre 5 campos.
    Lanza ValueError si la expresión es inválida.
    """
    if not cron_expr or not isinstance(cron_expr, str):
        raise ValueError("Expresión cron inválida: debe ser una cadena no vacía")
    
    parts = cron_expr.strip().split()
    
    if len(parts) < 5:
        raise ValueError(f"Expresión cron inválida: se esperan 5 campos, se obtuvieron {len(parts)}")
    
    if len(parts) > 5:
        raise ValueError(f"Expresión cron inválida: se esperan 5 campos, se obtuvieron {len(parts)}")
    
    result = {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }
    
    return result


def _run_automation_task(task_id: int):
    """Ejecuta una tarea de automatización programada."""
    db = SessionLocal()
    try:
        AutomationService.run_task(task_id, db)
    finally:
        db.close()


def shutdown_scheduler():
    """Detiene el scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
