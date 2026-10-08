import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.domains.tasks.models import Task
from backend.domains.tasks.schemas import TaskCreate, TaskRead, TaskUpdate
from backend.domains.usuarios.auth import current_active_user
from backend.domains.usuarios.models import User

router = APIRouter(prefix = '/tasks', tags = ['tasks'])

@router.post(
    "",
    response_model = TaskRead,
    status_code = status.HTTP_201_CREATED,
)

async def create_task(
    data: TaskCreate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    task = Task(
        title = data.title,
        description = data.description,
        user_id = current_user.id,
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task

@router.get("", response_model = list[TaskRead])
async def list_tasks(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Task)
        .where(Task.user_id == current_user)
        .order_by(Task.created_at.desc())
    )
    
    return result.scalars().all()

@router.get('/{task_id}', response_model = TaskRead)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Task não encontrada',
        )
    
    return task

@router.patch('/{task_id}', response_model = TaskRead)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Task não encontrada',
        )
    
    update_data = data.model_dump(exclude_unset = True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await session.commit()
    await session.refresh(task)
    return task

@router.delete('/{task_id}', status_code = status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_active_user,
        )
    )
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Task não encontrada',
        )
        
    await session.delete(task)
    await session.commit()