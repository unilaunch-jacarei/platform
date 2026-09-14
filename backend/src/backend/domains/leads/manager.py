import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domains.leads.models import Lead, LeadPageView
from backend.domains.leads.schemas import LeadCreate, LeadStatusUpdate, LeadViewCreate
from backend.error import NotFoundError


class LeadService:
    """Application operations for public lead capture and administration."""

    async def create(self, session: AsyncSession, data: LeadCreate) -> Lead:
        values = data.model_dump()
        if values["website"] is not None:
            values["website"] = str(values["website"])
        if values["company_size"] is not None:
            values["company_size"] = str(values["company_size"])

        lead = Lead(**values)
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
        return lead

    async def record_page_view(
        self, session: AsyncSession, data: LeadViewCreate
    ) -> tuple[LeadPageView, bool]:
        existing = await self._find_page_view(session, data.event_key)
        if existing is not None:
            return existing, False

        page_view = LeadPageView(**data.model_dump())
        created = True
        try:
            async with session.begin_nested():
                session.add(page_view)
                await session.flush()
        except IntegrityError:
            created = False

        if not created:
            page_view = await self._find_page_view(session, data.event_key)
            if page_view is None:
                raise RuntimeError("Page view conflict could not be resolved")

        await session.commit()
        return page_view, created

    async def list(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> list[Lead]:
        result = await session.scalars(
            select(Lead).order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result)

    async def get(self, session: AsyncSession, lead_id: uuid.UUID) -> Lead:
        lead = await session.get(Lead, lead_id)
        if lead is None:
            raise NotFoundError("Lead não encontrado")
        return lead

    async def update_status(
        self, session: AsyncSession, lead_id: uuid.UUID, data: LeadStatusUpdate
    ) -> Lead:
        lead = await self.get(session, lead_id)
        lead.status = data.status
        await session.commit()
        await session.refresh(lead)
        return lead

    async def _find_page_view(self, session: AsyncSession, event_key: str) -> LeadPageView | None:
        return await session.scalar(
            select(LeadPageView).where(LeadPageView.event_key == event_key)
        )


lead_service = LeadService()
