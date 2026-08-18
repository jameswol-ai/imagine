from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from .service import ProjectService
from database.connection import get_db
from core.authorization.dependencies import require_permission

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("view_project")),
):
    return await ProjectService.get_all(db, skip, limit)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("view_project")),
):
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("create_project")),
):
    return await ProjectService.create(db, data)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("edit_project")),
):
    project = await ProjectService.update(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("delete_project")),
):
    deleted = await ProjectService.delete(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return