import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    nome: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    nome: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    nome: str | None = None
