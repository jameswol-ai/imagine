from __future__ import annotations

from architecture.site_planning.repository import SitePlanRepository, SitePlanningRepository
from architecture.site_planning.service import SitePlanService, SitePlanningService
from architecture.site_planning.ui import render_site_planning


def test_site_planning_public_interfaces_are_compatible():
    assert SitePlanningRepository is SitePlanRepository
    assert SitePlanningService is SitePlanService
    assert callable(render_site_planning)


def test_site_planning_service_accepts_async_session():
    class SessionStub:
        pass

    service = SitePlanningService(SessionStub())
    assert isinstance(service, SitePlanService)
    assert service.repo is not None
