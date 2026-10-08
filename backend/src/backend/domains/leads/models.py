import uuid
from datetime import datetime
from enum import StrEnum

from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class LeadType(StrEnum):
    COMPANY = "company"
    STUDENT = "student"


class CatalogStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    MERGED = "merged"


class EducationalInstitution(Base):
    __tablename__ = "educational_institutions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'merged')",
            name="ck_educational_institutions_status",
        ),
        CheckConstraint(
            "merged_into_id IS NULL OR merged_into_id <> id",
            name="ck_educational_institutions_not_self_merged",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CatalogStatus.PENDING, index=True
    )
    merged_into_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("educational_institutions.id", ondelete="RESTRICT"), nullable=True
    )
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    aliases: Mapped[list["EducationalInstitutionAlias"]] = relationship(
        back_populates="institution", cascade="all, delete-orphan", lazy="raise"
    )


class EducationalInstitutionAlias(Base):
    __tablename__ = "educational_institution_aliases"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("educational_institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    institution: Mapped[EducationalInstitution] = relationship(
        back_populates="aliases", lazy="raise"
    )


class AcademicCourse(Base):
    __tablename__ = "academic_courses"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'merged')", name="ck_academic_courses_status"
        ),
        CheckConstraint(
            "merged_into_id IS NULL OR merged_into_id <> id",
            name="ck_academic_courses_not_self_merged",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CatalogStatus.PENDING, index=True
    )
    merged_into_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("academic_courses.id", ondelete="RESTRICT"), nullable=True
    )
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    aliases: Mapped[list["AcademicCourseAlias"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="raise"
    )


class AcademicCourseAlias(Base):
    __tablename__ = "academic_course_aliases"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("academic_courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    course: Mapped[AcademicCourse] = relationship(back_populates="aliases", lazy="raise")


class InterestArea(Base):
    __tablename__ = "interest_areas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint(
            "company_size IS NULL OR company_size IN "
            "('1-10', '11-50', '51-200', '201-500', '501+')",
            name="ck_leads_company_size",
        ),
        CheckConstraint(
            "status IN ('new', 'contacted', 'qualified', 'converted', 'discarded')",
            name="ck_leads_status",
        ),
        CheckConstraint("privacy_consent = true", name="ck_leads_privacy_consent"),
        CheckConstraint("lead_type IN ('company', 'student')", name="ck_leads_type"),
        CheckConstraint(
            "semester_number IS NULL OR semester_number BETWEEN 1 AND 12",
            name="ck_leads_semester_number",
        ),
        CheckConstraint(
            "(lead_type = 'company' AND company_name IS NOT NULL) OR "
            "(lead_type = 'student' AND institution_name IS NOT NULL "
            "AND course_name IS NOT NULL)",
            name="ck_leads_type_required_fields",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    lead_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=LeadType.COMPANY, server_default=LeadType.COMPANY
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    institution_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    course_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    semester: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    area_of_interest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("educational_institutions.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("academic_courses.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    semester_number: Mapped[int | None] = mapped_column(nullable=True, index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    privacy_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    privacy_policy_version: Mapped[str] = mapped_column(
        String(50), nullable=False, default="v1.0", server_default="v1.0"
    )
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

    institution: Mapped[EducationalInstitution | None] = relationship(lazy="raise")
    course: Mapped[AcademicCourse | None] = relationship(lazy="raise")
    interest_area_links: Mapped[list["LeadInterestArea"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", lazy="raise"
    )
    interest_areas: Mapped[list[InterestArea]] = relationship(
        secondary="lead_interest_areas", viewonly=True, lazy="raise"
    )


class LeadInterestArea(Base):
    __tablename__ = "lead_interest_areas"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True
    )
    interest_area_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("interest_areas.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lead: Mapped[Lead] = relationship(back_populates="interest_area_links", lazy="raise")
    interest_area: Mapped[InterestArea] = relationship(lazy="raise")


class LeadPageView(Base):
    __tablename__ = "lead_page_views"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    event_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="direct")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
