from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ZoningRule


class ZoningRepository:
    @staticmethod
    async def get(db: AsyncSession, zoning_id: UUID) -> Optional[ZoningRule]:
        return await db.get(ZoningRule, zoning_id)

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ZoningRule]:
        stmt = (
            select(ZoningRule)
            .order_by(ZoningRule.name, ZoningRule.code)
            .offset(skip)
            .limit(limit)
        )

        if project_id is not None:
            stmt = stmt.where(ZoningRule.project_id == project_id)

        if status is not None:
            stmt = stmt.where(ZoningRule.status == status)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, zoning: ZoningRule) -> ZoningRule:
        db.add(zoning)
        await db.commit()
        await db.refresh(zoning)
        return zoning

    @staticmethod
    async def update(db: AsyncSession, zoning: ZoningRule) -> ZoningRule:
        await db.commit()
        await db.refresh(zoning)
        return zoning

    @staticmethod
    async def delete(db: AsyncSession, zoning: ZoningRule) -> None:
        await db.delete(zoning)
        await db.commit()
