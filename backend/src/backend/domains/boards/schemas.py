import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from backend.domains.boards.models import TaskPriority


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: datetime | None = Field(default=None)
    position: int = Field(default=0, ge=0)

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_id: uuid.UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    position: int | None = Field(default=None, ge=0)

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    column_id: uuid.UUID
    title: str
    description: str | None
    priority: TaskPriority
    due_date: datetime | None
    position: int
    created_at: datetime
    updated_at: datetime


class BoardColumnCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    board_id: uuid.UUID
    name: str = Field(min_length=1, max_length=100)
    position: int = Field(default=0, ge=0)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return " ".join(value.split())


class BoardColumnUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int | None = Field(default=None, ge=0)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class BoardColumnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    board_id: uuid.UUID
    name: str
    position: int
    tasks: list[TaskRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class BoardCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class BoardUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    owner_id: uuid.UUID
    columns: list[BoardColumnRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
