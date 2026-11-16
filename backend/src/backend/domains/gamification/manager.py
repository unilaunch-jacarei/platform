import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domains.gamification.models import (
    UserAchievement,
    UserProgress,
    UserWorkTypeProgress,
    WorkHourAdjustment,
    WorkHourEntry,
    WorkSession,
    WorkSessionInterval,
)
from backend.error import ConflictError, NotFoundError


class GamificationManager:
    async def get_session(
        self, session: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> WorkSession:
        work_session = await session.scalar(
            select(WorkSession)
            .where(WorkSession.id == session_id, WorkSession.user_id == user_id)
            .with_for_update()
        )
        if work_session is None:
            raise NotFoundError("Sessão de trabalho não encontrada")
        return work_session

    async def get_open_interval(
        self, session: AsyncSession, work_session: WorkSession
    ) -> WorkSessionInterval:
        interval = await session.scalar(
            select(WorkSessionInterval).where(
                WorkSessionInterval.session_id == work_session.id,
                WorkSessionInterval.ended_at.is_(None),
            )
        )
        if interval is None:
            raise ConflictError("Sessão não possui intervalo ativo")
        return interval

    async def get_progress(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> UserProgress | None:
        return await session.get(UserProgress, user_id)

    async def list_work_type_progress(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> list[UserWorkTypeProgress]:
        result = await session.scalars(
            select(UserWorkTypeProgress)
            .where(UserWorkTypeProgress.user_id == user_id)
            .order_by(UserWorkTypeProgress.work_type)
        )
        return list(result)

    async def list_hour_entries(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> list[WorkHourEntry]:
        result = await session.scalars(
            select(WorkHourEntry)
            .where(WorkHourEntry.user_id == user_id)
            .order_by(WorkHourEntry.created_at.desc())
        )
        return list(result)

    async def list_sessions(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> list[WorkSession]:
        result = await session.scalars(
            select(WorkSession)
            .where(WorkSession.user_id == user_id)
            .order_by(WorkSession.created_at.desc())
        )
        return list(result)

    async def list_achievements(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> list[UserAchievement]:
        result = await session.scalars(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at)
        )
        return list(result)

    async def list_adjustments(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> list[WorkHourAdjustment]:
        result = await session.scalars(
            select(WorkHourAdjustment)
            .where(WorkHourAdjustment.user_id == user_id)
            .order_by(WorkHourAdjustment.created_at.desc())
        )
        return list(result)

    async def delete_achievement(
        self, session: AsyncSession, user_id: uuid.UUID, code: str
    ) -> None:
        await session.execute(
            delete(UserAchievement).where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_code == code,
            )
        )

    async def get_or_create_progress(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> UserProgress:
        progress = await session.get(UserProgress, user_id)
        if progress is None:
            progress = UserProgress(user_id=user_id)
            session.add(progress)
            await session.flush()
        return progress


gamification_manager = GamificationManager()
