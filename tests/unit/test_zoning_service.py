from unittest.mock import AsyncMock

import pytest

from architecture.zoning.models import ZoningUse
from architecture.zoning.schemas import ZoningRuleCreate
from architecture.zoning.service import (
    ZoningNotFoundError,
    ZoningService,
)


@pytest.mark.asyncio
async def test_get_raises_when_rule_does_not_exist(monkeypatch):
    db = AsyncMock()

    async def missing(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "architecture.zoning.service.ZoningRepository.get",
        missing,
    )

    from uuid import uuid4

    with pytest.raises(ZoningNotFoundError):
        await ZoningService.get(db, uuid4())


@pytest.mark.asyncio
async def test_create_constructs_rule_and_delegates(monkeypatch):
    db = AsyncMock()
    captured = {}

    async def create(*args):
        captured["rule"] = args[1]
        return args[1]

    monkeypatch.setattr(
        "architecture.zoning.service.ZoningRepository.create",
        create,
    )

    payload = ZoningRuleCreate(
        code="COM-01",
        name="Commercial",
        allowed_use=ZoningUse.COMMERCIAL,
        max_height_m=30,
        site_coverage_pct=60,
        setback_m=5,
        far=3,
    )

    result = await ZoningService.create(db, payload)

    assert result.code == "COM-01"
    assert captured["rule"].name == "Commercial"
