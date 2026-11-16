import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
from backend.domains.gamification.models import (
    UserAchievement,
    UserProgress,
    WorkSession,
    WorkSessionInterval,
    WorkSessionStatus,
)
from backend.domains.gamification.schemas import HourAdjustmentCreate, WorkSessionCreate
from backend.domains.gamification.services import (
    cancel_work_session,
    create_hour_adjustment,
    elapsed_seconds,
    finish_work_session,
    pause_work_session,
    resume_work_session,
    start_work_session,
)
from backend.domains.usuarios.models import User


@pytest_asyncio.fixture
async def gamification_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    user = User(
        id=uuid.uuid4(),
        email="gamification@example.com",
        hashed_password="hash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        nome="Gamification User",
    )
    async with factory() as session:
        session.add(user)
        await session.commit()
        yield factory, user.id
    await engine.dispose()


def test_elapsed_seconds_preserves_second_precision():
    start = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 10, 1, 17, tzinfo=timezone.utc)
    assert elapsed_seconds(start, end) == 77
    assert elapsed_seconds(start.replace(tzinfo=None), end) == 77


@pytest.mark.asyncio
async def test_pause_resume_and_finish_accumulate_intervals(gamification_session, monkeypatch):
    factory, user_id = gamification_session
    times = iter(
        [
            datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 10, 0, 30, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 1, 12, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 1, 12, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 1, 12, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 11, 1, 12, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(
        "backend.domains.gamification.services.utc_now",
        lambda: next(times),
    )

    async with factory() as session:
        work_session = await start_work_session(
            session, user_id, WorkSessionCreate(work_type="back")
        )
        await pause_work_session(session, work_session)
        await resume_work_session(session, work_session)
        work_session = await finish_work_session(session, work_session)
        assert work_session.status == WorkSessionStatus.COMPLETED
        assert work_session.total_seconds == 102
        intervals = await session.scalars(
            select(WorkSessionInterval).where(
                WorkSessionInterval.session_id == work_session.id
            )
        )
        assert len(list(intervals)) == 2


@pytest.mark.asyncio
async def test_cancelled_session_does_not_create_hours(gamification_session):
    factory, user_id = gamification_session
    async with factory() as session:
        work_session = WorkSession(
            id=uuid.uuid4(),
            user_id=user_id,
            work_type="front",
            status=WorkSessionStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
        )
        session.add(work_session)
        session.add(
            WorkSessionInterval(
                session_id=work_session.id,
                started_at=work_session.started_at,
            )
        )
        await session.commit()
        await cancel_work_session(session, work_session)
        assert work_session.status == WorkSessionStatus.CANCELLED
        interval = await session.scalar(
            select(WorkSessionInterval).where(
                WorkSessionInterval.session_id == work_session.id
            )
        )
        assert interval is not None
        assert interval.ended_at is not None


@pytest.mark.asyncio
async def test_adjustment_recalculates_level_and_removes_regressed_achievements(
    gamification_session,
):
    factory, user_id = gamification_session
    async with factory() as session:
        await create_hour_adjustment(
            session,
            user_id,
            user_id,
            HourAdjustmentCreate(work_type="back", seconds_delta=10 * 60 * 60, reason="validado"),
        )
        progress = await session.get(UserProgress, user_id)
        assert progress is not None
        assert progress.current_level == 2
        assert len((await session.scalars(select(UserAchievement))).all()) == 2

        await create_hour_adjustment(
            session,
            user_id,
            user_id,
            HourAdjustmentCreate(work_type="back", seconds_delta=-5 * 60 * 60, reason="correção"),
        )
        progress = await session.get(UserProgress, user_id)
        assert progress is not None
        assert progress.total_seconds == 5 * 60 * 60
        assert progress.current_level == 1
        achievements = (await session.scalars(select(UserAchievement))).all()
        assert [achievement.achievement_code for achievement in achievements] == ["initial"]
