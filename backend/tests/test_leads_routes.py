import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import Settings, get_settings
from backend.database import Base, get_db
from backend.main import create_app


@pytest_asyncio.fixture
async def lead_client():
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
    view_headers = {"Idempotency-Key": "view-request-1"}
    first_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    duplicate_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    assert first_view.status_code == 204
    assert duplicate_view.status_code == 204

    response = await lead_client.post(
        "/api/v1/public/leads?o=linkedin", json=lead_payload()
    )
    assert response.status_code == 201
    assert set(response.json()) == {"id", "created_at"}

    unauthorized = await lead_client.get("/api/v1/leads")
    assert unauthorized.status_code == 401


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
    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await lead_client.post(
        "/api/v1/public/leads?o=eventox", json=lead_payload()
    )
    lead_id = created.json()["id"]

    listed = await lead_client.get("/api/v1/leads", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["source"] == "eventox"

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
