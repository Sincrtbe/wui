"""Modelos de automatización."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from app.core.database import Base


class AutomationTask(Base):
    """Modelo de tarea de automatización."""

    __tablename__ = "automation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    schedule_expression = Column(String)
    workflow_definition = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AutomationRun(Base):
    """Modelo de ejecución de automatización."""

    __tablename__ = "automation_runs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("automation_tasks.id"), nullable=False)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)


class AutomationRunStep(Base):
    """Modelo de paso en ejecución de automatización."""

    __tablename__ = "automation_run_steps"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("automation_runs.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    params = Column(JSON)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    log = Column(Text)
