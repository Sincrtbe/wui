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
                scheduler.add_job(
                    _run_automation_task,
                    "cron",
                    args=[task.id],
                    id=f"task_{task.id}",
                    replace_existing=True,
                    **_parse_cron(task.schedule_expression),
                )
    finally:
        db.close()


def _parse_cron(cron_expr: str) -> dict:
    """Convierte una expresión cron a argumentos de APScheduler."""
    parts = cron_expr.split()
    result = {}
    if len(parts) >= 1:
        result["minute"] = parts[0]
    if len(parts) >= 2:
        result["hour"] = parts[1]
    if len(parts) >= 3:
        result["day"] = parts[2]
    if len(parts) >= 4:
        result["month"] = parts[3]
    if len(parts) >= 5:
        result["day_of_week"] = parts[4]
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
