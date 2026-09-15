import asyncio
from datetime import UTC, datetime, timedelta

from backend.config import get_settings
from backend.database import close_db, get_session_factory
from backend.domains.leads.manager import lead_service


async def purge_expired_leads() -> int:
    settings = get_settings()
    cutoff = datetime.now(UTC) - timedelta(days=settings.lead_retention_days)
    async with get_session_factory()() as session:
        return await lead_service.purge_before(session, cutoff)


async def _run() -> None:
    try:
        deleted = await purge_expired_leads()
        print(f"Deleted {deleted} expired leads")
    finally:
        await close_db()


def run() -> None:
    asyncio.run(_run())
