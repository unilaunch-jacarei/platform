import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from backend.domains.leads.models import CompanySize, LeadStatus


class LeadContactInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return " ".join(value.split())

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class LeadCompanyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(min_length=2, max_length=255)
    job_title: str | None = Field(default=None, max_length=120)
    company_size: CompanySize | None = None
    website: HttpUrl | None = Field(default=None, max_length=2048)
    message: str | None = Field(default=None, max_length=2000)

    @field_validator("company_name", "job_title", "message", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())


class LeadPublicCreate(LeadContactInput, LeadCompanyInput):
    privacy_consent: bool = Field(..., description="Must be true to submit a lead")

    @field_validator("privacy_consent")
    @classmethod
    def require_privacy_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("privacy_consent must be true")
        return value


class LeadCreate(LeadPublicCreate):
    privacy_consent: bool = Field(..., description="Must be true to submit a lead")
    source: str = Field(default="direct", min_length=1, max_length=255)

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        return value.strip()


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    company_name: str
    job_title: str | None
    company_size: CompanySize | None
    website: HttpUrl | None
    message: str | None
    privacy_consent: bool
    privacy_policy_version: str
    privacy_consent_at: datetime
    source: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadSubmissionRead(BaseModel):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadViewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_key: str = Field(min_length=1, max_length=255)
    source: str = Field(default="direct", min_length=1, max_length=255)

    @field_validator("event_key", "source", mode="before")
    @classmethod
    def normalize_value(cls, value: str) -> str:
        return value.strip()
