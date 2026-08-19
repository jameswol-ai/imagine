from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from .models import SitePlan
from .repository import SitePlanRepository
from .schemas import SitePlanCreate, SitePlanUpdate

class SitePlanService:
    def __init__(self, session: AsyncSession):
        self.repo = SitePlanRepository(session)
    async def list(self, project_id: UUID | None = None, active_only: bool = False): return await self.repo.list(project_id, active_only)
    async def get(self, site_plan_id: UUID): return await self.repo.get(site_plan_id)
    async def create(self, payload: SitePlanCreate):
        if await self.repo.get_by_code(payload.site_code): raise ValueError(f"Site plan code already exists: {payload.site_code}")
        values = payload.model_dump(); self._validate_area_allocation(values)
        return await self.repo.create(SitePlan(**values))
    async def update(self, site_plan_id: UUID, payload: SitePlanUpdate):
        obj = await self.repo.get(site_plan_id)
        if not obj: raise LookupError("Site plan not found")
        values = payload.model_dump(exclude_unset=True)
        if "site_code" in values:
            existing = await self.repo.get_by_code(values["site_code"])
            if existing and existing.id != obj.id: raise ValueError(f"Site plan code already exists: {values['site_code']}")
        merged = {k: getattr(obj, k) for k in ("site_area_m2","building_footprint_m2","road_area_m2","parking_area_m2","landscape_area_m2")}
        merged.update(values); self._validate_area_allocation(merged)
        return await self.repo.update(obj, values)
    async def delete(self, site_plan_id: UUID):
        obj = await self.repo.get(site_plan_id)
        if not obj: raise LookupError("Site plan not found")
        await self.repo.delete(obj)
    async def summary(self): return await self.repo.summary()
    @staticmethod
    def _validate_area_allocation(values):
        site = values["site_area_m2"]
        allocated = sum(values.get(k, 0) or 0 for k in ("building_footprint_m2","road_area_m2","parking_area_m2","landscape_area_m2"))
        if allocated > site: raise ValueError("Building, road, parking and landscape areas cannot exceed site area")
