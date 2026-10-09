# src/backend/domains/boards/manager.py
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.domains.boards.models import Board, BoardColumn, Task
from backend.domains.boards.schemas import (
    BoardColumnCreate,
    BoardColumnUpdate,
    BoardCreate,
    BoardUpdate,
    TaskCreate,
    TaskUpdate,
)
from backend.error import NotFoundError

DEFAULT_BOARD_COLUMNS = [
    ("A Fazer", 0),
    ("Em andamento", 1),
    ("Em review", 2),
    ("Concluído", 3),
]


class BoardManager:
    """Gerenciador de regras de negócio e operações de persistência para Boards, Colunas e Tarefas."""

    async def list(self, session: AsyncSession) -> list[Board]:
        """Lista todos os quadros ordenados pela data de criação, carregando colunas e tarefas."""
        result = await session.scalars(self._board_query().order_by(Board.created_at.desc()))
        return list(result)

    async def get(self, session: AsyncSession, board_id: uuid.UUID) -> Board:
        """Obtém um quadro específico pelo ID. Lança NotFoundError se não existir."""
        board = await session.scalar(self._board_query().where(Board.id == board_id))
        if board is None:
            raise NotFoundError("Board não encontrado")
        return board

    async def create(self, session: AsyncSession, data: BoardCreate, owner_id: uuid.UUID) -> Board:
        """Cria um novo quadro no banco e popula automaticamente com as colunas padrão."""
        board = Board(
            title=data.title,
            description=data.description,
            owner_id=owner_id,
        )
        session.add(board)
        await session.flush()

        default_columns = [
            BoardColumn(board_id=board.id, name=name, position=pos)
            for name, pos in DEFAULT_BOARD_COLUMNS
        ]
        session.add_all(default_columns)

        await session.commit()
        return await self.get(session, board.id)

    async def update(self, session: AsyncSession, board_id: uuid.UUID, data: BoardUpdate) -> Board:
        """Atualiza parcialmente as informações de um quadro."""
        board = await self.get(session, board_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(board, key, value)

        await session.commit()
        return await self.get(session, board.id)

    async def delete(self, session: AsyncSession, board_id: uuid.UUID) -> None:
        """Remove um quadro do banco de dados."""
        board = await self.get(session, board_id)
        await session.delete(board)
        await session.commit()

    async def create_column(self, session: AsyncSession, data: BoardColumnCreate) -> BoardColumn:
        """Adiciona uma nova coluna a um quadro garantindo a existência do Board pai."""
        await self.get(session, data.board_id)
        column = BoardColumn(**data.model_dump())
        session.add(column)
        await session.commit()

        reloaded = await session.scalar(
            select(BoardColumn)
            .where(BoardColumn.id == column.id)
            .options(selectinload(BoardColumn.tasks))
        )
        if reloaded is None:
            raise RuntimeError("Coluna criada não pôde ser recarregada")
        return reloaded

    async def update_column(
        self, session: AsyncSession, column_id: uuid.UUID, data: BoardColumnUpdate
    ) -> BoardColumn:
        """Atualiza as propriedades de uma coluna existente."""
        column = await session.scalar(
            select(BoardColumn)
            .where(BoardColumn.id == column_id)
            .options(selectinload(BoardColumn.tasks))
        )
        if column is None:
            raise NotFoundError("Coluna não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(column, key, value)

        await session.commit()
        reloaded = await session.scalar(
            select(BoardColumn)
            .where(BoardColumn.id == column_id)
            .options(selectinload(BoardColumn.tasks))
        )
        if reloaded is None:
            raise NotFoundError("Coluna não encontrada")
        return reloaded

    async def delete_column(self, session: AsyncSession, column_id: uuid.UUID) -> None:
        """Deleta uma coluna e suas tarefas associadas."""
        column = await session.scalar(select(BoardColumn).where(BoardColumn.id == column_id))
        if column is None:
            raise NotFoundError("Coluna não encontrada")
        await session.delete(column)
        await session.commit()

    async def create_task(self, session: AsyncSession, data: TaskCreate) -> Task:
        """Cria uma tarefa dentro de uma coluna válida."""
        column = await session.scalar(select(BoardColumn).where(BoardColumn.id == data.column_id))
        if column is None:
            raise NotFoundError("Coluna de destino não encontrada")

        task = Task(**data.model_dump())
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def update_task(
        self, session: AsyncSession, task_id: uuid.UUID, data: TaskUpdate
    ) -> Task:
        """Atualiza dados do card/tarefa, incluindo troca de coluna se aplicável."""
        task = await session.scalar(select(Task).where(Task.id == task_id))
        if task is None:
            raise NotFoundError("Tarefa não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        if "column_id" in update_data and update_data["column_id"] is not None:
            target_column = await session.scalar(
                select(BoardColumn).where(BoardColumn.id == update_data["column_id"])
            )
            if target_column is None:
                raise NotFoundError("Coluna de destino não encontrada")

        for key, value in update_data.items():
            setattr(task, key, value)

        await session.commit()
        await session.refresh(task)
        return task

    async def delete_task(self, session: AsyncSession, task_id: uuid.UUID) -> None:
        """Remove um card do quadro."""
        task = await session.scalar(select(Task).where(Task.id == task_id))
        if task is None:
            raise NotFoundError("Tarefa não encontrada")
        await session.delete(task)
        await session.commit()

    def _board_query(self):
        """Query padrão para listagem e obtenção de Boards com eager loading."""
        return select(Board).options(selectinload(Board.columns).selectinload(BoardColumn.tasks))


board_manager = BoardManager()
