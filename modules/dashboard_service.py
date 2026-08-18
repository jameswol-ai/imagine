from __future__ import annotations

import asyncio

from database.connection import AsyncSessionLocal
from projects.projects.service import ProjectService


def _load_dashboard_metrics():
    async def _load():
        async with AsyncSessionLocal() as db:
            return await ProjectService.get_dashboard_metrics(db)

    return asyncio.run(_load())


def get_dashboard_metrics():
    """
    Streamlit-safe bridge to the Projects service.
    """
    return _load_dashboard_metrics()