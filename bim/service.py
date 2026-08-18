from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Type, Dict, Any
from .models import (
    GenerativeDesign, Zoning, SitePlan, FloorPlan, RoomProgram, ComplianceCheck
)
from .schemas import (
    GenerativeDesignCreate, GenerativeDesignUpdate,
    ZoningCreate, ZoningUpdate,
    SitePlanCreate, SitePlanUpdate,
    FloorPlanCreate, FloorPlanUpdate,
    RoomProgramCreate, RoomProgramUpdate,
    ComplianceCheckCreate, ComplianceCheckUpdate
)

class ArchitectureService:
    @staticmethod
    async def generic_get(db: AsyncSession, model, id: str):
        return await db.get(model, id)

    @staticmethod
    async def generic_get_all(db: AsyncSession, model, skip: int = 0, limit: int = 100):
        result = await db.execute(select(model).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def generic_create(db: AsyncSession, model, data):
        instance = model(**data.model_dump())
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def generic_update(db: AsyncSession, model, id: str, data):
        instance = await db.get(model, id)
        if not instance:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def generic_delete(db: AsyncSession, model, id: str):
        instance = await db.get(model, id)
        if instance:
            await db.delete(instance)
            await db.commit()
            return True
        return False

    # Convenience methods for each type
    @classmethod
    async def get_generative_design(cls, db, id): return await cls.generic_get(db, GenerativeDesign, id)
    @classmethod
    async def get_all_generative_designs(cls, db, **kwargs): return await cls.generic_get_all(db, GenerativeDesign, **kwargs)
    @classmethod
    async def create_generative_design(cls, db, data): return await cls.generic_create(db, GenerativeDesign, data)
    @classmethod
    async def update_generative_design(cls, db, id, data): return await cls.generic_update(db, GenerativeDesign, id, data)
    @classmethod
    async def delete_generative_design(cls, db, id): return await cls.generic_delete(db, GenerativeDesign, id)

    # Similarly for Zoning, SitePlan, FloorPlan, RoomProgram, ComplianceCheck
    # (I'll omit repetitive code for brevity, but you'd add them)