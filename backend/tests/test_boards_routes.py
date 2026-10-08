import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import Settings, get_settings
from backend.database import Base, get_db
from backend.domains.boards.schemas import (
    BoardColumnCreate,
    BoardColumnUpdate,
    BoardCreate,
    BoardUpdate,
    TaskCreate,
    TaskUpdate,
)
from backend.domains.usuarios.models import User
from backend.infra.limiter import limiter
from backend.main import create_app


@pytest_asyncio.fixture
async def board_client():
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
        client.board_session_factory = factory
        yield client
    await engine.dispose()


async def get_superuser_token(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "SuperSecretPassword123!",
            "nome": "Super Admin",
        },
    )
    async with client.board_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == "admin@example.com"))
        user.is_superuser = True
        await session.commit()
    login = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "SuperSecretPassword123!"},
    )
    return login.json()["access_token"]


async def get_regular_user_token(client: AsyncClient) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "regular@example.com",
            "password": "RegularUserPassword123!",
            "nome": "Regular User",
        },
    )
    login = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "regular@example.com", "password": "RegularUserPassword123!"},
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_boards_unauthenticated_and_forbidden_access(board_client: AsyncClient):
    # Unauthenticated
    res = await board_client.get("/api/v1/boards")
    assert res.status_code == 401

    res = await board_client.post("/api/v1/boards", json={"title": "Test"})
    assert res.status_code == 401

    # Regular user (non-superuser) gets 403 Forbidden
    reg_token = await get_regular_user_token(board_client)
    headers = {"Authorization": f"Bearer {reg_token}"}
    res = await board_client.get("/api/v1/boards", headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_boards_crud_routes(board_client: AsyncClient):
    token = await get_superuser_token(board_client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Board
    create_res = await board_client.post(
        "/api/v1/boards",
        headers=headers,
        json={"title": "  Engineering   Board  ", "description": "  Core   tasks  "},
    )
    assert create_res.status_code == 201
    board_data = create_res.json()
    board_id = board_data["id"]
    assert board_data["title"] == "Engineering Board"
    assert board_data["description"] == "Core tasks"
    assert board_data["columns"] == []
    assert "owner_id" in board_data

    # Extra forbidden field validation
    extra_field_res = await board_client.post(
        "/api/v1/boards",
        headers=headers,
        json={"title": "Test", "extra": "not_allowed"},
    )
    assert extra_field_res.status_code == 422

    # 2. List Boards
    list_res = await board_client.get("/api/v1/boards", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["id"] == board_id

    # 3. Get Board
    get_res = await board_client.get(f"/api/v1/boards/{board_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == board_id

    get_missing = await board_client.get(f"/api/v1/boards/{uuid.uuid4()}", headers=headers)
    assert get_missing.status_code == 404

    # 4. Update Board
    update_res = await board_client.patch(
        f"/api/v1/boards/{board_id}",
        headers=headers,
        json={"title": "  Updated   Engineering  "},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Engineering"

    update_missing = await board_client.patch(
        f"/api/v1/boards/{uuid.uuid4()}",
        headers=headers,
        json={"title": "Not Found"},
    )
    assert update_missing.status_code == 404

    # 5. Delete Board
    del_res = await board_client.delete(f"/api/v1/boards/{board_id}", headers=headers)
    assert del_res.status_code == 204

    del_missing = await board_client.delete(f"/api/v1/boards/{uuid.uuid4()}", headers=headers)
    assert del_missing.status_code == 404


@pytest.mark.asyncio
async def test_columns_and_tasks_crud_routes(board_client: AsyncClient):
    token = await get_superuser_token(board_client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create parent board
    b_res = await board_client.post(
        "/api/v1/boards",
        headers=headers,
        json={"title": "Product Roadmap"},
    )
    board_id = b_res.json()["id"]

    # 1. Create Column
    col_res = await board_client.post(
        "/api/v1/boards/columns",
        headers=headers,
        json={"board_id": board_id, "name": "  In   Progress  ", "position": 1},
    )
    assert col_res.status_code == 201
    col_data = col_res.json()
    column_id = col_data["id"]
    assert col_data["name"] == "In Progress"
    assert col_data["position"] == 1
    assert col_data["tasks"] == []

    # Create Column for non-existent board -> 404
    col_missing_board = await board_client.post(
        "/api/v1/boards/columns",
        headers=headers,
        json={"board_id": str(uuid.uuid4()), "name": "Orphan Col"},
    )
    assert col_missing_board.status_code == 404

    # 2. Update Column
    update_col_res = await board_client.patch(
        f"/api/v1/boards/columns/{column_id}",
        headers=headers,
        json={"name": "Doing", "position": 2},
    )
    assert update_col_res.status_code == 200
    assert update_col_res.json()["name"] == "Doing"
    assert update_col_res.json()["position"] == 2

    # Update non-existent column -> 404
    update_missing_col = await board_client.patch(
        f"/api/v1/boards/columns/{uuid.uuid4()}",
        headers=headers,
        json={"name": "Ghost"},
    )
    assert update_missing_col.status_code == 404

    # Create second column for moving tasks
    col2_res = await board_client.post(
        "/api/v1/boards/columns",
        headers=headers,
        json={"board_id": board_id, "name": "Done", "position": 3},
    )
    col2_id = col2_res.json()["id"]

    # 3. Create Task
    task_res = await board_client.post(
        "/api/v1/boards/tasks",
        headers=headers,
        json={
            "column_id": column_id,
            "title": "  Setup   CI/CD  ",
            "description": "Configure GitHub Actions",
            "priority": "high",
            "position": 0,
        },
    )
    assert task_res.status_code == 201
    task_data = task_res.json()
    task_id = task_data["id"]
    assert task_data["title"] == "Setup CI/CD"
    assert task_data["description"] == "Configure GitHub Actions"
    assert task_data["priority"] == "high"

    # Create task with invalid priority -> 422
    task_invalid_priority = await board_client.post(
        "/api/v1/boards/tasks",
        headers=headers,
        json={"column_id": column_id, "title": "Test", "priority": "super_urgent"},
    )
    assert task_invalid_priority.status_code == 422

    # Create task for non-existent column -> 404
    task_missing_col = await board_client.post(
        "/api/v1/boards/tasks",
        headers=headers,
        json={"column_id": str(uuid.uuid4()), "title": "Orphan"},
    )
    assert task_missing_col.status_code == 404

    # 4. Update Task (move to col2 and update title)
    update_task_res = await board_client.patch(
        f"/api/v1/boards/tasks/{task_id}",
        headers=headers,
        json={"column_id": col2_id, "title": "Setup CI/CD (Finished)", "priority": "urgent"},
    )
    assert update_task_res.status_code == 200
    assert update_task_res.json()["column_id"] == col2_id
    assert update_task_res.json()["title"] == "Setup CI/CD (Finished)"
    assert update_task_res.json()["priority"] == "urgent"

    # Update task with non-existent target column -> 404
    update_task_bad_col = await board_client.patch(
        f"/api/v1/boards/tasks/{task_id}",
        headers=headers,
        json={"column_id": str(uuid.uuid4())},
    )
    assert update_task_bad_col.status_code == 404

    # Update non-existent task -> 404
    update_missing_task = await board_client.patch(
        f"/api/v1/boards/tasks/{uuid.uuid4()}",
        headers=headers,
        json={"title": "Ghost"},
    )
    assert update_missing_task.status_code == 404

    # Verify board eager loading shows columns and tasks
    board_full = await board_client.get(f"/api/v1/boards/{board_id}", headers=headers)
    assert board_full.status_code == 200
    assert len(board_full.json()["columns"]) == 2

    # 5. Delete Task
    del_task_res = await board_client.delete(f"/api/v1/boards/tasks/{task_id}", headers=headers)
    assert del_task_res.status_code == 204

    del_missing_task = await board_client.delete(
        f"/api/v1/boards/tasks/{uuid.uuid4()}", headers=headers
    )
    assert del_missing_task.status_code == 404

    # 6. Delete Column
    del_col_res = await board_client.delete(f"/api/v1/boards/columns/{column_id}", headers=headers)
    assert del_col_res.status_code == 204

    del_missing_col = await board_client.delete(
        f"/api/v1/boards/columns/{uuid.uuid4()}", headers=headers
    )
    assert del_missing_col.status_code == 404


def test_boards_schemas_validators():
    # BoardCreate / BoardUpdate text validators with non-string / None
    assert BoardCreate.normalize_text(None) is None
    assert BoardCreate.normalize_text(123) == 123
    assert BoardCreate.normalize_text("   hello   world   ") == "hello world"

    assert BoardUpdate.normalize_text(None) is None
    assert BoardUpdate.normalize_text(456) == 456
    assert BoardUpdate.normalize_text("  trimmed   text  ") == "trimmed text"

    # BoardColumnCreate / BoardColumnUpdate name validators
    assert BoardColumnCreate.normalize_name(123) == 123
    assert BoardColumnCreate.normalize_name("  Col   Name  ") == "Col Name"

    assert BoardColumnUpdate.normalize_name(None) is None
    assert BoardColumnUpdate.normalize_name(456) == 456
    assert BoardColumnUpdate.normalize_name("  Updated   Col  ") == "Updated Col"

    # TaskCreate / TaskUpdate validators
    assert TaskCreate.normalize_text(None) is None
    assert TaskCreate.normalize_text(123) == 123
    assert TaskCreate.normalize_text("  Task   Title  ") == "Task Title"

    assert TaskUpdate.normalize_text(None) is None
    assert TaskUpdate.normalize_text(456) == 456
    assert TaskUpdate.normalize_text("  Updated   Title  ") == "Updated Title"
