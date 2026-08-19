import pytest
from pydantic import ValidationError

from architecture.zoning.models import ZoningUse
from architecture.zoning.schemas import ZoningRuleCreate


def test_zoning_create_accepts_valid_values():
    item = ZoningRuleCreate(
        code="RES-01",
        name="Residential",
        allowed_use=ZoningUse.RESIDENTIAL,
        max_height_m=15,
        site_coverage_pct=50,
        setback_m=3,
        far=1.5,
    )

    assert item.code == "RES-01"
    assert item.site_coverage_pct == 50


@pytest.mark.parametrize( "field,value", [ ("max_height_m", -1), ("site_coverage_pct", 101), ("setback_m", -1), ("far", -1), ], )
def test_zoning_rejects_invalid_numeric_values(field, value):
    values = {
        "code": "RES-01",
        "name": "Residential",
        "allowed_use": ZoningUse.RESIDENTIAL,
        "max_height_m": 15,
        "site_coverage_pct": 50,
        "setback_m": 3,
        "far": 1.5,
    }

    values[field] = value

    with pytest.raises(ValidationError):
        ZoningRuleCreate(**values)
