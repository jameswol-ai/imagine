from __future__ import annotations

from architecture.site_planning.repository import (
    SitePlanningRepository,
)
from architecture.site_planning.service import (
    SitePlanningService,
)
from architecture.site_planning.ui import (
    render_site_planning,
)


def test_site_planning_renderer_stack_can_be_constructed():
    repository = SitePlanningRepository()

    service = SitePlanningService(
        repository
    )

    assert repository is not None
    assert service is not None
    assert callable(render_site_planning)