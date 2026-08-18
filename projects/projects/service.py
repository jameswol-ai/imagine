from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.repositories.base import BaseRepository
from .models import Project
from .schemas import ProjectCreate, ProjectUpdate

class ProjectService:
    @staticmethod
    async def get(db: AsyncSession, id: str):
        return await db.get(Project, id)

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Project).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: ProjectCreate):
        project = Project(**data.model_dump())
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def update(db: AsyncSession, id: str, data: ProjectUpdate):
        project = await db.get(Project, id)
        if not project:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete(db: AsyncSession, id: str):
        project = await db.get(Project, id)
        if project:
            await db.delete(project)
            await db.commit()
            return True
        return False