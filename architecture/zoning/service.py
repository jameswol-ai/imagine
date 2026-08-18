from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ZoningRule
from .repository import ZoningRepository
from .schemas import ZoningRuleCreate, ZoningRuleUpdate


class ZoningNotFoundError(LookupError):
    """Raised when a zoning rule does not exist."""


class ZoningConflictError(ValueError):
    """Raised when a zoning rule violates a uniqueness constraint."""


class ZoningService:
    @staticmethod
    async def get(db: AsyncSession, zoning_id: UUID) -> ZoningRule:
        zoning = await ZoningRepository.get(db, zoning_id)

        if zoning is None:
            raise ZoningNotFoundError(
                f"Zoning rule {zoning_id} not found."
            )

        return zoning

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ZoningRule]:
        if skip < 0:
            raise ValueError("skip must be >= 0.")

        if limit < 1 or limit > 500:
            raise ValueError("limit must be between 1 and 500.")

        return await ZoningRepository.list(
            db,
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def create(
        db: AsyncSession,
        data: ZoningRuleCreate,
    ) -> ZoningRule:
        zoning = ZoningRule(**data.model_dump())

        try:
            return await ZoningRepository.create(db, zoning)
        except IntegrityError as exc:
            await db.rollback()
            raise ZoningConflictError(
                f"Zoning code '{data.code}' already exists for this project."
            ) from exc

    @staticmethod
    async def update(
        db: AsyncSession,
        zoning_id: UUID,
        data: ZoningRuleUpdate,
    ) -> ZoningRule:
        zoning = await ZoningService.get(db, zoning_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(zoning, key, value)

        try:
            return await ZoningRepository.update(db, zoning)
        except IntegrityError as exc:
            await db.rollback()
            raise ZoningConflictError(
                f"Zoning code '{data.code}' already exists for this project."
            ) from exc

    @staticmethod
    async def delete(
        db: AsyncSession,
        zoning_id: UUID,
    ) -> None:
        zoning = await ZoningService.get(db, zoning_id)
        await ZoningRepository.delete(db, zoning)
