import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
from backend.domains.leads.manager import LeadService
from backend.domains.leads.models import CompanySize, LeadStatus
from backend.domains.leads.schemas import LeadCreate, LeadStatusUpdate, LeadViewCreate
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
