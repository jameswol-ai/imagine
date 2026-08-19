from architecture.site_planning.schemas import SitePlanCreate
def test_site_code_normalized():
    p=SitePlanCreate(name="Test",site_code=" site-01 ",site_area_m2=1000,building_footprint_m2=200,road_area_m2=100,parking_area_m2=100,landscape_area_m2=200,north_orientation_deg=0,slope_percent=5)
    assert p.site_code=="SITE-01"
def test_invalid_area_rejected():
    import pytest
    with pytest.raises(Exception): SitePlanCreate(name="Test",site_code="X",site_area_m2=0,building_footprint_m2=0,road_area_m2=0,parking_area_m2=0,landscape_area_m2=0,north_orientation_deg=0,slope_percent=0)
