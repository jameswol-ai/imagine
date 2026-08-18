from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ZoningRule, ZoningStatus, ZoningUse


DEFAULT_ZONING_RULES = (
    {
        "code": "RES-01",
        "name": "Residential",
        "description": "Default residential development controls.",
        "allowed_use": ZoningUse.RESIDENTIAL,
        "status": ZoningStatus.ACTIVE,
        "max_height_m": 15.0,
        "site_coverage_pct": 50.0,
        "setback_m": 3.0,
        "far": 1.5,
    },
    {
        "code": "COM-01",
        "name": "Commercial",
        "description": "Default commercial development controls.",
        "allowed_use": ZoningUse.COMMERCIAL,
        "status": ZoningStatus.ACTIVE,
        "max_height_m": 30.0,
        "site_coverage_pct": 60.0,
        "setback_m": 5.0,
        "far": 3.0,
    },
    {
        "code": "MIX-01",
        "name": "Mixed Use",
        "description": "Default mixed-use development controls.",
        "allowed_use": ZoningUse.MIXED_USE,
        "status": ZoningStatus.ACTIVE,
        "max_height_m": 45.0,
        "site_coverage_pct": 70.0,
        "setback_m": 4.0,
        "far": 4.0,
    },
)


async def seed_zoning(db: AsyncSession) -> int:
    created = 0

    for values in DEFAULT_ZONING_RULES:
        result = await db.execute(
            select(ZoningRule).where(
                ZoningRule.project_id.is_(None),
                ZoningRule.code == values["code"],
            )
        )

        if result.scalar_one_or_none() is not None:
            continue

        db.add(
            ZoningRule(
                project_id=None,
                **values,
            )
        )
        created += 1

    if created:
        await db.commit()

    return created
