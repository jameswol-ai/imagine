"""
IMAGINE Projects service layer.

The service supports both the asynchronous API path and the synchronous
Streamlit path. Every ORM operation imports Project through the central
model registry so Approval and Revision relationship targets are registered
before SQLAlchemy mapper configuration.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from projects.model_registry import Project

from .dashboard import aggregate_project_metrics
from .schemas import ProjectCreate, ProjectUpdate


def _project_uuid(value: str | UUID) -> UUID:
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


class ProjectService:
    """Project CRUD service."""

    # ------------------------------------------------------------------
    # Async API methods
    # ------------------------------------------------------------------

    @staticmethod
    async def get(db: AsyncSession, id: str | UUID):
        return await db.get(Project, _project_uuid(id))

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(Project).offset(max(skip, 0)).limit(min(max(limit, 1), 10000))
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: ProjectCreate):
        project = Project(**data.model_dump())
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def update(db: AsyncSession, id: str | UUID, data: ProjectUpdate):
        project = await db.get(Project, _project_uuid(id))
        if not project:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete(db: AsyncSession, id: str | UUID):
        project = await db.get(Project, _project_uuid(id))
        if not project:
            return False

        await db.delete(project)
        await db.commit()
        return True

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession):
        projects = await ProjectService.get_all(db=db, skip=0, limit=10000)
        return aggregate_project_metrics(projects)

    # ------------------------------------------------------------------
    # Sync Streamlit methods
    # ------------------------------------------------------------------

    @staticmethod
    def get_sync(db: Session, id: str | UUID):
        return db.get(Project, _project_uuid(id))

    @staticmethod
    def get_all_sync(db: Session, skip: int = 0, limit: int = 100):
        return (
            db.query(Project)
            .offset(max(skip, 0))
            .limit(min(max(limit, 1), 10000))
            .all()
        )

    @staticmethod
    def create_sync(db: Session, data: ProjectCreate):
        project = Project(**data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_sync(db: Session, id: str | UUID, data: ProjectUpdate):
        project = ProjectService.get_sync(db, id)
        if not project:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_sync(db: Session, id: str | UUID):
        project = ProjectService.get_sync(db, id)
        if not project:
            return False

        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def get_dashboard_metrics_sync(db: Session):
        projects = ProjectService.get_all_sync(db=db, skip=0, limit=10000)
        return aggregate_project_metrics(projects)
