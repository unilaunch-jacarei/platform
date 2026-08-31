import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from backend.database import (
    close_db,
    get_db,
    get_engine,
    get_session_factory,
    init_db,
)


@pytest.mark.asyncio
async def test_database_lifecycle():
    # 1. Get engine
    engine = get_engine()
    assert isinstance(engine, AsyncEngine)

    # 2. Get session factory
    factory = get_session_factory()
    assert isinstance(factory, async_sessionmaker)

    # 3. Init db
    await init_db()

    # 4. Get db dependency generator
    gen = get_db()
    session = await anext(gen)
    assert session is not None
    await session.close()

    # 5. Close db
    await close_db()
