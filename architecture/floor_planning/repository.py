"""
IMAGINE Architecture
Floor Planning Repository
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import FloorPlan


class FloorPlanRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        project_id: UUID | None = None,
        site_plan_id: UUID | None = None,
        zoning_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[FloorPlan]:

        stmt = select(FloorPlan).order_by(
            FloorPlan.created_at.desc()
        )

        if project_id:
            stmt = stmt.where(
                FloorPlan.project_id == project_id
            )

        if site_plan_id:
            stmt = stmt.where(
                FloorPlan.site_plan_id == site_plan_id
            )

        if zoning_id:
            stmt = stmt.where(
                FloorPlan.zoning_id == zoning_id
            )

        if active_only:
            stmt = stmt.where(
                FloorPlan.active.is_(True)
            )

        result = await self.session.scalars(stmt)

        return list(result.all())

    async def get(
        self,
        floor_plan_id: UUID,
    ) -> FloorPlan | None:

        return await self.session.get(
            FloorPlan,
            floor_plan_id,
        )

    async def get_by_code(
        self,
        plan_code: str,
    ) -> FloorPlan | None:

        stmt = select(FloorPlan).where(
            FloorPlan.plan_code == plan_code
        )

        return await self.session.scalar(stmt)

    async def create(
        self,
        floor_plan: FloorPlan,
    ) -> FloorPlan:

        self.session.add(floor_plan)

        await self.session.flush()
        await self.session.refresh(floor_plan)

        return floor_plan

    async def update(
        self,
        floor_plan: FloorPlan,
        values: dict,
    ) -> FloorPlan:

        for key, value in values.items():
            setattr(
                floor_plan,
                key,
                value,
            )

        await self.session.flush()
        await self.session.refresh(floor_plan)

        return floor_plan

    async def delete(
        self,
        floor_plan: FloorPlan,
    ) -> None:

        await self.session.delete(floor_plan)
        await self.session.flush()