import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import Settings, get_settings
from backend.database import Base, get_db
from backend.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def test_settings():
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        JWT_SECRET="test-jwt-secret-key-minimum-32-chars-long!",
    )


@pytest_asyncio.fixture
async def test_engine(test_settings):
    engine = create_async_engine(
        test_settings.async_database_url,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def client(test_settings, test_session_factory):
    app = create_app()

    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    payload = {
        "email": "duplicado@unilaunch.org",
        "password": "SenhaValida123",
        "nome": "Usuario Um",
    }
    # 1. First registration succeeds
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # 2. Second registration fails with 400
    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    data = res2.json()
    assert data["detail"] == "REGISTER_USER_ALREADY_EXISTS" or "error" in data


@pytest.mark.asyncio
async def test_register_invalid_data(client: AsyncClient):
    # Missing password
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "sem_senha@teste.com", "nome": "Sem Senha"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_full_auth_and_user_profile_lifecycle(client: AsyncClient):
    email = "lifecycle@unilaunch.org"
    password = "SenhaSegura12345"
    nome = "Estudante Lifecycle"

    # 1. Register
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "nome": nome},
    )
    assert reg_res.status_code == 201
    assert "id" in reg_res.json()

    # 2. Login
    login_res = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": email, "password": password},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get /usuarios/me
    me_res = await client.get("/api/v1/usuarios/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
    assert me_res.json()["nome"] == nome

    # 4. Patch /usuarios/me
    patch_res = await client.patch(
        "/api/v1/usuarios/me",
        headers=headers,
        json={"nome": "Nome Atualizado"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["nome"] == "Nome Atualizado"

    # 5. Access without token fails
    unauth_res = await client.get("/api/v1/usuarios/me")
    assert unauth_res.status_code == 401

    # 6. Forgot password flow trigger
    forgot_res = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": email},
    )
    assert forgot_res.status_code == 202

    # 7. Request verify token trigger
    verify_res = await client.post(
        "/api/v1/auth/request-verify-token",
        json={"email": email},
    )
    assert verify_res.status_code == 202

    # 8. Logout
    logout_res = await client.post("/api/v1/auth/jwt/logout", headers=headers)
    assert logout_res.status_code in (200, 204)
