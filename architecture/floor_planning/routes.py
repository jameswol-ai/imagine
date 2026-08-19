"""
IMAGINE Architecture
Floor Planning API Routes
"""

from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_session

from .schemas import (
    FloorPlanConstraintResult,
    FloorPlanCreate,
    FloorPlanRead,
    FloorPlanUpdate,
)
from .service import FloorPlanService


router = APIRouter(
    prefix="/floor-planning",
    tags=["Architecture - Floor Planning"],
)


@router.get(
    "",
    response_model=list[FloorPlanRead],
)
async def list_floor_plans(
    project_id: UUID | None = None,
    site_plan_id: UUID | None = None,
    zoning_id: UUID | None = None,
    active_only: bool = False,
    session: AsyncSession = Depends(get_session),
):
    service = FloorPlanService(session)

    return await service.list(
        project_id=project_id,
        site_plan_id=site_plan_id,
        zoning_id=zoning_id,
        active_only=active_only,
    )


@router.get(
    "/{floor_plan_id}",
    response_model=FloorPlanRead,
)
async def get_floor_plan(
    floor_plan_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    service = FloorPlanService(session)

    floor_plan = await service.get(
        floor_plan_id
    )

    if not floor_plan:
        raise HTTPException(
            status_code=404,
            detail="Floor plan not found",
        )

    return floor_plan


@router.get(
    "/{floor_plan_id}/constraints",
    response_model=FloorPlanConstraintResult,
)
async def validate_floor_plan(
    floor_plan_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    service = FloorPlanService(session)

    try:
        return await service.validate_constraints(
            floor_plan_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post(
    "",
    response_model=FloorPlanRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_floor_plan(
    payload: FloorPlanCreate,
    session: AsyncSession = Depends(get_session),
):

    service = FloorPlanService(session)

    try:
        floor_plan = await service.create(
            payload
        )

        await session.commit()

        return floor_plan

    except LookupError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.patch(
    "/{floor_plan_id}",
    response_model=FloorPlanRead,
)
async def update_floor_plan(
    floor_plan_id: UUID,
    payload: FloorPlanUpdate,
    session: AsyncSession = Depends(get_session),
):

    service = FloorPlanService(session)

    try:

        floor_plan = await service.update(
            floor_plan_id,
            payload,
        )

        await session.commit()

        return floor_plan

    except LookupError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.delete(
    "/{floor_plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_floor_plan(
    floor_plan_id: UUID,
    session: AsyncSession = Depends(get_session),
):

    service = FloorPlanService(session)

    try:

        await service.delete(
            floor_plan_id
        )

        await session.commit()

    except LookupError as exc:

        await session.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )