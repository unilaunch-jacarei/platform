import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.boards.manager import board_manager
from backend.domains.boards.schemas import (
    BoardColumnCreate,
    BoardColumnRead,
    BoardColumnUpdate,
    BoardCreate,
    BoardRead,
    BoardUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from backend.domains.usuarios.auth import current_superuser
from backend.domains.usuarios.models import User

boards_router = APIRouter(prefix="/boards", tags=["boards"])


@boards_router.get("", response_model=list[BoardRead])
async def list_boards(
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[BoardRead]:
    """Lista todos os quadros cadastrados com suas colunas e cards."""
    boards = await board_manager.list(session)
    return [BoardRead.model_validate(board) for board in boards]


@boards_router.get("/{board_id}", response_model=BoardRead)
async def get_board(
    board_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> BoardRead:
    """Obtém os detalhes de um quadro específico pelo ID."""
    board = await board_manager.get(session, board_id)
    return BoardRead.model_validate(board)


@boards_router.post(
    "",
    response_model=BoardRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_board(
    data: BoardCreate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> BoardRead:
    """Cria um novo quadro."""
    board = await board_manager.create(session, data)
    return BoardRead.model_validate(board)


@boards_router.patch("/{board_id}", response_model=BoardRead)
async def update_board(
    board_id: uuid.UUID,
    data: BoardUpdate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> BoardRead:
    """Atualiza dados de um quadro."""
    board = await board_manager.update(session, board_id, data)
    return BoardRead.model_validate(board)


@boards_router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Deleta um quadro."""
    await board_manager.delete(session, board_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@boards_router.post(
    "/columns",
    response_model=BoardColumnRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_column(
    data: BoardColumnCreate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> BoardColumnRead:
    """Adiciona uma nova coluna a um quadro."""
    column = await board_manager.create_column(session, data)
    return BoardColumnRead.model_validate(column)


@boards_router.patch("/columns/{column_id}", response_model=BoardColumnRead)
async def update_column(
    column_id: uuid.UUID,
    data: BoardColumnUpdate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> BoardColumnRead:
    """Atualiza dados de uma coluna."""
    column = await board_manager.update_column(session, column_id, data)
    return BoardColumnRead.model_validate(column)


@boards_router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Remove uma coluna."""
    await board_manager.delete_column(session, column_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@boards_router.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    data: TaskCreate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Cria uma nova tarefa dentro de uma coluna."""
    task = await board_manager.create_task(session, data)
    return TaskRead.model_validate(task)


@boards_router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> TaskRead:
    """Atualiza dados de uma tarefa (ex: mover de coluna, reordenar)."""
    task = await board_manager.update_task(session, task_id, data)
    return TaskRead.model_validate(task)


@boards_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    _user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """Remove uma tarefa do quadro."""
    await board_manager.delete_task(session, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
