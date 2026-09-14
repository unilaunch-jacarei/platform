import uuid
from datetime import datetime
from enum import StrEnum

from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CompanySize(StrEnum):
    """Supported company-size values sent by the public form."""

    MICRO = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-500"
    ENTERPRISE = "501+"


class LeadStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    DISCARDED = "discarded"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    privacy_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    privacy_consent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="direct")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=LeadStatus.NEW, server_default=LeadStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class LeadPageView(Base):
    __tablename__ = "lead_page_views"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    event_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="direct")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
