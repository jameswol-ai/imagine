"""IMAGINE Site Planning repository."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import SitePlan


class SitePlanningRepository:
    """Async persistence layer for Site Planning."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        project_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[SitePlan]:
        statement = select(SitePlan).order_by(SitePlan.created_at.desc())
        if project_id is not None:
            statement = statement.where(SitePlan.project_id == project_id)
        if active_only:
            statement = statement.where(SitePlan.active.is_(True))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get(self, site_plan_id: UUID) -> SitePlan | None:
        return await self.session.get(SitePlan, site_plan_id)

    async def get_by_code(self, site_code: str) -> SitePlan | None:
        statement = select(SitePlan).where(SitePlan.site_code == site_code.strip().upper())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, site_plan: SitePlan) -> SitePlan:
        self.session.add(site_plan)
        await self.session.flush()
        await self.session.refresh(site_plan)
        return site_plan

    async def update(self, site_plan: SitePlan, values: dict[str, Any]) -> SitePlan:
        for key, value in values.items():
            if hasattr(site_plan, key):
                setattr(site_plan, key, value)
        await self.session.flush()
        await self.session.refresh(site_plan)
        return site_plan

    async def delete(self, site_plan: SitePlan) -> None:
        await self.session.delete(site_plan)
        await self.session.flush()

    async def summary(self) -> dict[str, Any]:
        result = await self.session.execute(
            select(
                func.count(SitePlan.id),
                func.sum(func.cast(SitePlan.active, 1)),
                func.sum(func.cast(SitePlan.status == "Approved", 1)),
                func.coalesce(func.sum(SitePlan.site_area_m2), 0),
                func.coalesce(func.sum(SitePlan.landscape_area_m2), 0),
            )
        )
        total, active, approved, site_area, landscape = result.one()
        return {
            "total_plans": int(total or 0),
            "active_plans": int(active or 0),
            "approved_plans": int(approved or 0),
            "total_site_area_m2": site_area or 0,
            "total_landscaped_area_m2": landscape or 0,
        }


# Backward-compatible name retained for existing imports and tests.
SitePlanRepository = SitePlanningRepository


__all__ = ["SitePlanningRepository", "SitePlanRepository"]
