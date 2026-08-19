"""
IMAGINE Architecture
Room Programming API Routes
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db

from .schemas import (
    RoomProgramConstraintResult,
    RoomProgramCreate,
    RoomProgramRead,
    RoomProgramSummary,
    RoomProgramUpdate,
)
from .service import (
    RoomProgramConflictError,
    RoomProgramConstraintError,
    RoomProgramNotFoundError,
    RoomProgramService,
)

router = APIRouter(
    prefix="/room-programming",
    tags=["architecture-room-programming"],
)


@router.get(
    "/",
    response_model=list[RoomProgramRead],
)
async def list_room_programs(
    floor_plan_id: Optional[UUID] = None,
    active_only: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: AsyncSession = Depends(get_db),
):
    return await RoomProgramService.list(
        db,
        floor_plan_id=floor_plan_id,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/summary/{floor_plan_id}",
    response_model=RoomProgramSummary,
)
async def room_program_summary(
    floor_plan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await RoomProgramService.summary(
            db,
            floor_plan_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{room_program_id}",
    response_model=RoomProgramRead,
)
async def get_room_program(
    room_program_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await RoomProgramService.get(
            db,
            room_program_id,
        )
    except RoomProgramNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{room_program_id}/validate",
    response_model=RoomProgramConstraintResult,
)
async def validate_room_program(
    room_program_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await RoomProgramService.validate(
            db,
            room_program_id,
        )
    except RoomProgramNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/",
    response_model=RoomProgramRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_room_program(
    data: RoomProgramCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await RoomProgramService.create(
            db,
            data,
        )

    except RoomProgramConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except RoomProgramConstraintError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.put(
    "/{room_program_id}",
    response_model=RoomProgramRead,
)
async def update_room_program(
    room_program_id: UUID,
    data: RoomProgramUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await RoomProgramService.update(
            db,
            room_program_id,
            data,
        )

    except RoomProgramNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RoomProgramConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except RoomProgramConstraintError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{room_program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room_program(
    room_program_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await RoomProgramService.delete(
            db,
            room_program_id,
        )
    except RoomProgramNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc