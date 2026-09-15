import hashlib
import hmac
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import Settings, get_settings
from backend.database import Base, get_db
from backend.domains.leads.models import Lead, LeadType
from backend.domains.usuarios.models import User
from backend.infra.limiter import limiter
from backend.main import create_app


@pytest_asyncio.fixture
async def lead_client():
    limiter.reset()
    settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        JWT_SECRET="test-jwt-secret-key-minimum-32-chars-long!",
    )
    engine = create_async_engine(settings.async_database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    app = create_app()

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.lead_session_factory = factory
        yield client
    await engine.dispose()


def lead_payload() -> dict:
    return {
        "full_name": "Grace Hopper",
        "email": "grace@example.com",
        "company_name": "Compilers Inc.",
        "company_size": "51-200",
        "privacy_consent": True,
    }


@pytest.mark.asyncio
async def test_public_lead_submission_and_page_view(lead_client: AsyncClient):
    trace = await lead_client.get("/health", headers={"X-Request-ID": "trace-test-1"})
    assert trace.headers["X-Request-ID"] == "trace-test-1"

    metrics = await lead_client.get("/metrics")
    assert metrics.status_code == 200
    assert b"http_requests_total" in metrics.content

    view_headers = {"Idempotency-Key": "view-request-1"}
    first_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    duplicate_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    assert first_view.status_code == 204
    assert duplicate_view.status_code == 204

    response = await lead_client.post("/api/v1/public/leads?o=linkedin", json=lead_payload())
    assert response.status_code == 201
    assert set(response.json()) == {"id", "created_at"}

    unauthorized = await lead_client.get("/api/v1/leads")
    assert unauthorized.status_code == 401


@pytest.mark.asyncio
async def test_public_lead_submission_is_rate_limited(lead_client: AsyncClient):
    responses = []
    for index in range(6):
        payload = lead_payload()
        payload["email"] = f"rate-{index}@example.com"
        responses.append(await lead_client.post("/api/v1/public/leads", json=payload))

    assert [response.status_code for response in responses[:5]] == [201] * 5
    assert responses[5].status_code == 429

    forged_visitor = await lead_client.post(
        "/api/v1/public/leads",
        headers={"X-Client-IP": "203.0.113.10", "X-Client-IP-Signature": "invalid"},
        json={**lead_payload(), "email": "forged-visitor@example.com"},
    )
    assert forged_visitor.status_code == 429

    client_ip = "203.0.113.10"
    secret = "change-me-in-production"
    signature = hmac.new(secret.encode(), client_ip.encode(), hashlib.sha256).hexdigest()
    other_visitor = await lead_client.post(
        "/api/v1/public/leads",
        headers={"X-Client-IP": client_ip, "X-Client-IP-Signature": signature},
        json={**lead_payload(), "email": "other-visitor@example.com"},
    )
    assert other_visitor.status_code == 201


@pytest.mark.asyncio
async def test_public_routes_validate_request_data(lead_client: AsyncClient):
    missing_key = await lead_client.post("/api/v1/public/leads/views")
    assert missing_key.status_code == 422

    invalid_lead = await lead_client.post(
        "/api/v1/public/leads?o=instagram",
        json={"full_name": "A", "email": "invalid", "company_name": "", "privacy_consent": False},
    )
    assert invalid_lead.status_code == 422

    extra_field = await lead_client.post(
        "/api/v1/public/leads",
        json={
            "full_name": "Valid Name",
            "email": "valid@example.com",
            "company_name": "Valid Company",
            "privacy_consent": True,
            "owner_id": str(uuid.uuid4()),
        },
    )
    assert extra_field.status_code == 422

    invalid_id = await lead_client.get("/api/v1/leads/not-an-uuid")
    assert invalid_id.status_code == 401


@pytest.mark.asyncio
async def test_public_lead_accepts_only_required_fields(lead_client: AsyncClient):
    response = await lead_client.post(
        "/api/v1/public/leads?o=direct",
        json={
            "full_name": "Katherine Johnson",
            "email": "katherine@example.com",
            "company_name": "Orbital Systems",
            "privacy_consent": True,
        },
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_public_student_lead_submission(lead_client: AsyncClient):
    response = await lead_client.post(
        "/api/v1/public/leads/students?o=campus",
        json={
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "semester": "6th semester",
            "linkedin_url": "https://linkedin.com/in/mary-jackson",
            "github_url": "https://github.com/mary-jackson",
            "area_of_interest": "Aerospace",
            "message": "I want to learn more",
            "privacy_consent": True,
        },
    )

    assert response.status_code == 201
    async with lead_client.lead_session_factory() as session:
        lead = await session.get(Lead, uuid.UUID(response.json()["id"]))
    assert lead.lead_type == LeadType.STUDENT
    assert lead.company_name is None
    assert lead.institution_name == "Hampton Institute"
    assert lead.course_name == "Engineering"
    assert lead.source == "campus"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "course_name": "Engineering",
            "privacy_consent": True,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "privacy_consent": False,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "linkedin_url": "not-a-url",
            "privacy_consent": True,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "company_name": "Unexpected Company",
            "privacy_consent": True,
        },
    ],
)
async def test_public_student_lead_validates_request(lead_client: AsyncClient, payload: dict):
    response = await lead_client.post("/api/v1/public/leads/students", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_authenticated_lead_management(lead_client: AsyncClient):
    await lead_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "SenhaSegura12345",
            "nome": "Admin",
        },
    )
    async with lead_client.lead_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == "admin@example.com"))
        user.is_superuser = True
        await session.commit()
    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await lead_client.post("/api/v1/public/leads?o=eventox", json=lead_payload())
    lead_id = created.json()["id"]

    listed = await lead_client.get("/api/v1/leads", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["source"] == "eventox"
    assert listed.json()[0]["lead_type"] == "company"

    student = await lead_client.post(
        "/api/v1/public/leads/students?o=campus",
        json={
            "full_name": "Annie Easley",
            "email": "annie@example.com",
            "institution_name": "Cleveland State University",
            "course_name": "Mathematics",
            "privacy_consent": True,
        },
    )
    student_admin = await lead_client.get(f"/api/v1/leads/{student.json()['id']}", headers=headers)
    assert student_admin.status_code == 200
    assert student_admin.json()["lead_type"] == "student"
    assert student_admin.json()["company_name"] is None
    assert student_admin.json()["institution_name"] == "Cleveland State University"

    updated = await lead_client.patch(
        f"/api/v1/leads/{lead_id}/status",
        headers=headers,
        json={"status": "contacted"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "contacted"

    fetched = await lead_client.get(f"/api/v1/leads/{lead_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == lead_id

    missing = await lead_client.get(f"/api/v1/leads/{uuid.uuid4()}", headers=headers)
    assert missing.status_code == 404

    deleted = await lead_client.delete(f"/api/v1/leads/{lead_id}", headers=headers)
    assert deleted.status_code == 204
    deleted_lead = await lead_client.get(f"/api/v1/leads/{lead_id}", headers=headers)
    assert deleted_lead.status_code == 404


@pytest.mark.asyncio
async def test_regular_user_cannot_manage_leads(lead_client: AsyncClient):
    await lead_client.post(
        "/api/v1/auth/register",
        json={
            "email": "regular@example.com",
            "password": "SenhaSegura12345",
            "nome": "Regular",
        },
    )
    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "regular@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await lead_client.get("/api/v1/leads", headers=headers)
    assert response.status_code == 403
