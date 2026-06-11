"""Funciones auxiliares para sincronizar el scheduler con cambios en tareas."""
from app.tasks.scheduler import scheduler, _parse_cron, _run_automation_task, _run_daily_analytics


def sync_analytics_schedule(cron_expr: str):
    """Sincroniza la programación de analíticas diarias."""
    if not scheduler:
        return
    
    job_id = "daily_analytics"
    if not cron_expr:
        try:
            scheduler.remove_job(job_id)
        except:
            pass
        return
    
    try:
        scheduler.add_job(
            _run_daily_analytics,
            "cron",
            id=job_id,
            replace_existing=True,
            **_parse_cron(cron_expr),
        )
    except Exception as e:
        print(f"Error al sincronizar analíticas: {e}")


def sync_task_to_scheduler(task):
    """Sincroniza una tarea de automatización con el scheduler APScheduler.
    
    Si la tarea está activa y tiene una expresión cron, la añade/actualiza en el scheduler.
    Si está inactiva, la elimina del scheduler.
    """
    if not scheduler:
        return
    
    job_id = f"task_{task.id}"
    
    # Si la tarea está inactiva o no tiene expresión cron, eliminar del scheduler
    if not task.is_active or not task.schedule_expression:
        try:
            scheduler.remove_job(job_id)
        except:
            pass  # Job no existe, ignorar
        return
    
    # Si está activa, añadir o actualizar en el scheduler
    try:
        scheduler.add_job(
            _run_automation_task,
            "cron",
            args=[task.id],
            id=job_id,
            replace_existing=True,
            **_parse_cron(task.schedule_expression),
        )
    except Exception as e:
        print(f"Error al sincronizar tarea {task.id} con scheduler: {e}")


def remove_task_from_scheduler(task_id: int):
    """Elimina una tarea del scheduler."""
    if not scheduler:
        return
    
    job_id = f"task_{task_id}"
    try:
        scheduler.remove_job(job_id)
    except:
        pass  # Job no existe, ignorar
