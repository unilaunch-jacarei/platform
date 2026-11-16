import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.domains.gamification.models import AchievementCode, WorkSessionStatus, WorkType


class WorkSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_type: WorkType


class WorkSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_type: WorkType
    status: WorkSessionStatus
    total_seconds: int
    started_at: datetime
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class WorkSessionIntervalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int


class WorkTypeProgressRead(BaseModel):
    work_type: WorkType
    total_seconds: int
    total_hours: float


class AchievementRead(BaseModel):
    code: AchievementCode
    name: str
    description: str
    required_level: int
    unlocked: bool
    unlocked_at: datetime | None = None


class ProgressRead(BaseModel):
    user_id: uuid.UUID
    total_seconds: int
    total_hours: float
    current_level: int
    current_level_name: str
    next_level: int | None
    next_level_name: str | None
    seconds_to_next_level: int
    work_types: list[WorkTypeProgressRead]


class HourEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_type: WorkType
    seconds_delta: int
    source_type: str
    source_id: uuid.UUID | None
    description: str | None
    created_at: datetime


class HourAdjustmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_type: WorkType
    seconds_delta: int = Field(..., ne=0)
    reason: str = Field(min_length=1, max_length=1000)


class HourAdjustmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    admin_id: uuid.UUID
    work_type: WorkType
    seconds_delta: int
    reason: str
    created_at: datetime
