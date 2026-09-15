import pytest
from httpx import ASGITransport, AsyncClient

from backend.config import get_settings
from backend.main import create_app, lifespan


@pytest.mark.asyncio
async def test_app_lifespan():
    app = create_app()
    async with lifespan(app):
        assert app.state.limiter is not None


@pytest.mark.asyncio
async def test_metrics_token(monkeypatch):
    token = "metrics-token-with-at-least-32-characters"
    monkeypatch.setenv("METRICS_TOKEN", token)
    get_settings.cache_clear()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/metrics")).status_code == 401
        assert (await client.get("/missing")).status_code == 404
        response = await client.get("/metrics", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "http_request_errors_total" in response.text
        assert 'status_class="4xx"' in response.text
    get_settings.cache_clear()
