from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db

from .models import ZoningStatus
from .schemas import (
    ZoningRuleCreate,
    ZoningRuleResponse,
    ZoningRuleUpdate,
)
from .service import (
    ZoningConflictError,
    ZoningNotFoundError,
    ZoningService,
)


router = APIRouter(
    prefix="/zoning",
    tags=["architecture-zoning"],
)


@router.get("/", response_model=list[ZoningRuleResponse])
async def list_zoning(
    project_id: Optional[UUID] = None,
    zoning_status: Optional[ZoningStatus] = Query(
        default=None,
        alias="status",
    ),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await ZoningService.list(
        db,
        project_id=project_id,
        status=zoning_status.value if zoning_status else None,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{zoning_id}",
    response_model=ZoningRuleResponse,
)
async def get_zoning(
    zoning_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ZoningService.get(db, zoning_id)
    except ZoningNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/",
    response_model=ZoningRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_zoning(
    data: ZoningRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ZoningService.create(db, data)
    except ZoningConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.put(
    "/{zoning_id}",
    response_model=ZoningRuleResponse,
)
async def update_zoning(
    zoning_id: UUID,
    data: ZoningRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ZoningService.update(db, zoning_id, data)
    except ZoningNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ZoningConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{zoning_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_zoning(
    zoning_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await ZoningService.delete(db, zoning_id)
    except ZoningNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
