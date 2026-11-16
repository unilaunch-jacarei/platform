import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.gamification.manager import gamification_manager
from backend.domains.gamification.models import WorkSession
from backend.domains.gamification.rules import (
    ACHIEVEMENTS,
    LEVEL_HOURS,
    SECONDS_PER_HOUR,
    get_level_name,
)
from backend.domains.gamification.schemas import (
    AchievementRead,
    HourAdjustmentCreate,
    HourAdjustmentRead,
    HourEntryRead,
    ProgressRead,
    WorkSessionCreate,
    WorkSessionRead,
    WorkTypeProgressRead,
)
from backend.domains.gamification.services import (
    cancel_work_session,
    create_hour_adjustment,
    finish_work_session,
    pause_work_session,
    resume_work_session,
    start_work_session,
)
from backend.domains.usuarios.auth import current_active_user, current_superuser
from backend.domains.usuarios.models import User
from backend.error import NotFoundError

gamification_router = APIRouter(prefix="/gamification", tags=["gamification"])


async def get_owned_session(
    session_id: uuid.UUID,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    return await gamification_manager.get_session(session, session_id, user.id)


@gamification_router.post(
    "/work-sessions", response_model=WorkSessionRead, status_code=status.HTTP_201_CREATED
)
async def create_work_session(
    data: WorkSessionCreate,
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkSessionRead:
    return await start_work_session(session, user.id, data)


@gamification_router.post("/work-sessions/{session_id}/pause", response_model=WorkSessionRead)
async def pause_session(
    work_session: Annotated[WorkSession, Depends(get_owned_session)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkSessionRead:
    return await pause_work_session(session, work_session)


@gamification_router.post("/work-sessions/{session_id}/resume", response_model=WorkSessionRead)
async def resume_session(
    work_session: Annotated[WorkSession, Depends(get_owned_session)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkSessionRead:
    return await resume_work_session(session, work_session)


@gamification_router.post("/work-sessions/{session_id}/finish", response_model=WorkSessionRead)
async def finish_session(
    work_session: Annotated[WorkSession, Depends(get_owned_session)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkSessionRead:
    return await finish_work_session(session, work_session)


@gamification_router.post("/work-sessions/{session_id}/cancel", response_model=WorkSessionRead)
async def cancel_session(
    work_session: Annotated[WorkSession, Depends(get_owned_session)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> WorkSessionRead:
    return await cancel_work_session(session, work_session)


@gamification_router.get("/work-sessions", response_model=list[WorkSessionRead])
async def list_sessions(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[WorkSessionRead]:
    return await gamification_manager.list_sessions(session, user.id)


@gamification_router.get("/me/progress", response_model=ProgressRead)
async def get_my_progress(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ProgressRead:
    progress = await gamification_manager.get_progress(session, user.id)
    total_seconds = progress.total_seconds if progress else 0
    current_level = progress.current_level if progress else 1
    next_level = current_level + 1 if current_level < 5 else None
    next_seconds = LEVEL_HOURS[next_level] * SECONDS_PER_HOUR if next_level else total_seconds
    work_types = await gamification_manager.list_work_type_progress(session, user.id)
    return ProgressRead(
        user_id=user.id,
        total_seconds=total_seconds,
        total_hours=total_seconds / SECONDS_PER_HOUR,
        current_level=current_level,
        current_level_name=get_level_name(current_level),
        next_level=next_level,
        next_level_name=get_level_name(next_level) if next_level else None,
        seconds_to_next_level=max(0, next_seconds - total_seconds),
        work_types=[
            WorkTypeProgressRead(
                work_type=item.work_type,
                total_seconds=item.total_seconds,
                total_hours=item.total_seconds / SECONDS_PER_HOUR,
            )
            for item in work_types
        ],
    )


@gamification_router.get("/users/{user_id}/progress", response_model=ProgressRead)
async def get_user_progress(
    user_id: uuid.UUID,
    _admin: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ProgressRead:
    if await session.get(User, user_id) is None:
        raise NotFoundError("Usuário não encontrado")
    progress = await gamification_manager.get_progress(session, user_id)
    total_seconds = progress.total_seconds if progress else 0
    current_level = progress.current_level if progress else 1
    next_level = current_level + 1 if current_level < 5 else None
    next_seconds = LEVEL_HOURS[next_level] * SECONDS_PER_HOUR if next_level else total_seconds
    work_types = await gamification_manager.list_work_type_progress(session, user_id)
    return ProgressRead(
        user_id=user_id,
        total_seconds=total_seconds,
        total_hours=total_seconds / SECONDS_PER_HOUR,
        current_level=current_level,
        current_level_name=get_level_name(current_level),
        next_level=next_level,
        next_level_name=get_level_name(next_level) if next_level else None,
        seconds_to_next_level=max(0, next_seconds - total_seconds),
        work_types=[
            WorkTypeProgressRead(
                work_type=item.work_type,
                total_seconds=item.total_seconds,
                total_hours=item.total_seconds / SECONDS_PER_HOUR,
            )
            for item in work_types
        ],
    )


@gamification_router.get("/me/hours", response_model=list[HourEntryRead])
async def list_my_hours(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[HourEntryRead]:
    return await gamification_manager.list_hour_entries(session, user.id)


@gamification_router.get("/me/achievements", response_model=list[AchievementRead])
async def list_my_achievements(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[AchievementRead]:
    unlocked = {
        item.achievement_code: item
        for item in await gamification_manager.list_achievements(session, user.id)
    }
    progress = await gamification_manager.get_progress(session, user.id)
    current_level = progress.current_level if progress else 1
    return [
        AchievementRead(
            code=item.code,
            name=item.name,
            description=item.description,
            required_level=item.required_level,
            unlocked=current_level >= item.required_level,
            unlocked_at=unlocked[item.code.value].unlocked_at
            if item.code.value in unlocked and current_level >= item.required_level
            else None,
        )
        for item in ACHIEVEMENTS
    ]


@gamification_router.get("/achievements", response_model=list[AchievementRead])
async def list_achievement_catalog(
    _user: Annotated[User, Depends(current_active_user)],
) -> list[AchievementRead]:
    return [
        AchievementRead(
            code=item.code,
            name=item.name,
            description=item.description,
            required_level=item.required_level,
            unlocked=False,
        )
        for item in ACHIEVEMENTS
    ]


@gamification_router.post(
    "/users/{user_id}/hour-adjustments",
    response_model=HourAdjustmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_hour_adjustment(
    user_id: uuid.UUID,
    data: HourAdjustmentCreate,
    admin: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HourAdjustmentRead:
    if await session.get(User, user_id) is None:
        raise NotFoundError("Usuário não encontrado")
    return await create_hour_adjustment(session, user_id, admin.id, data)


@gamification_router.get(
    "/users/{user_id}/hours", response_model=list[HourEntryRead]
)
async def list_user_hours(
    user_id: uuid.UUID,
    _admin: Annotated[User, Depends(current_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[HourEntryRead]:
    if await session.get(User, user_id) is None:
        raise NotFoundError("Usuário não encontrado")
    return await gamification_manager.list_hour_entries(session, user_id)
