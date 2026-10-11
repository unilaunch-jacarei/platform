import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.boards.dependencies import require_board_role
from backend.domains.boards.manager import board_manager
from backend.domains.boards.models import BoardRole
from backend.domains.boards.schemas import (
    BoardColumnCreate,
    BoardColumnRead,
    BoardColumnUpdate,
    BoardCreate,
    BoardMemberCreate,
    BoardMemberRead,
    BoardMemberUpdate,
    BoardRead,
    BoardUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from backend.domains.usuarios.auth import current_active_user, current_superuser
from backend.domains.usuarios.models import User

boards_router = APIRouter(prefix="/boards", tags=["boards"])


# --- Operações de Boards ---


@boards_router.get("", response_model=list[BoardRead])
async def list_boards(
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[BoardRead]:
    """Lista todos os quadros cadastrados com seus membros."""
    boards = await board_manager.list(session)
    return [BoardRead.model_validate(board) for board in boards]


@boards_router.get("/{board_id}", response_model=BoardRead)
async def get_board(
    board_id: uuid.UUID,
    _role: Annotated[
        BoardRole,
        Depends(
            require_board_role(
                [BoardRole.VIEWER, BoardRole.MEMBER, BoardRole.ADMIN, BoardRole.OWNER]
            )
        ),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
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
    current_user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardRead:
    """Cria um novo quadro e vincula o usuário criador como OWNER."""
    board = await board_manager.create(session, data, owner_id=current_user.id)
    return BoardRead.model_validate(board)


@boards_router.patch("/{board_id}", response_model=BoardRead)
async def update_board(
    board_id: uuid.UUID,
    data: BoardUpdate,
    _role: Annotated[
        BoardRole,
        Depends(require_board_role([BoardRole.ADMIN, BoardRole.OWNER])),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardRead:
    """Atualiza dados de um quadro."""
    board = await board_manager.update(session, board_id, data)
    return BoardRead.model_validate(board)


@boards_router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: uuid.UUID,
    _role: Annotated[
        BoardRole,
        Depends(require_board_role([BoardRole.OWNER])),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Deleta um quadro."""
    await board_manager.delete(session, board_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Operações de Membros ---


@boards_router.get("/{board_id}/members", response_model=list[BoardMemberRead])
async def list_board_members(
    board_id: uuid.UUID,
    _role: Annotated[
        BoardRole,
        Depends(
            require_board_role(
                [BoardRole.VIEWER, BoardRole.MEMBER, BoardRole.ADMIN, BoardRole.OWNER]
            )
        ),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[BoardMemberRead]:
    """Lista todos os membros de um quadro especifico."""
    members = await board_manager.list_members(session, board_id)
    return [BoardMemberRead.model_validate(member) for member in members]


@boards_router.post(
    "/{board_id}/members",
    response_model=BoardMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_board_member(
    board_id: uuid.UUID,
    data: BoardMemberCreate,
    _role: Annotated[
        BoardRole,
        Depends(require_board_role([BoardRole.ADMIN, BoardRole.OWNER])),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardMemberRead:
    """Adiciona um novo membro ao quadro."""
    member = await board_manager.add_member(session, board_id, data)
    return BoardMemberRead.model_validate(member)


@boards_router.patch("/{board_id}/members/{user_id}", response_model=BoardMemberRead)
async def update_board_member_role(
    board_id: uuid.UUID,
    user_id: uuid.UUID,
    data: BoardMemberUpdate,
    _role: Annotated[
        BoardRole,
        Depends(require_board_role([BoardRole.ADMIN, BoardRole.OWNER])),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardMemberRead:
    """Atualiza o papel/função de um membro no quadro."""
    member = await board_manager.update_member_role(session, board_id, user_id, data)
    return BoardMemberRead.model_validate(member)


@boards_router.delete("/{board_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_board_member(
    board_id: uuid.UUID,
    user_id: uuid.UUID,
    _role: Annotated[
        BoardRole,
        Depends(require_board_role([BoardRole.ADMIN, BoardRole.OWNER])),
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Remove um membro do quadro."""
    await board_manager.remove_member(session, board_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Operações de Colunas ---


@boards_router.post(
    "/columns",
    response_model=BoardColumnRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_column(
    data: BoardColumnCreate,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardColumnRead:
    """Adiciona uma nova coluna a um quadro."""
    column = await board_manager.create_column(session, data)
    return BoardColumnRead.model_validate(column)


@boards_router.patch("/columns/{column_id}", response_model=BoardColumnRead)
async def update_column(
    column_id: uuid.UUID,
    data: BoardColumnUpdate,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BoardColumnRead:
    """Atualiza dados de uma coluna."""
    column = await board_manager.update_column(session, column_id, data)
    return BoardColumnRead.model_validate(column)


@boards_router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: uuid.UUID,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Remove uma coluna."""
    await board_manager.delete_column(session, column_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Operações de Tarefas ---


@boards_router.post(
    "/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    data: TaskCreate,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    """Cria uma nova tarefa dentro de uma coluna."""
    task = await board_manager.create_task(session, data)
    return TaskRead.model_validate(task)


@boards_router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRead:
    """Atualiza dados de uma tarefa (ex: mover de coluna, reordenar)."""
    task = await board_manager.update_task(session, task_id, data)
    return TaskRead.model_validate(task)


@boards_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    _user: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Remove uma tarefa do quadro."""
    await board_manager.delete_task(session, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
