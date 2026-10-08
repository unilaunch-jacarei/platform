import uuid
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from backend.domains.leads.models import CatalogStatus, CompanySize, LeadStatus, LeadType


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


class LeadPrivacyInput(BaseModel):
    privacy_consent: bool = Field(..., description="Must be true to submit a lead")

    @field_validator("privacy_consent")
    @classmethod
    def require_privacy_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("privacy_consent must be true")
        return value


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


class StudentLeadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution_id: uuid.UUID | None = None
    institution_name: str | None = Field(default=None, min_length=2, max_length=255)
    course_id: uuid.UUID | None = None
    course_name: str | None = Field(default=None, min_length=2, max_length=255)
    semester_number: int | None = Field(default=None, ge=1, le=12, strict=True)
    interest_area_ids: list[uuid.UUID] | None = Field(default=None, max_length=3)
    semester: str | None = Field(default=None, max_length=50)
    linkedin_url: HttpUrl | None = Field(default=None, max_length=2048)
    github_url: HttpUrl | None = Field(default=None, max_length=2048)
    area_of_interest: str | None = Field(default=None, max_length=255)
    message: str | None = Field(default=None, max_length=2000)

    @field_validator(
        "institution_name",
        "course_name",
        "semester",
        "area_of_interest",
        "message",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None or not isinstance(value, str):
            return value
        return " ".join(value.split())

    @model_validator(mode="after")
    def validate_catalog_selection(self):
        if (self.institution_id is None) == (self.institution_name is None):
            raise ValueError("send exactly one of institution_id or institution_name")
        if (self.course_id is None) == (self.course_name is None):
            raise ValueError("send exactly one of course_id or course_name")
        if self.semester is not None and self.semester_number is not None:
            raise ValueError("semester and semester_number cannot be sent together")
        if self.area_of_interest is not None and self.interest_area_ids is not None:
            raise ValueError("area_of_interest and interest_area_ids cannot be sent together")
        if self.interest_area_ids is not None and len(set(self.interest_area_ids)) != len(
            self.interest_area_ids
        ):
            raise ValueError("interest_area_ids must be distinct")
        return self


class LeadPublicCreate(LeadContactInput, LeadCompanyInput, LeadPrivacyInput):
    pass


class StudentLeadPublicCreate(LeadContactInput, StudentLeadInput, LeadPrivacyInput):
    pass


class LeadSourceInput(BaseModel):
    source: str = Field(default="direct", min_length=1, max_length=255)

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        return value.strip()


class LeadCreate(LeadPublicCreate, LeadSourceInput):
    lead_type: Literal[LeadType.COMPANY] = LeadType.COMPANY


class StudentLeadCreate(StudentLeadPublicCreate, LeadSourceInput):
    lead_type: Literal[LeadType.STUDENT] = LeadType.STUDENT


class CatalogItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class InterestAreaRead(CatalogItemRead):
    code: str


class CatalogReferenceRead(CatalogItemRead):
    status: CatalogStatus


class CatalogAliasRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class CatalogAdminRead(CatalogReferenceRead):
    aliases: list[CatalogAliasRead]
    merged_into_id: uuid.UUID | None
    reviewed_by_id: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CatalogMergeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: uuid.UUID


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lead_type: LeadType
    full_name: str
    email: EmailStr
    company_name: str | None
    job_title: str | None
    company_size: CompanySize | None
    website: HttpUrl | None
    institution_name: str | None
    course_name: str | None
    semester: str | None
    linkedin_url: HttpUrl | None
    github_url: HttpUrl | None
    area_of_interest: str | None
    institution: CatalogReferenceRead | None
    course: CatalogReferenceRead | None
    semester_number: int | None
    interest_areas: list[InterestAreaRead]
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
