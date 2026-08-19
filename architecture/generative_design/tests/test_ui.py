"""
Tests for the generative design UI.

The UI test intentionally focuses on importability and
key structural functions. Full browser-level interaction
belongs in a higher-level integration test suite.
"""

from architecture.generative_design.ui import (
    _default_constraints,
)


def test_ui_defaults_are_valid():
    constraints = _default_constraints()

    assert constraints.site.width > 0
    assert constraints.site.depth > 0
    assert constraints.zoning.max_storeys >= 1
    assert len(constraints.program.rooms) > 0


def test_ui_defaults_have_room_requirements():
    constraints = _default_constraints()

    for room in constraints.program.rooms:
        assert room.name
        assert room.area > 0
        assert room.quantity >= 1