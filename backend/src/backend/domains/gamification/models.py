import uuid
from datetime import datetime
from enum import StrEnum

from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class WorkType(StrEnum):
    BACK = "back"
    FRONT = "front"
    FULLSTACK = "fullstack"
    DATABASE = "banco_de_dados"
    API = "api"


class WorkSessionStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AchievementCode(StrEnum):
    INITIAL = "initial"
    BASIC = "basic"
    MEDIUM = "medium"
    ADVANCED = "advanced"
    MASTER = "master"


class WorkSession(Base):
    __tablename__ = "work_sessions"
    __table_args__ = (
        CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_sessions_work_type",
        ),
        CheckConstraint(
            "status IN ('active', 'paused', 'completed', 'cancelled')",
            name="ck_work_sessions_status",
        ),
        CheckConstraint(
            "total_seconds >= 0",
            name="ck_work_sessions_total_seconds",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=WorkSessionStatus.ACTIVE, index=True
    )
    total_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False
    )

    intervals: Mapped[list["WorkSessionInterval"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", lazy="raise"
    )


class WorkSessionInterval(Base):
    __tablename__ = "work_session_intervals"
    __table_args__ = (
        CheckConstraint(
            "duration_seconds >= 0",
            name="ck_work_session_intervals_duration_seconds",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("work_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    session: Mapped[WorkSession] = relationship(back_populates="intervals", lazy="raise")


class WorkHourEntry(Base):
    __tablename__ = "work_hour_entries"
    __table_args__ = (
        CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_hour_entries_work_type",
        ),
        CheckConstraint(
            "seconds_delta <> 0",
            name="ck_work_hour_entries_seconds_delta",
        ),
        UniqueConstraint(
            "source_type",
            "source_id",
            name="uq_work_hour_entries_source",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    seconds_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    total_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False
    )


class UserWorkTypeProgress(Base):
    __tablename__ = "user_work_type_progress"
    __table_args__ = (
        CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_user_work_type_progress_work_type",
        ),
        UniqueConstraint("user_id", "work_type", name="uq_user_work_type_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_type: Mapped[str] = mapped_column(String(30), nullable=False)
    total_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_code", name="uq_user_achievements_user_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_code: Mapped[str] = mapped_column(String(30), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
    progress_snapshot_seconds: Mapped[int] = mapped_column(Integer, nullable=False)


class WorkHourAdjustment(Base):
    __tablename__ = "work_hour_adjustments"
    __table_args__ = (
        CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_hour_adjustments_work_type",
        ),
        CheckConstraint(
            "seconds_delta <> 0",
            name="ck_work_hour_adjustments_seconds_delta",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    admin_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    work_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    seconds_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
