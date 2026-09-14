import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from backend.domains.leads.models import CompanySize, LeadStatus


class LeadContactInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class LeadCompanyInput(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    job_title: str | None = Field(default=None, max_length=120)
    company_size: CompanySize | None = None
    website: HttpUrl | None = None
    message: str | None = Field(default=None, max_length=2000)

    @field_validator("company_name", "job_title", "message")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value is not None else None


class LeadCreate(LeadContactInput, LeadCompanyInput):
    privacy_consent: bool = Field(..., description="Must be true to submit a lead")
    source: str = Field(default="direct", max_length=255)

    @field_validator("privacy_consent")
    @classmethod
    def require_privacy_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("privacy_consent must be true")
        return value

    @field_validator("source")
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
    privacy_consent_at: datetime
    source: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadViewCreate(BaseModel):
    event_key: str = Field(min_length=1, max_length=255)
    source: str = Field(default="direct", max_length=255)

    @field_validator("event_key", "source")
    @classmethod
    def normalize_value(cls, value: str) -> str:
        return value.strip()
