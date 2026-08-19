import pytest
from architecture.site_planning.service import SitePlanService
def test_area_allocation_guard():
    with pytest.raises(ValueError): SitePlanService._validate_area_allocation({"site_area_m2":100,"building_footprint_m2":80,"road_area_m2":30,"parking_area_m2":0,"landscape_area_m2":0})
def test_area_allocation_valid():
    SitePlanService._validate_area_allocation({"site_area_m2":100,"building_footprint_m2":40,"road_area_m2":20,"parking_area_m2":10,"landscape_area_m2":20})
