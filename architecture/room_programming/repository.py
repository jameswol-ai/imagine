"""
IMAGINE Architecture
Room Programming Repository
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import RoomProgram


class RoomProgramRepository:

    @staticmethod
    async def get(
        db: AsyncSession,
        room_program_id: UUID,
    ) -> RoomProgram | None:
        return await db.get(
            RoomProgram,
            room_program_id,
        )

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        floor_plan_id: UUID | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RoomProgram]:

        stmt = select(RoomProgram)

        if floor_plan_id:
            stmt = stmt.where(
                RoomProgram.floor_plan_id == floor_plan_id
            )

        if active_only:
            stmt = stmt.where(
                RoomProgram.active.is_(True)
            )

        stmt = (
            stmt.order_by(
                RoomProgram.floor_level,
                RoomProgram.room_code,
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.scalars(stmt)

        return list(result.all())

    @staticmethod
    async def get_by_code(
        db: AsyncSession,
        *,
        floor_plan_id: UUID,
        room_code: str,
    ) -> RoomProgram | None:

        stmt = select(RoomProgram).where(
            RoomProgram.floor_plan_id == floor_plan_id,
            RoomProgram.room_code == room_code,
        )

        return await db.scalar(stmt)

    @staticmethod
    async def create(
        db: AsyncSession,
        room_program: RoomProgram,
    ) -> RoomProgram:

        db.add(room_program)

        await db.flush()
        await db.refresh(room_program)

        return room_program

    @staticmethod
    async def update(
        db: AsyncSession,
        room_program: RoomProgram,
    ) -> RoomProgram:

        await db.flush()
        await db.refresh(room_program)

        return room_program

    @staticmethod
    async def delete(
        db: AsyncSession,
        room_program: RoomProgram,
    ) -> None:

        await db.delete(room_program)

        await db.flush()