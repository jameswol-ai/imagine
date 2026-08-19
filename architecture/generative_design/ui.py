"""
IMAGINE
Generative Design Streamlit UI

Streamlit presentation layer for the generative-design engine.

The UI deliberately does not create database sessions directly.
Database access is delegated to GenerativeDesignService and the
repository layer.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any
from uuid import UUID

import streamlit as st

from .constraints import (
    constraint_summary,
    normalize_and_validate_constraints,
)
from .schemas import DesignConstraints
from .service import GenerativeDesignService


# =====================================================================
# ASYNC HELPERS
# =====================================================================

def _run_async(coro: Any) -> Any:
    """
    Execute an async operation from Streamlit.

    Streamlit normally runs synchronously, so the coroutine is executed
    in a dedicated event loop when no loop is already active.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # Streamlit normally reaches this branch only when an event loop
    # already exists. Execute the coroutine in a separate thread so we
    # never attempt to nest asyncio.run().
    import threading

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:
            error["value"] = exc

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )
    thread.start()
    thread.join()

    if "value" in error:
        raise error["value"]

    return result.get("value")


# =====================================================================
# SERVICE ADAPTER
# =====================================================================

def _get_service() -> GenerativeDesignService:
    """
    Obtain the configured generative-design service.

    The service is expected to own repository/database interaction.
    """

    from .repository import GenerativeDesignRepository

    # Import the session factory lazily so merely importing ui.py does
    # not establish a database connection or require database settings.
    from database.connection import AsyncSessionLocal

    repository = GenerativeDesignRepository(
        AsyncSessionLocal
    )

    return GenerativeDesignService(
        repository=repository,
    )


# =====================================================================
# CONSTRAINT INPUT
# =====================================================================

def _default_constraints() -> dict[str, Any]:
    """Return a safe initial constraint document."""

    return {
        "project_id": None,
        "site": {
            "width": 30.0,
            "depth": 40.0,
            "north_access": True,
            "setback_front": 3.0,
            "setback_rear": 3.0,
            "setback_left": 2.0,
            "setback_right": 2.0,
        },
        "zoning": {
            "max_site_coverage": 0.60,
            "max_far": 2.0,
            "max_height": 15.0,
            "max_storeys": 3,
        },
        "program": {
            "rooms": [
                {
                    "name": "Living Room",
                    "area": 30.0,
                    "quantity": 1,
                    "required": True,
                },
                {
                    "name": "Bedroom",
                    "area": 16.0,
                    "quantity": 3,
                    "required": True,
                },
                {
                    "name": "Kitchen",
                    "area": 15.0,
                    "quantity": 1,
                    "required": True,
                },
            ],
            "circulation_ratio": 0.15,
        },
        "compliance": {
            "minimum_egress_width": 1.1,
            "accessibility_required": True,
            "fire_separation_required": True,
        },
        "metadata": {},
    }


def _constraints_editor() -> dict[str, Any]:
    """Render the basic constraint editor."""

    defaults = _default_constraints()

    st.subheader("Design Constraints")

    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input(
            "Site width (m)",
            min_value=1.0,
            value=float(defaults["site"]["width"]),
            step=1.0,
        )

        depth = st.number_input(
            "Site depth (m)",
            min_value=1.0,
            value=float(defaults["site"]["depth"]),
            step=1.0,
        )

        front = st.number_input(
            "Front setback (m)",
            min_value=0.0,
            value=float(
                defaults["site"]["setback_front"]
            ),
            step=0.5,
        )

        rear = st.number_input(
            "Rear setback (m)",
            min_value=0.0,
            value=float(
                defaults["site"]["setback_rear"]
            ),
            step=0.5,
        )

    with col2:
        left = st.number_input(
            "Left setback (m)",
            min_value=0.0,
            value=float(
                defaults["site"]["setback_left"]
            ),
            step=0.5,
        )

        right = st.number_input(
            "Right setback (m)",
            min_value=0.0,
            value=float(
                defaults["site"]["setback_right"]
            ),
            step=0.5,
        )

        max_storeys = st.number_input(
            "Maximum storeys",
            min_value=1,
            value=int(
                defaults["zoning"]["max_storeys"]
            ),
            step=1,
        )

        max_coverage = st.number_input(
            "Maximum site coverage",
            min_value=0.01,
            max_value=1.0,
            value=float(
                defaults["zoning"]["max_site_coverage"]
            ),
            step=0.05,
        )

    north_access = st.checkbox(
        "North access",
        value=bool(
            defaults["site"]["north_access"]
        ),
    )

    circulation = st.slider(
        "Circulation ratio",
        min_value=0.0,
        max_value=1.0,
        value=float(
            defaults["program"]["circulation_ratio"]
        ),
        step=0.05,
    )

    rooms = st.session_state.get(
        "generative_design_rooms",
        defaults["program"]["rooms"],
    )

    st.markdown("#### Room Program")

    room_count = st.number_input(
        "Number of room types",
        min_value=0,
        max_value=50,
        value=len(rooms),
        step=1,
        key="gd_room_count",
    )

    updated_rooms: list[dict[str, Any]] = []

    for index in range(int(room_count)):
        existing = (
            rooms[index]
            if index < len(rooms)
            else {
                "name": "",
                "area": 10.0,
                "quantity": 1,
                "required": True,
            }
        )

        room_col1, room_col2, room_col3 = st.columns(
            [2, 1, 1]
        )

        with room_col1:
            name = st.text_input(
                f"Room {index + 1}",
                value=str(
                    existing.get("name", "")
                ),
                key=f"gd_room_name_{index}",
            )

        with room_col2:
            area = st.number_input(
                "Area",
                min_value=0.1,
                value=float(
                    existing.get("area", 10.0)
                ),
                step=1.0,
                key=f"gd_room_area_{index}",
            )

        with room_col3:
            quantity = st.number_input(
                "Qty",
                min_value=1,
                value=int(
                    existing.get("quantity", 1)
                ),
                step=1,
                key=f"gd_room_qty_{index}",
            )

        updated_rooms.append(
            {
                "name": name,
                "area": area,
                "quantity": quantity,
                "required": bool(
                    existing.get(
                        "required",
                        True,
                    )
                ),
            }
        )

    st.session_state[
        "generative_design_rooms"
    ] = updated_rooms

    return {
        "project_id": None,
        "site": {
            "width": width,
            "depth": depth,
            "north_access": north_access,
            "setback_front": front,
            "setback_rear": rear,
            "setback_left": left,
            "setback_right": right,
        },
        "zoning": {
            "max_site_coverage": max_coverage,
            "max_far": defaults["zoning"]["max_far"],
            "max_height": defaults["zoning"]["max_height"],
            "max_storeys": int(max_storeys),
        },
        "program": {
            "rooms": updated_rooms,
            "circulation_ratio": circulation,
        },
        "compliance": defaults["compliance"],
        "metadata": {},
    }


# =====================================================================
# SUMMARY
# =====================================================================

def _render_constraint_summary(
    constraints: DesignConstraints,
) -> None:
    """Display normalized constraint information."""

    summary = constraint_summary(
        constraints
    )

    site = summary["site"]
    zoning = summary["zoning"]
    program = summary["program"]

    st.subheader("Constraint Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Site Area",
            f"{site['gross_area']:.1f} m²",
        )

    with col2:
        st.metric(
            "Buildable Area",
            f"{site['buildable_area']:.1f} m²",
        )

    with col3:
        st.metric(
            "Required GFA",
            f"{program['required_gross_area']:.1f} m²",
        )

    with col4:
        st.metric(
            "Max Storeys",
            zoning["max_storeys"],
        )


# =====================================================================
# CANDIDATE DISPLAY
# =====================================================================

def _candidate_value(
    candidate: Any,
    field: str,
    default: Any = None,
) -> Any:
    """Read a candidate field from either an object or mapping."""

    if isinstance(candidate, Mapping):
        return candidate.get(
            field,
            default,
        )

    return getattr(
        candidate,
        field,
        default,
    )


def _render_candidate(
    candidate: Any,
    index: int,
) -> None:
    """Render one generated candidate."""

    name = _candidate_value(
        candidate,
        "name",
        f"Candidate {index + 1}",
    )

    score = _candidate_value(
        candidate,
        "score",
        0.0,
    )

    rank = _candidate_value(
        candidate,
        "rank",
        None,
    )

    status = _candidate_value(
        candidate,
        "status",
        "generated",
    )

    geometry = _candidate_value(
        candidate,
        "geometry",
        {},
    )

    metrics = _candidate_value(
        candidate,
        "metrics",
        {},
    )

    evaluation = _candidate_value(
        candidate,
        "evaluation",
        {},
    )

    title = (
        f"#{rank} {name}"
        if rank is not None
        else name
    )

    with st.expander(
        title,
        expanded=index == 0,
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Score",
                f"{float(score):.3f}",
            )

        with col2:
            st.metric(
                "Status",
                str(status),
            )

        with col3:
            st.metric(
                "Rank",
                rank if rank is not None else "N/A",
            )

        st.markdown("**Geometry**")
        st.json(geometry)

        st.markdown("**Metrics**")
        st.json(metrics)

        if evaluation:
            st.markdown("**Evaluation**")
            st.json(evaluation)


# =====================================================================
# MAIN RENDERER
# =====================================================================

def render_generative_design() -> None:
    """
    Render the complete Generative Design module.

    This function intentionally remains the public entry point expected
    by streamlit_app.py and the module registry.
    """

    st.title("Generative Design")
    st.caption(
        "Constraint-driven architectural option generation."
    )

    if "generative_design_last_run" not in st.session_state:
        st.session_state[
            "generative_design_last_run"
        ] = None

    if "generative_design_candidates" not in st.session_state:
        st.session_state[
            "generative_design_candidates"
        ] = []

    constraints_payload = _constraints_editor()

    normalized, validation = (
        normalize_and_validate_constraints(
            constraints_payload
        )
    )

    if validation.errors:
        st.error("Constraint validation failed.")

        for error in validation.errors:
            st.write(f"• {error}")

        if validation.warnings:
            with st.expander("Warnings"):
                for warning in validation.warnings:
                    st.write(f"• {warning}")

        return

    if normalized is None:
        st.error(
            "Unable to normalize the design constraints."
        )
        return

    _render_constraint_summary(
        normalized
    )

    if validation.warnings:
        with st.expander(
            f"Warnings ({len(validation.warnings)})"
        ):
            for warning in validation.warnings:
                st.warning(warning)

    st.divider()

    candidate_count = st.slider(
        "Candidates to generate",
        min_value=1,
        max_value=100,
        value=5,
        key="gd_candidate_count",
    )

    run_name = st.text_input(
        "Run name",
        value="Generative Design Run",
        key="gd_run_name",
    )

    generate = st.button(
        "Generate Designs",
        type="primary",
        use_container_width=True,
        key="gd_generate",
    )

    if generate:
        service = _get_service()

        with st.status(
            "Generating design candidates...",
            expanded=True,
        ) as status:

            try:
                result = _run_async(
                    service.generate(
                        constraints=normalized,
                        name=run_name,
                        candidate_count=candidate_count,
                    )
                )

                st.session_state[
                    "generative_design_last_run"
                ] = result

                candidates = _candidate_value(
                    result,
                    "candidates",
                    [],
                )

                st.session_state[
                    "generative_design_candidates"
                ] = list(candidates)

                status.update(
                    label="Generation completed",
                    state="complete",
                )

            except Exception as exc:
                status.update(
                    label="Generation failed",
                    state="error",
                )

                st.error(
                    f"Generative design failed: {exc}"
                )

    candidates = st.session_state[
        "generative_design_candidates"
    ]

    if not candidates:
        st.info(
            "No generated candidates yet. "
            "Set the constraints and generate a design set."
        )
        return

    st.divider()
    st.subheader(
        f"Generated Candidates ({len(candidates)})"
    )

    for index, candidate in enumerate(
        candidates
    ):
        _render_candidate(
            candidate,
            index,
        )


__all__ = [
    "render_generative_design",
]