import pytest

from backend.main import create_app, lifespan


@pytest.mark.asyncio
async def test_app_lifespan():
    app = create_app()
    async with lifespan(app):
        assert app.state.limiter is not None
