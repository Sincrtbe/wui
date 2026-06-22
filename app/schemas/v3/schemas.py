"""
app/schemas/v3/schemas.py
Schemas Pydantic para la API v3 de WUI.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class PipelineStage(str, Enum):
    IDEA_GENERATION = "idea_generation"
    SCRIPT_WRITING = "script_writing"
    SCENE_GRAPHIC = "scene_graphic"
    SCENE_VIDEO = "scene_video"
    TTS = "tts"


class ContentStage(str, Enum):
    IDEA = "idea"
    SCRIPT = "script"
    GRAPHIC = "graphic"
    VIDEO = "video"
    PUBLISHED = "published"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class NoteType(str, Enum):
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    IMPROVEMENT = "improvement"
    GENERAL = "general"


class ScoreSource(str, Enum):
    YOUTUBE_API = "youtube_api"
    MANUAL = "manual"
    AI_PREDICTED = "ai_predicted"


class ScoreMetric(str, Enum):
    VIEWS = "views"
    CTR = "ctr"
    RETENTION = "retention"
    LIKES_RATIO = "likes_ratio"
    AI_SCORE = "ai_score"


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─────────────────────────────────────────────────────────────────────────────
# Channel
# ─────────────────────────────────────────────────────────────────────────────

class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    platform: str = "youtube"
    platform_id: str = ""
    url: str = ""


class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    platform: Optional[str] = None
    platform_id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    status: Optional[str] = None


class ChannelOut(BaseModel):
    id: str
    user_id: str
    name: str
    platform: str
    platform_id: str
    url: str
    thumbnail: str
    subscribers: int
    description: str
    status: str
    voice_sample_path: str
    created_at: str
    updated_at: str
    last_sync: Optional[str]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────────────────────────

class PromptVariableSchema(BaseModel):
    name: str
    type: str = "string"
    required: bool = False
    description: Optional[str] = ""


class PromptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: str = "custom"
    description: str = ""
    tags: list[str] = []
    variables_schema: list[PromptVariableSchema] = []


class PromptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    variables_schema: Optional[list[PromptVariableSchema]] = None


class PromptOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    content: str
    category: str
    description: str
    tags: list[str]
    variables_schema: list[dict]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PromptRenderRequest(BaseModel):
    prompt_content: str
    context: dict = {}


class PromptRenderResponse(BaseModel):
    rendered: str
    variables_used: list[str]
    variables_missing: list[str]


class PromptValidateResponse(BaseModel):
    valid: bool
    valid_variables: list[str]
    invalid_variables: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Assignments
# ─────────────────────────────────────────────────────────────────────────────

class PipelineAssignmentSet(BaseModel):
    stage: PipelineStage
    prompt_id: str
    channel_id: Optional[str] = None  # None = global del usuario


class PipelineAssignmentOut(BaseModel):
    stage: str
    prompt_id: str
    prompt: Optional[PromptOut] = None


# ─────────────────────────────────────────────────────────────────────────────
# Content Item
# ─────────────────────────────────────────────────────────────────────────────

class ContentItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    channel_id: str
    stage: ContentStage = ContentStage.IDEA
    tags: list[str] = []
    idea_notes: str = ""


class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    stage: Optional[ContentStage] = None
    status: Optional[ContentStatus] = None
    tags: Optional[list[str]] = None
    idea_notes: Optional[str] = None
    script_content: Optional[str] = None
    scene_prompts: Optional[list[dict]] = None
    generated_images: Optional[list[dict]] = None
    generated_videos: Optional[list[dict]] = None
    tts_result: Optional[dict] = None


class ContentItemOut(BaseModel):
    id: str
    user_id: str
    channel_id: str
    parent_id: Optional[str]
    title: str
    stage: str
    status: str
    tags: list[str]
    current_version_id: Optional[str]
    idea_notes: str
    script_content: str
    scene_prompts: list[dict]
    generated_images: list[dict]
    generated_videos: list[dict]
    tts_result: Optional[dict]
    notes: list[dict]
    scores: list[dict]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Notes
# ─────────────────────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    note_type: NoteType
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    note_type: Optional[NoteType] = None
    content: Optional[str] = None
    resolved: Optional[bool] = None


class NoteOut(BaseModel):
    id: str
    user_id: str
    note_type: str
    content: str
    resolved: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Versions
# ─────────────────────────────────────────────────────────────────────────────

class VersionCreate(BaseModel):
    prompt_id: Optional[str] = None
    prompt_version_id: Optional[str] = None


class VersionOut(BaseModel):
    id: str
    content_item_id: str
    version_number: int
    stage_snapshot: str
    data: dict
    prompt_id: Optional[str]
    prompt_version_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Scores
# ─────────────────────────────────────────────────────────────────────────────

class ScoreCreate(BaseModel):
    metric_type: ScoreMetric
    value: float
    source: ScoreSource = ScoreSource.MANUAL
    notes: str = ""


class ScoreOut(BaseModel):
    id: str
    metric_type: str
    value: float
    source: str
    notes: str
    recorded_at: str

    class Config:
        from_attributes = True


class AnalyticsOut(BaseModel):
    content_id: str
    latest_scores: dict[str, float]  # metric_type → latest value
    averages: dict[str, float]  # metric_type → average value
    version_count: int
    notes_summary: dict[str, int]  # note_type → count
