from modules.structural.ec4 import CompositeBeamInput, design_composite_beam
from modules.structural.ec6 import MasonryWallInput, screen_masonry_wall
from modules.structural.section_shapes import CircularSection, RectangularSection


def test_composite_beam_screening():
    result = design_composite_beam(CompositeBeamInput(6000, 355, 180000, 30, 2500, 0, 180, moment_demand_kn_m=100))
    assert result.simplified_moment_capacity_kn_m > 0
    assert result.interaction_utilisation >= 0


def test_masonry_wall_screening():
    result = screen_masonry_wall(MasonryWallInput(200, 3, 4, 7.5, axial_demand_kn=100, eccentricity_mm=10))
    assert result.capacity_kn > 0
    assert result.status in {"PASS", "REVIEW"}


def test_section_properties():
    rect = RectangularSection(300, 500)
    circ = CircularSection(400)
    assert rect.area_mm2 == 150000
    assert rect.ix_mm4 > rect.iy_mm4
    assert circ.area_mm2 > 0
    assert circ.z_mm3 > 0
