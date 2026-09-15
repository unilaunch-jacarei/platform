import uuid

from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.leads.manager import lead_service
from backend.domains.leads.schemas import (
    LeadCreate,
    LeadPublicCreate,
    LeadRead,
    LeadStatusUpdate,
    LeadSubmissionRead,
    LeadViewCreate,
)
from backend.domains.usuarios.auth import current_superuser
from backend.domains.usuarios.models import User
from backend.infra.limiter import limiter

public_leads_router = APIRouter(prefix="/public/leads", tags=["public-leads"])
leads_router = APIRouter(prefix="/leads", tags=["leads"])


@public_leads_router.post(
    "/views",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
@limiter.limit("30/minute")
async def register_lead_page_view(
    request: Request,
    response: Response,
    o: str = Query(default="direct", max_length=255),
    idempotency_key: str = Header(..., alias="Idempotency-Key", max_length=255),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await lead_service.record_page_view(
        session,
        LeadViewCreate(event_key=idempotency_key, source=o),
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@public_leads_router.post(
    "",
    response_model=LeadSubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/hour")
async def create_public_lead(
    request: Request,
    data: LeadPublicCreate,
    o: str = Query(default="direct", max_length=255),
    session: AsyncSession = Depends(get_db),
) -> LeadSubmissionRead:
    data = LeadCreate.model_validate({**data.model_dump(), "source": o})
    lead = await lead_service.create(session, data)
    return LeadSubmissionRead.model_validate(lead)


@leads_router.get("", response_model=list[LeadRead])
async def list_leads(
    _user: User = Depends(current_superuser),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> list[LeadRead]:
    leads = await lead_service.list(session, limit=limit, offset=offset)
    return [LeadRead.model_validate(lead) for lead in leads]


@leads_router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> LeadRead:
    lead = await lead_service.get(session, lead_id)
    return LeadRead.model_validate(lead)


@leads_router.patch("/{lead_id}/status", response_model=LeadRead)
async def update_lead_status(
    lead_id: uuid.UUID,
    data: LeadStatusUpdate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> LeadRead:
    lead = await lead_service.update_status(session, lead_id, data)
    return LeadRead.model_validate(lead)


@leads_router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> Response:
    await lead_service.delete(session, lead_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
