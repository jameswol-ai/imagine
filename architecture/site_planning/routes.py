from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_session
from .schemas import SitePlanCreate, SitePlanRead, SitePlanUpdate, SitePlanSummary
from .service import SitePlanService
router = APIRouter(prefix="/site-planning", tags=["Architecture - Site Planning"])
@router.get("", response_model=list[SitePlanRead])
async def list_site_plans(project_id: UUID | None = None, active_only: bool = False, session: AsyncSession = Depends(get_session)): return await SitePlanService(session).list(project_id, active_only)
@router.get("/summary", response_model=SitePlanSummary)
async def site_plan_summary(session: AsyncSession = Depends(get_session)): return await SitePlanService(session).summary()
@router.get("/{site_plan_id}", response_model=SitePlanRead)
async def get_site_plan(site_plan_id: UUID, session: AsyncSession = Depends(get_session)):
    obj = await SitePlanService(session).get(site_plan_id)
    if not obj: raise HTTPException(404, "Site plan not found")
    return obj
@router.post("", response_model=SitePlanRead, status_code=status.HTTP_201_CREATED)
async def create_site_plan(payload: SitePlanCreate, session: AsyncSession = Depends(get_session)):
    try: obj = await SitePlanService(session).create(payload); await session.commit(); return obj
    except ValueError as exc: await session.rollback(); raise HTTPException(400, str(exc))
@router.patch("/{site_plan_id}", response_model=SitePlanRead)
async def update_site_plan(site_plan_id: UUID, payload: SitePlanUpdate, session: AsyncSession = Depends(get_session)):
    try: obj = await SitePlanService(session).update(site_plan_id, payload); await session.commit(); return obj
    except LookupError as exc: await session.rollback(); raise HTTPException(404, str(exc))
    except ValueError as exc: await session.rollback(); raise HTTPException(400, str(exc))
@router.delete("/{site_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_plan(site_plan_id: UUID, session: AsyncSession = Depends(get_session)):
    try: await SitePlanService(session).delete(site_plan_id); await session.commit()
    except LookupError as exc: await session.rollback(); raise HTTPException(404, str(exc))
