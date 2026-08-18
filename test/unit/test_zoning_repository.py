from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from architecture.zoning.repository import ZoningRepository


@pytest.mark.asyncio
async def test_get_uses_session_get():
    db = AsyncMock()
    expected = object()
    db.get.return_value = expected

    result = await ZoningRepository.get(
        db,
        uuid4(),
    )

    assert result is expected
    db.get.assert_awaited_once()
