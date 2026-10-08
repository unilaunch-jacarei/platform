import uuid
from datetime import datetime
from sqlalchemy import Boolean, Datetime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

class Task(Base):
    __tablename__ = 'tasks'
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key = True,
        default = uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable = False)
    description: Mapped[str | None] = mapped_column(String(255), nullable = True)
    completed: Mapped[bool] = mapped_column(Boolean, default = False, nullable = False)
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('usuarios.id', ondelete = 'CASCADE'),
        nullable = False,
        index = True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        Datetime(timezone = True),
        server_default = func.now(),
        nullable = False,
    )
    
    update_at: Mapped[datetime] = mapped_column(
        Datetime(timezone = True),
        server_default = func.now(),
        onupdate = func.now(),
        nullable = False,
    )