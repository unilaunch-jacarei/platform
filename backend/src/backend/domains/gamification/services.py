import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domains.gamification.manager import gamification_manager
from backend.domains.gamification.models import (
    UserAchievement,
    UserWorkTypeProgress,
    WorkHourAdjustment,
    WorkHourEntry,
    WorkSession,
    WorkSessionInterval,
    WorkSessionStatus,
)
from backend.domains.gamification.rules import (
    ACHIEVEMENTS,
    SECONDS_PER_HOUR,
    get_level_from_seconds,
)
from backend.domains.gamification.schemas import HourAdjustmentCreate, WorkSessionCreate
from backend.error import BadRequestError, ConflictError


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def elapsed_seconds(started_at: datetime, ended_at: datetime) -> int:
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    if ended_at.tzinfo is None:
        ended_at = ended_at.replace(tzinfo=timezone.utc)
    return max(0, int((ended_at - started_at).total_seconds()))


async def recalculate_progress(session: AsyncSession, user_id: uuid.UUID) -> None:
    total_seconds = await session.scalar(
        select(func.coalesce(func.sum(WorkHourEntry.seconds_delta), 0)).where(
            WorkHourEntry.user_id == user_id
        )
    )
    type_rows = await session.execute(
        select(
            WorkHourEntry.work_type,
            func.coalesce(func.sum(WorkHourEntry.seconds_delta), 0),
        )
        .where(WorkHourEntry.user_id == user_id)
        .group_by(WorkHourEntry.work_type)
    )
    progress = await gamification_manager.get_or_create_progress(session, user_id)
    progress.total_seconds = max(0, int(total_seconds or 0))
    progress.current_level = get_level_from_seconds(progress.total_seconds)
    progress.updated_at = utc_now()

    existing_types = {
        row.work_type: row
        for row in await session.scalars(
            select(UserWorkTypeProgress).where(UserWorkTypeProgress.user_id == user_id)
        )
    }
    for work_type, seconds in type_rows:
        type_progress = existing_types.get(work_type)
        if type_progress is None:
            type_progress = UserWorkTypeProgress(user_id=user_id, work_type=work_type)
            session.add(type_progress)
        type_progress.total_seconds = max(0, int(seconds or 0))
        type_progress.updated_at = utc_now()

    current_codes = {
        achievement.achievement_code
        for achievement in await gamification_manager.list_achievements(session, user_id)
    }
    required_codes = {
        achievement.code.value
        for achievement in ACHIEVEMENTS
        if progress.current_level >= achievement.required_level
    }
    for code in current_codes - required_codes:
        await gamification_manager.delete_achievement(session, user_id, code)
    for achievement in ACHIEVEMENTS:
        if achievement.code.value in required_codes and achievement.code.value not in current_codes:
            session.add(
                UserAchievement(
                    user_id=user_id,
                    achievement_code=achievement.code.value,
                    progress_snapshot_seconds=progress.total_seconds,
                )
            )

    await session.flush()


async def start_work_session(
    session: AsyncSession, user_id: uuid.UUID, data: WorkSessionCreate
) -> WorkSession:
    now = utc_now()
    work_session = WorkSession(
        user_id=user_id,
        work_type=data.work_type.value,
        status=WorkSessionStatus.ACTIVE,
        started_at=now,
    )
    session.add(work_session)
    await session.flush()
    session.add(WorkSessionInterval(session_id=work_session.id, started_at=now))
    await session.commit()
    await session.refresh(work_session)
    return work_session


async def pause_work_session(
    session: AsyncSession, work_session: WorkSession
) -> WorkSession:
    if work_session.status != WorkSessionStatus.ACTIVE:
        raise ConflictError("Somente sessões ativas podem ser pausadas")
    now = utc_now()
    interval = await gamification_manager.get_open_interval(session, work_session)
    interval.ended_at = now
    interval.duration_seconds = elapsed_seconds(interval.started_at, now)
    work_session.total_seconds += interval.duration_seconds
    work_session.status = WorkSessionStatus.PAUSED
    work_session.updated_at = now
    await session.commit()
    await session.refresh(work_session)
    return work_session


async def resume_work_session(
    session: AsyncSession, work_session: WorkSession
) -> WorkSession:
    if work_session.status != WorkSessionStatus.PAUSED:
        raise ConflictError("Somente sessões pausadas podem ser retomadas")
    now = utc_now()
    work_session.status = WorkSessionStatus.ACTIVE
    work_session.updated_at = now
    session.add(WorkSessionInterval(session_id=work_session.id, started_at=now))
    await session.commit()
    await session.refresh(work_session)
    return work_session


async def finish_work_session(
    session: AsyncSession, work_session: WorkSession
) -> WorkSession:
    if work_session.status not in {WorkSessionStatus.ACTIVE, WorkSessionStatus.PAUSED}:
        raise ConflictError("Somente sessões ativas ou pausadas podem ser finalizadas")
    now = utc_now()
    if work_session.status == WorkSessionStatus.ACTIVE:
        interval = await gamification_manager.get_open_interval(session, work_session)
        interval.ended_at = now
        interval.duration_seconds = elapsed_seconds(interval.started_at, now)
        work_session.total_seconds += interval.duration_seconds
    work_session.status = WorkSessionStatus.COMPLETED
    work_session.finished_at = now
    work_session.updated_at = now
    if work_session.total_seconds > 0:
        session.add(
            WorkHourEntry(
                user_id=work_session.user_id,
                work_type=work_session.work_type,
                seconds_delta=work_session.total_seconds,
                source_type="work_session",
                source_id=work_session.id,
            )
        )
    await recalculate_progress(session, work_session.user_id)
    await session.commit()
    await session.refresh(work_session)
    return work_session


async def cancel_work_session(
    session: AsyncSession, work_session: WorkSession
) -> WorkSession:
    if work_session.status in {WorkSessionStatus.COMPLETED, WorkSessionStatus.CANCELLED}:
        raise ConflictError("Sessão já encerrada")
    if work_session.status == WorkSessionStatus.ACTIVE:
        now = utc_now()
        interval = await gamification_manager.get_open_interval(session, work_session)
        interval.ended_at = now
        interval.duration_seconds = elapsed_seconds(interval.started_at, now)
        work_session.total_seconds += interval.duration_seconds
    work_session.status = WorkSessionStatus.CANCELLED
    work_session.updated_at = utc_now()
    await session.commit()
    await session.refresh(work_session)
    return work_session


async def create_hour_adjustment(
    session: AsyncSession,
    user_id: uuid.UUID,
    admin_id: uuid.UUID,
    data: HourAdjustmentCreate,
) -> WorkHourAdjustment:
    if data.seconds_delta < 0:
        current_total = await session.scalar(
            select(func.coalesce(func.sum(WorkHourEntry.seconds_delta), 0)).where(
                WorkHourEntry.user_id == user_id,
                WorkHourEntry.work_type == data.work_type.value,
            )
        )
        if int(current_total or 0) + data.seconds_delta < 0:
            raise BadRequestError(
                "O ajuste não pode deixar o total de horas do tipo de trabalho negativo"
            )
    adjustment = WorkHourAdjustment(
        user_id=user_id,
        admin_id=admin_id,
        work_type=data.work_type.value,
        seconds_delta=data.seconds_delta,
        reason=data.reason.strip(),
    )
    session.add(adjustment)
    await session.flush()
    session.add(
        WorkHourEntry(
            user_id=user_id,
            work_type=data.work_type.value,
            seconds_delta=data.seconds_delta,
            source_type="admin_adjustment",
            source_id=adjustment.id,
            description=data.reason.strip(),
        )
    )
    await recalculate_progress(session, user_id)
    await session.commit()
    await session.refresh(adjustment)
    return adjustment
