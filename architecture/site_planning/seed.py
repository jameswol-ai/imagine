from decimal import Decimal
from .models import SitePlan
SEED_SITE_PLANS = [
    dict(name="Green Tower Site", site_code="SITE-GT-001", status="Approved", site_area_m2=Decimal("5000"), building_footprint_m2=Decimal("2100"), road_area_m2=Decimal("800"), parking_area_m2=Decimal("700"), landscape_area_m2=Decimal("1400"), north_orientation_deg=Decimal("15"), slope_percent=Decimal("4.5"), soil_type="Clay", drainage_strategy="Permeable paving and stormwater attenuation", access_strategy="Primary east access with service entrance"),
    dict(name="Harbor Bridge Compound", site_code="SITE-HB-001", status="Proposed", site_area_m2=Decimal("8200"), building_footprint_m2=Decimal("3000"), road_area_m2=Decimal("1800"), parking_area_m2=Decimal("1200"), landscape_area_m2=Decimal("2200"), north_orientation_deg=Decimal("0"), slope_percent=Decimal("2"), soil_type="Sand"),
]
async def seed_site_plans(session):
    from sqlalchemy import select
    if await session.scalar(select(SitePlan.id).limit(1)): return 0
    for data in SEED_SITE_PLANS: session.add(SitePlan(**data))
    await session.flush(); return len(SEED_SITE_PLANS)
