from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import SitePlan

class SitePlanRepository:
    def __init__(self, session: AsyncSession): self.session = session
    async def list(self, project_id: UUID | None = None, active_only: bool = False):
        stmt = select(SitePlan).order_by(SitePlan.created_at.desc())
        if project_id: stmt = stmt.where(SitePlan.project_id == project_id)
        if active_only: stmt = stmt.where(SitePlan.active.is_(True))
        return list((await self.session.scalars(stmt)).all())
    async def get(self, site_plan_id: UUID): return await self.session.get(SitePlan, site_plan_id)
    async def get_by_code(self, site_code: str):
        return await self.session.scalar(select(SitePlan).where(SitePlan.site_code == site_code))
    async def create(self, site_plan: SitePlan):
        self.session.add(site_plan); await self.session.flush(); await self.session.refresh(site_plan); return site_plan
    async def update(self, site_plan: SitePlan, values: dict):
        for key, value in values.items(): setattr(site_plan, key, value)
        await self.session.flush(); await self.session.refresh(site_plan); return site_plan
    async def delete(self, site_plan: SitePlan):
        await self.session.delete(site_plan); await self.session.flush()
    async def summary(self):
        plans = list((await self.session.scalars(select(SitePlan))).all())
        return {"total_plans": len(plans), "active_plans": sum(p.active for p in plans),
                "approved_plans": sum(p.status == "Approved" for p in plans),
                "total_site_area_m2": sum((p.site_area_m2 or 0) for p in plans),
                "total_landscaped_area_m2": sum((p.landscape_area_m2 or 0) for p in plans)}
