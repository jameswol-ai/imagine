"""
IMAGINE
Site Planning Service

Provides the asynchronous Site Planning domain service used by
the API and a synchronous adapter used by Streamlit and other
synchronous callers.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import AsyncSessionLocal

from .models import SitePlan
from .repository import SitePlanRepository
from .schemas import SitePlanCreate, SitePlanUpdate


class SitePlanService:
    """Application service for Site Planning."""

    def __init__(self, session: AsyncSession):
        self.repo = SitePlanRepository(session)

    async def list(self, project_id: UUID | None = None, active_only: bool = False) -> list[SitePlan]:
        return await self.repo.list(project_id=project_id, active_only=active_only)

    async def get(self, site_plan_id: UUID) -> SitePlan | None:
        return await self.repo.get(site_plan_id)

    async def create(self, payload: SitePlanCreate) -> SitePlan:
        existing = await self.repo.get_by_code(payload.site_code)
        if existing:
            raise ValueError(f"Site plan code already exists: {payload.site_code}")
        values = payload.model_dump()
        self._validate_area_allocation(values)
        return await self.repo.create(SitePlan(**values))

    async def update(self, site_plan_id: UUID, payload: SitePlanUpdate) -> SitePlan:
        obj = await self.repo.get(site_plan_id)
        if not obj:
            raise LookupError("Site plan not found")
        values = payload.model_dump(exclude_unset=True)
        if "site_code" in values:
            existing = await self.repo.get_by_code(values["site_code"])
            if existing and existing.id != obj.id:
                raise ValueError(f"Site plan code already exists: {values['site_code']}")
        merged = {key: getattr(obj, key) for key in (
            "site_area_m2", "building_footprint_m2", "road_area_m2",
            "parking_area_m2", "landscape_area_m2",
        )}
        merged.update(values)
        self._validate_area_allocation(merged)
        return await self.repo.update(obj, values)

    async def delete(self, site_plan_id: UUID) -> None:
        obj = await self.repo.get(site_plan_id)
        if not obj:
            raise LookupError("Site plan not found")
        await self.repo.delete(obj)

    async def summary(self) -> dict[str, Any]:
        return await self.repo.summary()

    @staticmethod
    def _run_sync(operation: Callable[[AsyncSession], Awaitable[Any]]) -> Any:
        async def runner() -> Any:
            async with AsyncSessionLocal() as session:
                try:
                    result = await operation(session)
                    await session.commit()
                    return result
                except Exception:
                    await session.rollback()
                    raise

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(runner())
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(asyncio.run, runner()).result()

    @staticmethod
    def _coerce_create_payload(payload: SitePlanCreate | dict[str, Any]) -> SitePlanCreate:
        if isinstance(payload, SitePlanCreate):
            return payload
        return SitePlanCreate.model_validate(payload)

    @staticmethod
    def _coerce_update_payload(payload: SitePlanUpdate | dict[str, Any]) -> SitePlanUpdate:
        if isinstance(payload, SitePlanUpdate):
            return payload
        return SitePlanUpdate.model_validate(payload)

    def list_sync(self, project_id: UUID | None = None, active_only: bool = False) -> list[SitePlan]:
        return self._run_sync(lambda session: SitePlanService(session).list(project_id, active_only))

    def create_sync(self, payload: SitePlanCreate | dict[str, Any]) -> SitePlan:
        validated = self._coerce_create_payload(payload)
        return self._run_sync(lambda session: SitePlanService(session).create(validated))

    def update_sync(self, site_plan_id: UUID, payload: SitePlanUpdate | dict[str, Any]) -> SitePlan:
        validated = self._coerce_update_payload(payload)
        return self._run_sync(lambda session: SitePlanService(session).update(site_plan_id, validated))

    def delete_sync(self, site_plan_id: UUID) -> None:
        return self._run_sync(lambda session: SitePlanService(session).delete(site_plan_id))

    def summary_sync(self) -> dict[str, Any]:
        return self._run_sync(lambda session: SitePlanService(session).summary())

    @staticmethod
    def _validate_area_allocation(values: dict[str, Any]) -> None:
        site_area = values["site_area_m2"]
        allocated = sum((values.get(key, 0) or 0) for key in (
            "building_footprint_m2", "road_area_m2", "parking_area_m2", "landscape_area_m2",
        ))
        if allocated > site_area:
            raise ValueError("Building, road, parking and landscape areas cannot exceed site area")


# Compatibility alias used by older integration code and external callers.
SitePlanningService = SitePlanService

__all__ = ["SitePlanService", "SitePlanningService"]
