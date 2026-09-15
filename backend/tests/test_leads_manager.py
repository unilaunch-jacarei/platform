import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
from backend.domains.leads.manager import LeadService
from backend.domains.leads.models import CompanySize, Lead, LeadStatus, LeadType
from backend.domains.leads.schemas import (
    LeadCreate,
    LeadStatusUpdate,
    LeadViewCreate,
    StudentLeadCreate,
    StudentLeadPublicCreate,
)
from backend.error import NotFoundError


@pytest_asyncio.fixture
async def lead_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


def lead_data() -> LeadCreate:
    return LeadCreate(
        full_name="Ada Lovelace",
        email="ADA@example.com",
        company_name="Analytical Engines",
        company_size=CompanySize.SMALL,
        website="https://example.com",
        privacy_consent=True,
        source="linkedin",
    )


@pytest.mark.asyncio
async def test_create_list_and_update_lead(lead_session: AsyncSession):
    service = LeadService()

    lead = await service.create(lead_session, lead_data())
    assert lead.email == "ada@example.com"
    assert lead.website == "https://example.com/"
    assert lead.lead_type == LeadType.COMPANY
    assert lead.status == LeadStatus.NEW

    leads = await service.list(lead_session)
    assert [item.id for item in leads] == [lead.id]

    found = await service.get(lead_session, lead.id)
    assert found.id == lead.id

    updated = await service.update_status(
        lead_session, lead.id, LeadStatusUpdate(status=LeadStatus.CONTACTED)
    )
    assert updated.status == LeadStatus.CONTACTED


@pytest.mark.asyncio
async def test_record_page_view_is_idempotent(lead_session: AsyncSession):
    service = LeadService()
    data = LeadViewCreate(event_key="request-1", source="instagram")

    first, created = await service.record_page_view(lead_session, data)
    second, duplicate = await service.record_page_view(lead_session, data)

    assert created is True
    assert duplicate is False
    assert first.id == second.id


@pytest.mark.asyncio
async def test_get_missing_lead_raises(lead_session: AsyncSession):
    with pytest.raises(NotFoundError):
        await LeadService().get(lead_session, uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_and_purge_leads(lead_session: AsyncSession):
    service = LeadService()
    old_lead = await service.create(lead_session, lead_data())
    old_lead.created_at = datetime.now(UTC) - timedelta(days=400)
    await lead_session.commit()

    assert await service.purge_before(lead_session, datetime.now(UTC) - timedelta(days=365)) == 1

    current_lead = await service.create(lead_session, lead_data())
    await service.delete(lead_session, current_lead.id)
    with pytest.raises(NotFoundError):
        await service.get(lead_session, current_lead.id)


def test_lead_schema_rejects_without_privacy_consent():
    with pytest.raises(ValueError):
        LeadCreate(
            full_name="Alan Turing",
            email="alan@example.com",
            company_name="Computing Ltd",
            privacy_consent=False,
        )


def test_lead_schema_rejects_empty_source_and_long_website():
    base = {
        "full_name": "Alan Turing",
        "email": "alan@example.com",
        "company_name": "Computing Ltd",
        "privacy_consent": True,
    }
    with pytest.raises(ValueError):
        LeadCreate(**base, source="   ")
    with pytest.raises(ValueError):
        LeadCreate(**base, website=f"https://example.com/{'a' * 2048}")


@pytest.mark.asyncio
async def test_create_student_lead(lead_session: AsyncSession):
    lead = await LeadService().create(
        lead_session,
        StudentLeadCreate(
            full_name="  Margaret   Hamilton ",
            email="MARGARET@example.com",
            institution_name=" MIT ",
            course_name=" Software Engineering ",
            semester=" 4th semester ",
            linkedin_url="https://linkedin.com/in/margaret",
            github_url="https://github.com/margaret",
            area_of_interest=" Flight software ",
            message=" Interested in the program ",
            privacy_consent=True,
            source="university-fair",
        ),
    )

    assert lead.lead_type == LeadType.STUDENT
    assert lead.company_name is None
    assert lead.full_name == "Margaret Hamilton"
    assert lead.email == "margaret@example.com"
    assert lead.institution_name == "MIT"
    assert lead.course_name == "Software Engineering"
    assert lead.linkedin_url == "https://linkedin.com/in/margaret"
    assert lead.github_url == "https://github.com/margaret"
    assert lead.source == "university-fair"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("semester", "s" * 51),
        ("linkedin_url", "not-a-url"),
        ("linkedin_url", f"https://example.com/{'a' * 2048}"),
        ("github_url", "not-a-url"),
        ("area_of_interest", "a" * 256),
        ("message", "m" * 2001),
    ],
)
def test_student_lead_schema_validates_optional_fields(field: str, value: str):
    data = {
        "full_name": "Dorothy Vaughan",
        "email": "dorothy@example.com",
        "institution_name": "Wilberforce University",
        "course_name": "Mathematics",
        "privacy_consent": True,
        field: value,
    }

    with pytest.raises(ValueError):
        StudentLeadPublicCreate(**data)


@pytest.mark.parametrize("missing_field", ["institution_name", "course_name"])
def test_student_lead_schema_requires_student_fields(missing_field: str):
    data = {
        "full_name": "Dorothy Vaughan",
        "email": "dorothy@example.com",
        "institution_name": "Wilberforce University",
        "course_name": "Mathematics",
        "privacy_consent": True,
    }
    del data[missing_field]

    with pytest.raises(ValueError):
        StudentLeadPublicCreate(**data)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead",
    [
        Lead(
            lead_type=LeadType.COMPANY,
            full_name="Missing Company",
            email="company@example.com",
            privacy_consent=True,
        ),
        Lead(
            lead_type=LeadType.STUDENT,
            full_name="Missing Course",
            email="student@example.com",
            institution_name="Example University",
            privacy_consent=True,
        ),
    ],
)
async def test_database_enforces_type_required_fields(lead_session: AsyncSession, lead: Lead):
    lead_session.add(lead)
    with pytest.raises(IntegrityError):
        await lead_session.commit()
