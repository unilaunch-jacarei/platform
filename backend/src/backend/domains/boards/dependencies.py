# ruff: noqa: I001

import uuid
from typing import Annotated, Callable, Coroutine, Sequence

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.boards.models import Board, BoardMember, BoardRole
from backend.domains.boards.models import BoardColumn, Task
from backend.domains.usuarios.auth import current_active_user
from backend.domains.usuarios.models import User

ROLE_HIERARCHY: dict[BoardRole, int] = {
    BoardRole.VIEWER: 1,
    BoardRole.MEMBER: 2,
    BoardRole.ADMIN: 3,
    BoardRole.OWNER: 4,
}


async def get_user_board_role(
    session: AsyncSession,
    board_id: uuid.UUID,
    user: User,
) -> BoardRole | None:
    """Busca o papel (role) do usuário no quadro.

    Superusuários e o dono direto do board assumem 'owner' automaticamente.
    """
    if user.is_superuser:
        return BoardRole.OWNER

    # 1. Verifica se o usuário é o criador/dono direto do Board
    stmt_board = select(Board.owner_id).where(Board.id == board_id)
    board_owner_id = (await session.execute(stmt_board)).scalar_one_or_none()

    if board_owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board não encontrado",
        )

    if board_owner_id == user.id:
        return BoardRole.OWNER

    # 2. Busca o vínculo na tabela de membros
    stmt_member = select(BoardMember.role).where(
        BoardMember.board_id == board_id,
        BoardMember.user_id == user.id,
    )
    role_str = (await session.execute(stmt_member)).scalar_one_or_none()

    if role_str is None:
        return None

    return BoardRole(role_str)


async def require_user_board_role(
    session: AsyncSession,
    board_id: uuid.UUID,
    current_user: User,
    allowed_roles: Sequence[BoardRole],
) -> BoardRole:
    """Valida a permissão do usuário para uma operação em um quadro."""
    user_role = await get_user_board_role(session, board_id, current_user)

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não é membro deste quadro",
        )

    user_level = ROLE_HIERARCHY[user_role]
    min_required_level = min(ROLE_HIERARCHY[role] for role in allowed_roles)
    if user_level < min_required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão suficiente para esta operação",
        )

    return user_role


async def get_column_board_id(session: AsyncSession, column_id: uuid.UUID) -> uuid.UUID:
    """Obtém o quadro de uma coluna, preservando o erro de recurso inexistente."""
    board_id = await session.scalar(select(BoardColumn.board_id).where(BoardColumn.id == column_id))
    if board_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coluna não encontrada",
        )
    return board_id


async def get_task_board_id(session: AsyncSession, task_id: uuid.UUID) -> uuid.UUID:
    """Obtém o quadro de uma tarefa a partir da sua coluna."""
    board_id = await session.scalar(
        select(BoardColumn.board_id)
        .join(Task, Task.column_id == BoardColumn.id)
        .where(Task.id == task_id)
    )
    if board_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return board_id


def require_board_role(
    allowed_roles: Sequence[BoardRole],
) -> Callable[..., Coroutine[None, None, BoardRole]]:
    """Dependency Factory que valida se o usuário autenticado possui ao menos um

    dos papéis/roles permitidos no Board identificado na URL ({board_id}).
    """

    async def dependency(
        board_id: Annotated[uuid.UUID, Path()],
        current_user: Annotated[User, Depends(current_active_user)],
        session: Annotated[AsyncSession, Depends(get_db)],
    ) -> BoardRole:
        user_role = await get_user_board_role(session, board_id, current_user)

        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não é membro deste quadro",
            )

        # Checa se a role do usuário satisfaz alguma das permissões necessárias
        user_level = ROLE_HIERARCHY[user_role]
        min_required_level = min(ROLE_HIERARCHY[role] for role in allowed_roles)

        if user_level < min_required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão suficiente para esta operação",
            )

        return user_role

    return dependency
