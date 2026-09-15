from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend import cleanup


@pytest.mark.asyncio
async def test_purge_expired_leads_uses_configured_retention(monkeypatch):
    session = object()

    class SessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *_args):
            return None

    purge = AsyncMock(return_value=3)
    monkeypatch.setattr(cleanup, "get_settings", lambda: SimpleNamespace(lead_retention_days=30))
    monkeypatch.setattr(cleanup, "get_session_factory", lambda: lambda: SessionContext())
    monkeypatch.setattr(cleanup.lead_service, "purge_before", purge)

    assert await cleanup.purge_expired_leads() == 3
    assert purge.await_args.args[0] is session
    assert 29 <= (cleanup.datetime.now(cleanup.UTC) - purge.await_args.args[1]).days <= 30
