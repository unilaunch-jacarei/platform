import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
from backend.domains.boards.manager import BoardManager
from backend.domains.boards.models import TaskPriority
from backend.domains.boards.schemas import (
    BoardColumnCreate,
    BoardColumnUpdate,
    BoardCreate,
    BoardUpdate,
    TaskCreate,
    TaskUpdate,
)
from backend.domains.usuarios.models import User
from backend.error import NotFoundError


@pytest_asyncio.fixture
async def board_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def board_user(board_session: AsyncSession) -> User:
    user = User(
        email="test_board_user@example.com",
        hashed_password="hashed_dummy_password",
        nome="Board User",
        is_active=True,
        is_superuser=True,
    )
    board_session.add(user)
    await board_session.commit()
    await board_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_and_get_board(board_session: AsyncSession, board_user: User):
    manager = BoardManager()
    data = BoardCreate(title="Sprint 1 Board", description="Board for sprint 1 tasks")

    board = await manager.create(board_session, data, owner_id=board_user.id)
    assert board.id is not None
    assert board.title == "Sprint 1 Board"
    assert board.description == "Board for sprint 1 tasks"
    assert board.owner_id == board_user.id
    assert board.columns == []

    fetched = await manager.get(board_session, board.id)
    assert fetched.id == board.id
    assert fetched.title == "Sprint 1 Board"
    assert fetched.owner_id == board_user.id


@pytest.mark.asyncio
async def test_get_board_not_found(board_session: AsyncSession):
    manager = BoardManager()
    with pytest.raises(NotFoundError, match="Board não encontrado"):
        await manager.get(board_session, uuid.uuid4())


@pytest.mark.asyncio
async def test_list_boards_ordering(board_session: AsyncSession, board_user: User):
    manager = BoardManager()

    # Empty list
    empty_list = await manager.list(board_session)
    assert empty_list == []

    # Create 2 boards with distinct created_at
    board1 = await manager.create(
        board_session, BoardCreate(title="First Board"), owner_id=board_user.id
    )
    board1.created_at = datetime.now(UTC) - timedelta(days=1)
    await board_session.commit()

    board2 = await manager.create(
        board_session, BoardCreate(title="Second Board"), owner_id=board_user.id
    )

    boards = await manager.list(board_session)
    assert len(boards) == 2
    # Ordered by created_at desc
    assert [b.id for b in boards] == [board2.id, board1.id]


@pytest.mark.asyncio
async def test_update_board(board_session: AsyncSession, board_user: User):
    manager = BoardManager()
    board = await manager.create(
        board_session,
        BoardCreate(title="Original Title", description="Original Desc"),
        owner_id=board_user.id,
    )

    updated = await manager.update(
        board_session,
        board.id,
        BoardUpdate(title="Updated Title", description="Updated Desc"),
    )
    assert updated.title == "Updated Title"
    assert updated.description == "Updated Desc"

    with pytest.raises(NotFoundError, match="Board não encontrado"):
        await manager.update(board_session, uuid.uuid4(), BoardUpdate(title="New"))


@pytest.mark.asyncio
async def test_delete_board(board_session: AsyncSession, board_user: User):
    manager = BoardManager()
    board = await manager.create(
        board_session, BoardCreate(title="To Delete"), owner_id=board_user.id
    )

    await manager.delete(board_session, board.id)

    with pytest.raises(NotFoundError, match="Board não encontrado"):
        await manager.get(board_session, board.id)

    with pytest.raises(NotFoundError, match="Board não encontrado"):
        await manager.delete(board_session, uuid.uuid4())


@pytest.mark.asyncio
async def test_column_crud_lifecycle(board_session: AsyncSession, board_user: User):
    manager = BoardManager()
    board = await manager.create(
        board_session, BoardCreate(title="Kanban Board"), owner_id=board_user.id
    )

    # 1. Create Column
    col_data = BoardColumnCreate(board_id=board.id, name="To Do", position=0)
    col = await manager.create_column(board_session, col_data)
    assert col.id is not None
    assert col.name == "To Do"
    assert col.board_id == board.id
    assert col.position == 0
    assert col.tasks == []

    # Create Column for non-existent board raises NotFoundError
    with pytest.raises(NotFoundError, match="Board não encontrado"):
        await manager.create_column(
            board_session, BoardColumnCreate(board_id=uuid.uuid4(), name="Invalid")
        )

    # 2. Update Column
    updated_col = await manager.update_column(
        board_session, col.id, BoardColumnUpdate(name="In Progress", position=1)
    )
    assert updated_col.name == "In Progress"
    assert updated_col.position == 1

    # Update non-existent column
    with pytest.raises(NotFoundError, match="Coluna não encontrada"):
        await manager.update_column(
            board_session, uuid.uuid4(), BoardColumnUpdate(name="Nonexistent")
        )

    # 3. Delete Column
    await manager.delete_column(board_session, col.id)

    # Delete non-existent column
    with pytest.raises(NotFoundError, match="Coluna não encontrada"):
        await manager.delete_column(board_session, col.id)


@pytest.mark.asyncio
async def test_task_crud_lifecycle(board_session: AsyncSession, board_user: User):
    manager = BoardManager()
    board = await manager.create(
        board_session, BoardCreate(title="Task Board"), owner_id=board_user.id
    )
    col1 = await manager.create_column(
        board_session, BoardColumnCreate(board_id=board.id, name="Backlog", position=0)
    )
    col2 = await manager.create_column(
        board_session, BoardColumnCreate(board_id=board.id, name="Done", position=1)
    )

    # 1. Create Task
    due = datetime.now(UTC) + timedelta(days=7)
    task_data = TaskCreate(
        column_id=col1.id,
        title="Implement Auth",
        description="Add JWT auth support",
        priority=TaskPriority.HIGH,
        due_date=due,
        position=0,
    )
    task = await manager.create_task(board_session, task_data)
    assert task.id is not None
    assert task.column_id == col1.id
    assert task.title == "Implement Auth"
    assert task.description == "Add JWT auth support"
    assert task.priority == TaskPriority.HIGH
    assert task.position == 0

    # Create Task in non-existent column raises NotFoundError
    with pytest.raises(NotFoundError, match="Coluna de destino não encontrada"):
        await manager.create_task(
            board_session, TaskCreate(column_id=uuid.uuid4(), title="Orphan Task")
        )

    # 2. Update Task (content and moving to another column)
    updated_task = await manager.update_task(
        board_session,
        task.id,
        TaskUpdate(
            column_id=col2.id,
            title="Implement Auth (Complete)",
            priority=TaskPriority.URGENT,
            position=2,
        ),
    )
    assert updated_task.column_id == col2.id
    assert updated_task.title == "Implement Auth (Complete)"
    assert updated_task.priority == TaskPriority.URGENT
    assert updated_task.position == 2

    # Update task with non-existent destination column raises NotFoundError
    with pytest.raises(NotFoundError, match="Coluna de destino não encontrada"):
        await manager.update_task(board_session, task.id, TaskUpdate(column_id=uuid.uuid4()))

    # Update non-existent task raises NotFoundError
    with pytest.raises(NotFoundError, match="Tarefa não encontrada"):
        await manager.update_task(board_session, uuid.uuid4(), TaskUpdate(title="Non-existent"))

    # 3. Delete Task
    await manager.delete_task(board_session, task.id)

    # Delete non-existent task raises NotFoundError
    with pytest.raises(NotFoundError, match="Tarefa não encontrada"):
        await manager.delete_task(board_session, task.id)
