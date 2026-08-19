"""
IMAGINE
Generative Design UI
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from .constraints import (
    calculate_buildable_site,
    calculate_required_gross_area,
    validate_constraints,
)
from .generator import generate_candidates
from .schemas import (
    ComplianceConstraints,
    DesignConstraints,
    ProgramConstraints,
    RoomRequirement,
    SiteConstraints,
    ZoningConstraints,
)
from .scoring import score_and_rank


def _default_constraints() -> DesignConstraints:
    return DesignConstraints(
        site=SiteConstraints(
            width=30,
            depth=40,
            north_access=True,
            setback_front=5,
            setback_rear=3,
            setback_left=3,
            setback_right=3,
        ),
        zoning=ZoningConstraints(
            max_site_coverage=0.60,
            max_far=2.0,
            max_height=15,
            max_storeys=3,
        ),
        program=ProgramConstraints(
            rooms=[
                RoomRequirement(
                    name="Living Room",
                    area=30,
                ),
                RoomRequirement(
                    name="Kitchen",
                    area=18,
                ),
                RoomRequirement(
                    name="Bedroom",
                    area=16,
                    quantity=3,
                ),
                RoomRequirement(
                    name="Bathroom",
                    area=6,
                    quantity=3,
                ),
            ]
        ),
        compliance=ComplianceConstraints(),
    )


def render_generative_design() -> None:
    """Render the Streamlit generative-design workspace."""

    st.title("Generative Design")

    st.caption(
        "Constraint-driven architectural option generation."
    )

    defaults = _default_constraints()

    with st.expander(
        "Site & Zoning Constraints",
        expanded=True,
    ):
        col1, col2 = st.columns(2)

        with col1:
            site_width = st.number_input(
                "Site Width",
                min_value=1.0,
                value=float(
                    defaults.site.width
                ),
            )

            site_depth = st.number_input(
                "Site Depth",
                min_value=1.0,
                value=float(
                    defaults.site.depth
                ),
            )

            front_setback = st.number_input(
                "Front Setback",
                min_value=0.0,
                value=float(
                    defaults.site.setback_front
                ),
            )

        with col2:
            max_coverage = st.slider(
                "Maximum Site Coverage",
                min_value=0.1,
                max_value=1.0,
                value=defaults.zoning.max_site_coverage,
            )

            max_storeys = st.number_input(
                "Maximum Storeys",
                min_value=1,
                max_value=100,
                value=defaults.zoning.max_storeys,
            )

            max_far = st.number_input(
                "Maximum FAR",
                min_value=0.1,
                value=defaults.zoning.max_far,
            )

    with st.expander(
        "Room Program",
        expanded=True,
    ):
        room_count = st.number_input(
            "Number of Room Types",
            min_value=1,
            max_value=30,
            value=4,
        )

        rooms: list[RoomRequirement] = []

        for index in range(
            int(room_count)
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                name = st.text_input(
                    f"Room {index + 1}",
                    value=(
                        defaults.program.rooms[index].name
                        if index
                        < len(
                            defaults.program.rooms
                        )
                        else f"Room {index + 1}"
                    ),
                    key=f"gd_room_name_{index}",
                )

            with col2:
                area = st.number_input(
                    f"Area {index + 1}",
                    min_value=1.0,
                    value=float(
                        defaults.program.rooms[index].area
                        if index
                        < len(
                            defaults.program.rooms
                        )
                        else 10
                    ),
                    key=f"gd_room_area_{index}",
                )

            with col3:
                quantity = st.number_input(
                    f"Quantity {index + 1}",
                    min_value=1,
                    value=1,
                    key=f"gd_room_quantity_{index}",
                )

            rooms.append(
                RoomRequirement(
                    name=name,
                    area=area,
                    quantity=quantity,
                )
            )

    candidate_count = st.slider(
        "Number of Design Options",
        min_value=1,
        max_value=20,
        value=5,
    )

    if st.button(
        "Generate Design Options",
        type="primary",
        use_container_width=True,
    ):
        constraints = DesignConstraints(
            site=SiteConstraints(
                width=site_width,
                depth=site_depth,
                north_access=True,
                setback_front=front_setback,
                setback_rear=defaults.site.setback_rear,
                setback_left=defaults.site.setback_left,
                setback_right=defaults.site.setback_right,
            ),
            zoning=ZoningConstraints(
                max_site_coverage=max_coverage,
                max_far=max_far,
                max_height=defaults.zoning.max_height,
                max_storeys=int(max_storeys),
            ),
            program=ProgramConstraints(
                rooms=rooms,
                circulation_ratio=defaults.program.circulation_ratio,
            ),
            compliance=defaults.compliance,
        )

        validation = validate_constraints(
            constraints
        )

        if not validation.valid:
            for error in validation.errors:
                st.error(error)

            return

        for warning in validation.warnings:
            st.warning(warning)

        buildable = calculate_buildable_site(
            constraints
        )

        required_area = (
            calculate_required_gross_area(
                constraints
            )
        )

        st.subheader("Design Envelope")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Buildable Area",
            f"{buildable.area:,.1f} m²",
        )

        col2.metric(
            "Required Gross Area",
            f"{required_area:,.1f} m²",
        )

        col3.metric(
            "Maximum Storeys",
            int(max_storeys),
        )

        candidates = generate_candidates(
            constraints,
            int(candidate_count),
        )

        ranked = score_and_rank(
            candidates,
            constraints,
        )

        st.subheader("Generated Options")

        for candidate in ranked:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Rank",
                    candidate.rank,
                )

                col2.metric(
                    "Score",
                    f"{candidate.score:.1f}",
                )

                col3.metric(
                    "Storeys",
                    candidate.metrics["storeys"],
                )

                st.write(
                    f"**{candidate.name}**"
                )

                st.json(
                    {
                        "geometry": candidate.geometry,
                        "metrics": candidate.metrics,
                        "evaluation": candidate.evaluation,
                    }
                )