from architecture.site_planning.repository import SitePlanRepository
def test_repository_methods_exist():
    for name in ("list","get","get_by_code","create","update","delete","summary"): assert hasattr(SitePlanRepository,name)
