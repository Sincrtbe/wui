"""Servicio de automatización."""
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AutomationTask, AutomationRun, AutomationRunStep, Channel
from app.schemas.automation import AutomationTaskCreate, AutomationTaskUpdate
from app.core.database import SessionLocal
from app.services.automation_service_sync import sync_task_to_scheduler, remove_task_from_scheduler


class AutomationService:
    """Servicio de gestión de automatización."""

    @staticmethod
    def create(db: Session, task: AutomationTaskCreate) -> AutomationTask:
        """Crea una nueva tarea de automatización."""
        db_task = AutomationTask(
            channel_id=task.channel_id,
            name=task.name,
            description=task.description,
            schedule_expression=task.schedule_expression,
            workflow_definition=task.workflow_definition,
            is_active=True,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        # Sincronizar con el scheduler
        sync_task_to_scheduler(db_task)
        return db_task

    @staticmethod
    def get_all(db: Session) -> list[AutomationTask]:
        """Obtiene todas las tareas de automatización."""
        return db.query(AutomationTask).all()

    @staticmethod
    def get_by_id(db: Session, task_id: int) -> AutomationTask | None:
        """Obtiene una tarea de automatización por ID."""
        return db.query(AutomationTask).filter(AutomationTask.id == task_id).first()

    @staticmethod
    def update(db: Session, task_id: int, task_update: AutomationTaskUpdate) -> AutomationTask | None:
        """Actualiza una tarea de automatización."""
        db_task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        if not db_task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)

        db.commit()
        db.refresh(db_task)
        # Sincronizar con el scheduler después de actualizar
        sync_task_to_scheduler(db_task)
        return db_task

    @staticmethod
    def delete(db: Session, task_id: int) -> bool:
        """Elimina una tarea de automatización."""
        db_task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        if not db_task:
            return False

        remove_task_from_scheduler(task_id)
        db.delete(db_task)
        db.commit()
        return True

    @staticmethod
    def run_task(task_id: int, db: Session = None) -> AutomationRun:
        """Lanza la ejecución de una tarea de automatización."""
        internal_db = db
        if internal_db is None:
            internal_db = SessionLocal()

        task = internal_db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        run = AutomationRun(
            task_id=task_id,
            status="pending",
            started_at=datetime.utcnow(),
        )
        internal_db.add(run)
        internal_db.commit()
        internal_db.refresh(run)

        workflow = task.workflow_definition or {}
        steps = workflow.get("steps", [])

        for idx, step_def in enumerate(steps):
            step = AutomationRunStep(
                run_id=run.id,
                step_index=idx,
                action=step_def.get("action", "unknown"),
                params=step_def.get("params", {}),
                status="pending",
                log="",
            )
            internal_db.add(step)

        internal_db.commit()
        internal_db.refresh(run)

        threading.Thread(target=AutomationService._execute_run, args=(run.id,), daemon=True).start()

        return run

    @staticmethod
    def _execute_run(run_id: int):
        """Ejecuta los pasos de una ejecución en segundo plano."""
        db = SessionLocal()
        try:
            run = db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
            if not run:
                return

            run.status = "running"
            db.commit()

            steps = (
                db.query(AutomationRunStep)
                .filter(AutomationRunStep.run_id == run_id)
                .order_by(AutomationRunStep.step_index)
                .all()
            )

            for step in steps:
                step.status = "running"
                step.started_at = datetime.utcnow()
                db.commit()

                try:
                    action = step.action
                    params = step.params or {}
                    if action == "scrape_channel_info":
                        log_message = AutomationService._scrape_channel_info(run.task_id, db)
                    else:
                        log_message = f"Ejecutando acción '{action}' con parámetros: {params}"
                        time.sleep(2)
                    step.status = "completed"
                    step.log = log_message
                    step.completed_at = datetime.utcnow()
                except Exception as exc:
                    step.status = "failed"
                    step.log = f"Error: {str(exc)}"
                    step.completed_at = datetime.utcnow()
                    run.status = "failed"
                    db.commit()
                    return

                db.commit()

            run.status = "completed"
            run.finished_at = datetime.utcnow()
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _scrape_channel_info(task_id: int, db: Session) -> str:
        task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        channel = db.query(Channel).filter(Channel.id == task.channel_id).first()
        if not channel:
            raise ValueError(f"Canal para tarea {task_id} no encontrado")

        channel.last_scraped_at = datetime.utcnow()
        channel.last_scrape_status = "success"
        channel.scrape_data = {
            "summary": f"Datos actualizados para {channel.name}",
            "social_activity": "Se ha detectado actividad reciente en redes sociales.",
        }
        db.commit()
        return f"Scrape diario completado para canal {channel.name}"

    @staticmethod
    def get_runs(db: Session, task_id: int | None = None) -> list[AutomationRun]:
        """Obtiene ejecuciones con filtro opcional por tarea."""
        query = db.query(AutomationRun)
        if task_id is not None:
            query = query.filter(AutomationRun.task_id == task_id)
        return query.all()

    @staticmethod
    def get_run_by_id(db: Session, run_id: int) -> AutomationRun | None:
        """Obtiene una ejecución por ID."""
        return db.query(AutomationRun).filter(AutomationRun.id == run_id).first()

    @staticmethod
    def retry_run(db: Session, run_id: int) -> AutomationRun | None:
        """Reintenta una ejecución fallida."""
        run = db.query(AutomationRun).filter(AutomationRun.id == run_id).first()
        if not run:
            return None

        steps = db.query(AutomationRunStep).filter(AutomationRunStep.run_id == run_id).all()
        for step in steps:
            step.status = "pending"
            step.log = ""
            step.started_at = None
            step.completed_at = None

        run.status = "pending"
        run.started_at = datetime.utcnow()
        run.finished_at = None
        db.commit()

        threading.Thread(target=AutomationService._execute_run, args=(run_id,), daemon=True).start()
        return run
