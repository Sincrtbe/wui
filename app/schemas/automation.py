"""Schemas de automatización."""
from pydantic import BaseModel
from datetime import datetime


class AutomationTaskCreate(BaseModel):
    channel_id: int
    name: str
    description: str | None = None
    schedule_expression: str | None = None
    workflow_definition: dict


class AutomationTaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    schedule_expression: str | None = None
    workflow_definition: dict | None = None
    is_active: bool | None = None


class AutomationTaskResponse(BaseModel):
    id: int
    channel_id: int
    name: str
    description: str | None
    schedule_expression: str | None
    workflow_definition: dict
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AutomationRunStepResponse(BaseModel):
    id: int
    run_id: int
    step_index: int
    action: str
    params: dict | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    log: str | None

    class Config:
        from_attributes = True


class AutomationRunResponse(BaseModel):
    id: int
    task_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None

    class Config:
        from_attributes = True


class AutomationRunDetailResponse(BaseModel):
    id: int
    task_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    steps: list[AutomationRunStepResponse] = []

    class Config:
        from_attributes = True
