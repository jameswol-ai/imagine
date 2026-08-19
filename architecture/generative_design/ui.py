"""
IMAGINE
Generative Design Streamlit UI

Streamlit presentation layer for the Generative Design module.

Architecture:

    Streamlit UI
        ↓
    GenerativeDesignService
        ↓
    GenerativeDesignRepository
        ↓
    Async SQLAlchemy session

The UI deliberately does not import AsyncSessionLocal at module
import time. Database access is created lazily when an operation
actually requires persistence.
"""

from __future__ import annotations

import asyncio
import inspect
import threading
from collections.abc import Mapping
from typing import Any
from uuid import UUID

import streamlit as st

from .constraints import (
    constraint_summary,
    normalize_and_validate_constraints,
)
from .generator import DesignCandidate
from .schemas import (
    DesignConstraints,
    GenerativeDesignRunResponse,
)
from .service import GenerativeDesignService


# =====================================================================
# CONSTANTS
# =====================================================================

DEFAULT_CANDIDATE_COUNT = 5

STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

SESSION_CONSTRAINTS = (
    "generative_design_constraints",
)

SESSION_RESULT = (
    "generative_design_result",
)

SESSION_SELECTED_CANDIDATE = (
    "generative_design_selected_candidate",
)


# =====================================================================
# ASYNC EXECUTION
# =====================================================================

def _run_async(
    coroutine: Any,
) -> Any:
    """
    Execute an awaitable from Streamlit.

    Streamlit normally runs synchronously, while the service layer
    uses AsyncSession and async repository operations.

    If no event loop is running, asyncio.run() is used directly.

    If an event loop is already running, the coroutine is executed
    in a dedicated thread with its own event loop.
    """

    if not inspect.isawaitable(coroutine):
        return coroutine

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    result: list[Any] = []
    errors: list[BaseException] = []

    def runner() -> None:
        try:
            result.append(
                asyncio.run(coroutine)
            )
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()
    thread.join()

    if errors:
        raise errors[0]

    return (
        result[0]
        if result
        else None
    )


# =====================================================================
# DATABASE / SERVICE BOUNDARY
# =====================================================================

async def _generate_with_service(
    constraints: DesignConstraints,
    candidate_count: int,
) -> Any:
    """
    Execute generation through the service layer.

    AsyncSessionLocal is intentionally imported here rather than at
    module import time.
    """

    from database.connection import (
        AsyncSessionLocal,
    )

    async with AsyncSessionLocal() as session:

        service = (
            GenerativeDesignService(
                session=session,
            )
        )

        return await service.generate(
            constraints=constraints,
            candidate_count=candidate_count,
        )


async def _service_operation(
    operation: str,
    **kwargs: Any,
) -> Any:
    """
    Execute a service operation using one async database session.

    This helper keeps database access out of the Streamlit rendering
    layer.
    """

    from database.connection import (
        AsyncSessionLocal,
    )

    async with AsyncSessionLocal() as session:

        service = (
            GenerativeDesignService(
                session=session,
            )
        )

        method = getattr(
            service,
            operation,
        )

        result = method(
            **kwargs
        )

        if inspect.isawaitable(result):
            return await result

        return result


# =====================================================================
# SAFE DISPLAY HELPERS
# =====================================================================

def _as_dict(
    value: Any,
) -> dict[str, Any]:
    """Convert common model objects to dictionaries."""

    if value is None:
        return {}

    if isinstance(
        value,
        Mapping,
    ):
        return dict(value)

    if hasattr(
        value,
        "model_dump",
    ):
        return value.model_dump(
            mode="python"
        )

    if hasattr(
        value,
        "__dict__",
    ):
        return {
            key: value
            for key, value in value.__dict__.items()
            if not key.startswith("_")
        }

    return {}


def _candidate_value(
    candidate: Any,
    field: str,
    default: Any = None,
) -> Any:
    """Read a candidate field from a dataclass, model, or mapping."""

    if isinstance(
        candidate,
        Mapping,
    ):
        return candidate.get(
            field,
            default,
        )

    return getattr(
        candidate,
        field,
        default,
    )


def _candidate_id(
    candidate: Any,
) -> UUID | None:
    """Return a candidate UUID when persisted."""

    value = _candidate_value(
        candidate,
        "id",
    )

    if value is None:
        return None

    if isinstance(
        value,
        UUID,
    ):
        return value

    try:
        return UUID(
            str(value)
        )
    except (
        TypeError,
        ValueError,
    ):
        return None


def _candidate_name(
    candidate: Any,
) -> str:
    return str(
        _candidate_value(
            candidate,
            "name",
            "Unnamed Candidate",
        )
    )


def _candidate_score(
    candidate: Any,
) -> float:
    value = _candidate_value(
        candidate,
        "score",
        0.0,
    )

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _candidate_rank(
    candidate: Any,
) -> int | None:
    value = _candidate_value(
        candidate,
        "rank",
    )

    if value is None:
        return None

    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def _candidate_status(
    candidate: Any,
) -> str:
    return str(
        _candidate_value(
            candidate,
            "status",
            "generated",
        )
    )


# =====================================================================
# RESULT EXTRACTION
# =====================================================================

def _extract_candidates(
    result: Any,
) -> list[Any]:
    """
    Extract candidates from common service result shapes.

    Supports:

    - list[DesignCandidate]
    - GenerativeDesignRunResponse
    - objects with .candidates
    - mappings containing "candidates"
    """

    if result is None:
        return []

    if isinstance(
        result,
        (list, tuple),
    ):
        return list(result)

    if isinstance(
        result,
        Mapping,
    ):
        candidates = result.get(
            "candidates",
            [],
        )

        if isinstance(
            candidates,
            (list, tuple),
        ):
            return list(candidates)

        return []

    candidates = getattr(
        result,
        "candidates",
        None,
    )

    if candidates is not None:
        return list(candidates)

    return []


def _extract_run(
    result: Any,
) -> Any:
    """Return the persisted run when one is available."""

    if isinstance(
        result,
        GenerativeDesignRunResponse,
    ):
        return result

    if hasattr(
        result,
        "candidates",
    ):
        return result

    if isinstance(
        result,
        Mapping,
    ):
        run = result.get(
            "run"
        )

        if run is not None:
            return run

    return None


# =====================================================================
# DEFAULT CONSTRAINTS
# =====================================================================

def _default_constraints() -> dict[str, Any]:
    """
    Return a practical initial constraint payload.

    Project ID is intentionally left unset until the user selects a
    project.
    """

    return {
        "project_id": None,
        "site": {
            "width": 30.0,
            "depth": 40.0,
            "north_access": True,
            "setback_front": 5.0,
            "setback_rear": 3.0,
            "setback_left": 3.0,
            "setback_right": 3.0,
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
                    "area": 14.0,
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


# =====================================================================
# PROJECT ID
# =====================================================================

def _parse_project_id(
    value: str,
) -> UUID | None:
    """Convert an optional Streamlit project ID to UUID."""

    value = value.strip()

    if not value:
        return None

    try:
        return UUID(value)
    except ValueError:
        return None


# =====================================================================
# PROJECT SELECTION
# =====================================================================

def _render_project_selection() -> UUID | None:
    """Render the project identifier input."""

    st.subheader("Project")

    project_id_text = st.text_input(
        "Project UUID",
        value="",
        key="generative_design_project_id",
        help=(
            "Enter the UUID of the project to which "
            "this generative-design run belongs."
        ),
    )

    if not project_id_text.strip():
        st.info(
            "No project selected. Generation can still be "
            "previewed, but persisted runs should normally "
            "belong to a project."
        )

        return None

    project_id = _parse_project_id(
        project_id_text
    )

    if project_id is None:
        st.error(
            "Project ID must be a valid UUID."
        )

        return None

    st.success(
        f"Project: `{project_id}`"
    )

    return project_id


# =====================================================================
# CONSTRAINT EDITOR
# =====================================================================

def _render_constraint_editor(
    project_id: UUID | None,
) -> DesignConstraints | None:
    """Render and validate the generative-design constraints."""

    defaults = (
        st.session_state.get(
            SESSION_CONSTRAINTS
        )
        or _default_constraints()
    )

    defaults = _as_dict(
        defaults
    )

    defaults["project_id"] = (
        project_id
    )

    site = defaults.get(
        "site",
        {},
    )

    zoning = defaults.get(
        "zoning",
        {},
    )

    program = defaults.get(
        "program",
        {},
    )

    compliance = defaults.get(
        "compliance",
        {},
    )

    with st.expander(
        "Site Constraints",
        expanded=True,
    ):

        width = st.number_input(
            "Site width (m)",
            min_value=1.0,
            value=float(
                site.get(
                    "width",
                    30.0,
                )
            ),
            step=1.0,
            key="gd_site_width",
        )

        depth = st.number_input(
            "Site depth (m)",
            min_value=1.0,
            value=float(
                site.get(
                    "depth",
                    40.0,
                )
            ),
            step=1.0,
            key="gd_site_depth",
        )

        north_access = st.checkbox(
            "North access",
            value=bool(
                site.get(
                    "north_access",
                    True,
                )
            ),
            key="gd_north_access",
        )

        col1, col2 = st.columns(2)

        with col1:
            setback_front = st.number_input(
                "Front setback (m)",
                min_value=0.0,
                value=float(
                    site.get(
                        "setback_front",
                        5.0,
                    )
                ),
                step=0.5,
                key="gd_setback_front",
            )

            setback_left = st.number_input(
                "Left setback (m)",
                min_value=0.0,
                value=float(
                    site.get(
                        "setback_left",
                        3.0,
                    )
                ),
                step=0.5,
                key="gd_setback_left",
            )

        with col2:
            setback_rear = st.number_input(
                "Rear setback (m)",
                min_value=0.0,
                value=float(
                    site.get(
                        "setback_rear",
                        3.0,
                    )
                ),
                step=0.5,
                key="gd_setback_rear",
            )

            setback_right = st.number_input(
                "Right setback (m)",
                min_value=0.0,
                value=float(
                    site.get(
                        "setback_right",
                        3.0,
                    )
                ),
                step=0.5,
                key="gd_setback_right",
            )

    with st.expander(
        "Zoning Constraints",
        expanded=True,
    ):

        col1, col2 = st.columns(2)

        with col1:
            max_site_coverage = st.slider(
                "Maximum site coverage",
                min_value=0.01,
                max_value=1.0,
                value=float(
                    zoning.get(
                        "max_site_coverage",
                        0.60,
                    )
                ),
                step=0.01,
                key="gd_max_site_coverage",
            )

            max_far = st.number_input(
                "Maximum FAR",
                min_value=0.01,
                value=float(
                    zoning.get(
                        "max_far",
                        2.0,
                    )
                ),
                step=0.1,
                key="gd_max_far",
            )

        with col2:
            max_height = st.number_input(
                "Maximum height (m)",
                min_value=0.1,
                value=float(
                    zoning.get(
                        "max_height",
                        15.0,
                    )
                ),
                step=0.5,
                key="gd_max_height",
            )

            max_storeys = st.number_input(
                "Maximum storeys",
                min_value=1,
                value=int(
                    zoning.get(
                        "max_storeys",
                        3,
                    )
                ),
                step=1,
                key="gd_max_storeys",
            )

    with st.expander(
        "Room Programme",
        expanded=True,
    ):

        circulation_ratio = st.slider(
            "Circulation ratio",
            min_value=0.0,
            max_value=1.0,
            value=float(
                program.get(
                    "circulation_ratio",
                    0.15,
                )
            ),
            step=0.01,
            key="gd_circulation_ratio",
        )

        existing_rooms = program.get(
            "rooms",
            [],
        )

        room_rows: list[dict[str, Any]] = []

        if existing_rooms:
            for room in existing_rooms:
                room_rows.append(
                    {
                        "name": room.get(
                            "name",
                            "",
                        ),
                        "area": float(
                            room.get(
                                "area",
                                10.0,
                            )
                        ),
                        "quantity": int(
                            room.get(
                                "quantity",
                                1,
                            )
                        ),
                        "required": bool(
                            room.get(
                                "required",
                                True,
                            )
                        ),
                    }
                )

        if not room_rows:
            room_rows = [
                {
                    "name": "Room",
                    "area": 10.0,
                    "quantity": 1,
                    "required": True,
                }
            ]

        edited_rooms = st.data_editor(
            room_rows,
            num_rows="dynamic",
            use_container_width=True,
            key="gd_rooms_editor",
            column_config={
                "name": st.column_config.TextColumn(
                    "Room",
                    required=True,
                ),
                "area": st.column_config.NumberColumn(
                    "Area (m²)",
                    min_value=0.1,
                    step=1.0,
                ),
                "quantity": st.column_config.NumberColumn(
                    "Quantity",
                    min_value=1,
                    step=1,
                ),
                "required": st.column_config.CheckboxColumn(
                    "Required",
                ),
            },
        )

    with st.expander(
        "Compliance",
        expanded=False,
    ):

        minimum_egress_width = st.number_input(
            "Minimum egress width (m)",
            min_value=0.1,
            value=float(
                compliance.get(
                    "minimum_egress_width",
                    1.1,
                )
            ),
            step=0.1,
            key="gd_egress_width",
        )

        accessibility_required = st.checkbox(
            "Accessibility required",
            value=bool(
                compliance.get(
                    "accessibility_required",
                    True,
                )
            ),
            key="gd_accessibility",
        )

        fire_separation_required = st.checkbox(
            "Fire separation required",
            value=bool(
                compliance.get(
                    "fire_separation_required",
                    True,
                )
            ),
            key="gd_fire_separation",
        )

    payload = {
        "project_id": project_id,
        "site": {
            "width": width,
            "depth": depth,
            "north_access": north_access,
            "setback_front": setback_front,
            "setback_rear": setback_rear,
            "setback_left": setback_left,
            "setback_right": setback_right,
        },
        "zoning": {
            "max_site_coverage": max_site_coverage,
            "max_far": max_far,
            "max_height": max_height,
            "max_storeys": max_storeys,
        },
        "program": {
            "rooms": [
                dict(row)
                for row in edited_rooms
            ],
            "circulation_ratio": circulation_ratio,
        },
        "compliance": {
            "minimum_egress_width": (
                minimum_egress_width
            ),
            "accessibility_required": (
                accessibility_required
            ),
            "fire_separation_required": (
                fire_separation_required
            ),
        },
        "metadata": {},
    }

    normalized, validation = (
        normalize_and_validate_constraints(
            payload
        )
    )

    if validation.warnings:
        with st.expander(
            "Constraint Warnings",
            expanded=False,
        ):
            for warning in validation.warnings:
                st.warning(warning)

    if validation.errors:
        st.error(
            "The design constraints are invalid."
        )

        for error in validation.errors:
            st.error(error)

        return None

    if normalized is None:
        st.error(
            "Constraint normalization failed."
        )

        return None

    st.session_state[
        SESSION_CONSTRAINTS
    ] = normalized

    return normalized


# =====================================================================
# CONSTRAINT SUMMARY
# =====================================================================

def _render_constraint_summary(
    constraints: DesignConstraints,
) -> None:
    """Render calculated constraint metrics."""

    summary = constraint_summary(
        constraints
    )

    site = summary["site"]
    program = summary["program"]
    zoning = summary["zoning"]

    st.subheader(
        "Design Envelope"
    )

    cols = st.columns(4)

    cols[0].metric(
        "Buildable Area",
        f"{site['buildable_area']:,.1f} m²",
    )

    cols[1].metric(
        "Required GFA",
        f"{program['required_gross_area']:,.1f} m²",
    )

    cols[2].metric(
        "Max FAR",
        f"{zoning['max_far']:.2f}",
    )

    cols[3].metric(
        "Max Storeys",
        str(
            zoning["max_storeys"]
        ),
    )


# =====================================================================
# CANDIDATE CARDS
# =====================================================================

def _render_candidate_card(
    candidate: Any,
    index: int,
) -> None:
    """Render one generated candidate."""

    name = _candidate_name(
        candidate
    )

    score = _candidate_score(
        candidate
    )

    rank = _candidate_rank(
        candidate
    )

    status = _candidate_status(
        candidate
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
        f"#{rank} "
        if rank is not None
        else f"Option {index + 1} "
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"### {title}{name}"
        )

        cols = st.columns(3)

        cols[0].metric(
            "Score",
            f"{score:.3f}",
        )

        cols[1].metric(
            "Status",
            status,
        )

        if isinstance(
            metrics,
            Mapping,
        ):
            gfa = metrics.get(
                "gross_floor_area"
            )

            if gfa is not None:
                cols[2].metric(
                    "GFA",
                    f"{float(gfa):,.1f} m²",
                )
            else:
                cols[2].metric(
                    "Rooms",
                    str(
                        metrics.get(
                            "room_count",
                            "-",
                        )
                    ),
                )
        else:
            cols[2].metric(
                "Rooms",
                "-",
            )

        with st.expander(
            "Inspect candidate",
            expanded=False,
        ):

            st.write(
                "**Geometry**"
            )
            st.json(
                _as_dict(
                    geometry
                )
            )

            st.write(
                "**Metrics**"
            )
            st.json(
                _as_dict(
                    metrics
                )
            )

            st.write(
                "**Evaluation**"
            )
            st.json(
                _as_dict(
                    evaluation
                )
            )

            candidate_id = _candidate_id(
                candidate
            )

            if candidate_id:
                st.caption(
                    f"Candidate UUID: {candidate_id}"
                )

        if st.button(
            "Select this design",
            key=(
                "gd_select_candidate_"
                f"{index}"
            ),
            use_container_width=True,
        ):
            st.session_state[
                SESSION_SELECTED_CANDIDATE
            ] = candidate

            st.rerun()


# =====================================================================
# CANDIDATE RESULTS
# =====================================================================

def _render_candidates(
    candidates: list[Any],
) -> None:
    """Render all candidates."""

    if not candidates:
        st.info(
            "No design candidates have been generated yet."
        )
        return

    st.subheader(
        f"Generated Designs ({len(candidates)})"
    )

    for index, candidate in enumerate(
        candidates
    ):
        _render_candidate_card(
            candidate,
            index,
        )


# =====================================================================
# BEST DESIGN
# =====================================================================

def _select_best_candidate(
    candidates: list[Any],
) -> Any | None:
    """Return the highest-scoring candidate."""

    if not candidates:
        return None

    return max(
        candidates,
        key=_candidate_score,
    )


def _render_best_design(
    candidates: list[Any],
) -> None:
    """Render the best candidate."""

    best = _select_best_candidate(
        candidates
    )

    if best is None:
        return

    st.subheader(
        "Recommended Design"
    )

    with st.container(
        border=True
    ):

        st.markdown(
            f"## {_candidate_name(best)}"
        )

        st.metric(
            "Design Score",
            f"{_candidate_score(best):.3f}",
        )

        geometry = _candidate_value(
            best,
            "geometry",
            {},
        )

        metrics = _candidate_value(
            best,
            "metrics",
            {},
        )

        if isinstance(
            geometry,
            Mapping,
        ):
            footprint = geometry.get(
                "footprint",
                {},
            )

            if isinstance(
                footprint,
                Mapping,
            ):
                cols = st.columns(3)

                cols[0].metric(
                    "Width",
                    f"{float(footprint.get('width', 0)):.2f} m",
                )

                cols[1].metric(
                    "Depth",
                    f"{float(footprint.get('depth', 0)):.2f} m",
                )

                cols[2].metric(
                    "Storeys",
                    str(
                        geometry.get(
                            "storeys",
                            "-",
                        )
                    ),
                )

        if st.button(
            "Select recommended design",
            key="gd_select_best",
            use_container_width=True,
        ):
            st.session_state[
                SESSION_SELECTED_CANDIDATE
            ] = best

            st.rerun()


# =====================================================================
# SELECTED DESIGN
# =====================================================================

def _render_selected_design() -> None:
    """Render the currently selected candidate."""

    candidate = st.session_state.get(
        SESSION_SELECTED_CANDIDATE
    )

    if candidate is None:
        return

    st.subheader(
        "Selected Design"
    )

    st.success(
        f"Selected: {_candidate_name(candidate)}"
    )

    candidate_id = _candidate_id(
        candidate
    )

    if candidate_id:
        st.caption(
            f"Candidate UUID: {candidate_id}"
        )

    cols = st.columns(2)

    with cols[0]:
        st.write(
            "**Geometry**"
        )
        st.json(
            _as_dict(
                _candidate_value(
                    candidate,
                    "geometry",
                    {},
                )
            )
        )

    with cols[1]:
        st.write(
            "**Metrics**"
        )
        st.json(
            _as_dict(
                _candidate_value(
                    candidate,
                    "metrics",
                    {},
                )
            )
        )


# =====================================================================
# RUN RESULT
# =====================================================================

def _render_run_result(
    result: Any,
) -> None:
    """Render the service response."""

    if result is None:
        return

    run = _extract_run(
        result
    )

    candidates = _extract_candidates(
        result
    )

    if run is not None:

        status = str(
            getattr(
                run,
                "status",
                STATUS_COMPLETED,
            )
        )

        if status == STATUS_COMPLETED:
            st.success(
                "Generative design run completed."
            )

        elif status == STATUS_FAILED:
            st.error(
                str(
                    getattr(
                        run,
                        "error_message",
                        "Generation failed.",
                    )
                )
            )

        else:
            st.info(
                f"Run status: {status}"
            )

        candidate_count = getattr(
            run,
            "candidate_count",
            len(candidates),
        )

        st.caption(
            f"Persisted candidates: {candidate_count}"
        )

        run_id = getattr(
            run,
            "id",
            None,
        )

        if run_id:
            st.caption(
                f"Run UUID: {run_id}"
            )

    _render_best_design(
        candidates
    )

    _render_candidates(
        candidates
    )


# =====================================================================
# GENERATION
# =====================================================================

def _generate(
    constraints: DesignConstraints,
    candidate_count: int,
) -> Any:
    """
    Generate and persist candidates through the service.

    The service owns the transaction boundary.
    """

    return _run_async(
        _generate_with_service(
            constraints,
            candidate_count,
        )
    )


def _render_generation_controls(
    constraints: DesignConstraints,
) -> None:
    """Render the generation controls."""

    st.subheader(
        "Generate Designs"
    )

    candidate_count = st.slider(
        "Number of candidates",
        min_value=1,
        max_value=100,
        value=DEFAULT_CANDIDATE_COUNT,
        key="gd_candidate_count",
    )

    run_name = st.text_input(
        "Run name",
        value="Generative Design Run",
        max_chars=255,
        key="gd_run_name",
    )

    generate = st.button(
        "Generate Design Options",
        type="primary",
        use_container_width=True,
        key="gd_generate",
    )

    if not generate:
        return

    if not run_name.strip():
        st.error(
            "Run name cannot be empty."
        )
        return

    st.session_state[
        SESSION_RESULT
    ] = None

    with st.status(
        "Generating design options...",
        expanded=True,
    ) as status:

        st.write(
            "Validating constraints..."
        )

        normalized, validation = (
            normalize_and_validate_constraints(
                constraints
            )
        )

        if validation.errors:
            status.update(
                label="Generation blocked",
                state="error",
            )

            for error in validation.errors:
                st.error(error)

            return

        if normalized is None:
            status.update(
                label="Generation blocked",
                state="error",
            )

            st.error(
                "Unable to normalize design constraints."
            )

            return

        normalized.metadata = {
            **normalized.metadata,
            "run_name": run_name.strip(),
        }

        st.write(
            "Constraints validated."
        )

        st.write(
            f"Generating {candidate_count} candidates..."
        )

        try:
            result = _generate(
                normalized,
                candidate_count,
            )

            st.session_state[
                SESSION_RESULT
            ] = result

            status.update(
                label="Generation complete",
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

            st.exception(exc)


# =====================================================================
# REGENERATION
# =====================================================================

def _render_regeneration(
    constraints: DesignConstraints,
) -> None:
    """Render a lightweight regeneration control."""

    result = st.session_state.get(
        SESSION_RESULT
    )

    if result is None:
        return

    candidates = _extract_candidates(
        result
    )

    if not candidates:
        return

    st.divider()

    st.subheader(
        "Regenerate"
    )

    st.caption(
        "Generate a fresh candidate set using the current constraints."
    )

    if st.button(
        "Regenerate",
        key="gd_regenerate",
        use_container_width=True,
    ):

        candidate_count = st.session_state.get(
            "gd_candidate_count",
            DEFAULT_CANDIDATE_COUNT,
        )

        with st.spinner(
            "Regenerating designs..."
        ):
            try:
                result = _generate(
                    constraints,
                    int(candidate_count),
                )

                st.session_state[
                    SESSION_RESULT
                ] = result

                st.session_state[
                    SESSION_SELECTED_CANDIDATE
                ] = None

                st.rerun()

            except Exception as exc:
                st.error(
                    f"Regeneration failed: {exc}"
                )


# =====================================================================
# RUN HISTORY
# =====================================================================

def _load_run_history(
    project_id: UUID | None,
) -> Any:
    """
    Load run history through the service layer.

    This method intentionally uses capability detection because the
    service/repository API may expose history under different method
    names while the core generation contract remains stable.
    """

    if project_id is None:
        return []

    async def operation() -> Any:

        from database.connection import (
            AsyncSessionLocal,
        )

        async with AsyncSessionLocal() as session:

            service = (
                GenerativeDesignService(
                    session=session,
                )
            )

            for method_name in (
                "list_runs",
                "get_run_history",
                "list_run_history",
            ):

                method = getattr(
                    service,
                    method_name,
                    None,
                )

                if method is None:
                    continue

                result = method(
                    project_id=project_id
                )

                if inspect.isawaitable(
                    result
                ):
                    result = await result

                return result

        return []

    return _run_async(
        operation()
    )


def _render_run_history(
    project_id: UUID | None,
) -> None:
    """Render persisted generative-design run history."""

    if project_id is None:
        return

    with st.expander(
        "Run History",
        expanded=False,
    ):

        if st.button(
            "Refresh Run History",
            key="gd_refresh_history",
        ):

            try:
                history = _load_run_history(
                    project_id
                )

                st.session_state[
                    "gd_run_history"
                ] = history

            except Exception as exc:
                st.error(
                    f"Unable to load run history: {exc}"
                )

        history = st.session_state.get(
            "gd_run_history"
        )

        if history is None:
            st.caption(
                "Click Refresh Run History to load persisted runs."
            )
            return

        if not history:
            st.info(
                "No generative-design runs were found."
            )
            return

        for index, run in enumerate(
            history
        ):

            if isinstance(
                run,
                Mapping,
            ):
                run_id = run.get(
                    "id"
                )
                name = run.get(
                    "name",
                    f"Run {index + 1}",
                )
                status = run.get(
                    "status",
                    "-",
                )
                count = run.get(
                    "candidate_count",
                    0,
                )

            else:
                run_id = getattr(
                    run,
                    "id",
                    None,
                )

                name = getattr(
                    run,
                    "name",
                    f"Run {index + 1}",
                )

                status = getattr(
                    run,
                    "status",
                    "-",
                )

                count = getattr(
                    run,
                    "candidate_count",
                    0,
                )

            st.write(
                f"**{name}**"
            )

            st.caption(
                f"Status: {status} · "
                f"Candidates: {count}"
            )

            if run_id:
                st.caption(
                    f"Run UUID: {run_id}"
                )

            if index < len(history) - 1:
                st.divider()


# =====================================================================
# MAIN RENDERER
# =====================================================================

def render_generative_design() -> None:
    """
    Render the complete Generative Design module.

    This is the public entry point imported by streamlit_app.py.
    """

    st.title(
        "Generative Design"
    )

    st.caption(
        "Constraint-driven architectural design generation."
    )

    project_id = _render_project_selection()

    st.divider()

    constraints = _render_constraint_editor(
        project_id
    )

    if constraints is None:
        return

    _render_constraint_summary(
        constraints
    )

    st.divider()

    _render_generation_controls(
        constraints
    )

    result = st.session_state.get(
        SESSION_RESULT
    )

    if result is not None:
        st.divider()

        _render_run_result(
            result
        )

        _render_selected_design()

        _render_regeneration(
            constraints
        )

    _render_run_history(
        project_id
    )