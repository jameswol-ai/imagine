"""
IMAGINE
Site Planning UI

Streamlit interface for Site Planning.

The renderer intentionally has a zero-argument contract so it can
be registered directly with the IMAGINE application shell.

Database operations are performed through the synchronous
SitePlanService adapters:

    list_sync()
    create_sync()
    update_sync()
    delete_sync()
    summary_sync()

The asynchronous SitePlanService API remains unchanged.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pandas as pd
import streamlit as st

from .service import SitePlanService


# ============================================================
# SERVICE FACTORY
# ============================================================


def _get_sync_service() -> SitePlanService:
    """
    Create a SitePlanService instance for Streamlit.

    The synchronous adapter methods create their own async
    database sessions internally.

    No database session is retained by the Streamlit UI.
    """

    return SitePlanService.__new__(
        SitePlanService
    )


# ============================================================
# DATAFRAME CONVERSION
# ============================================================


def _plans_to_dataframe(
    plans: list[Any],
) -> pd.DataFrame:
    """
    Convert SitePlan ORM objects into a Streamlit dataframe.
    """

    rows: list[dict[str, Any]] = []

    for plan in plans:

        rows.append(
            {
                "ID": str(plan.id),
                "Site": plan.name,
                "Code": plan.site_code,
                "Status": plan.status,
                "Active": bool(plan.active),
                "Area (m²)": float(
                    plan.site_area_m2 or 0
                ),
                "Footprint (m²)": float(
                    plan.building_footprint_m2 or 0
                ),
                "Roads (m²)": float(
                    plan.road_area_m2 or 0
                ),
                "Parking (m²)": float(
                    plan.parking_area_m2 or 0
                ),
                "Landscape (m²)": float(
                    plan.landscape_area_m2 or 0
                ),
                "Slope (%)": float(
                    plan.slope_percent or 0
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# SUMMARY
# ============================================================


def _render_summary(
    service: SitePlanService,
) -> None:
    """
    Render Site Planning summary metrics.
    """

    try:

        summary = service.summary_sync()

    except Exception as exc:

        st.warning(
            "Site Planning summary could not be loaded."
        )

        with st.expander(
            "Summary error",
            expanded=False,
        ):

            st.exception(exc)

        return

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total Plans",
            summary.get(
                "total_plans",
                0,
            ),
        )

    with col2:

        st.metric(
            "Active",
            summary.get(
                "active_plans",
                0,
            ),
        )

    with col3:

        st.metric(
            "Approved",
            summary.get(
                "approved_plans",
                0,
            ),
        )

    with col4:

        st.metric(
            "Site Area",
            f'{float(summary.get("total_site_area_m2", 0)):,.0f} m²',
        )

    with col5:

        st.metric(
            "Landscape",
            f'{float(summary.get("total_landscaped_area_m2", 0)):,.0f} m²',
        )


# ============================================================
# CREATE FORM
# ============================================================


def _render_create_form(
    service: SitePlanService,
) -> None:
    """
    Render the Site Planning create form.
    """

    with st.expander(
        "Add Site Plan",
        expanded=False,
    ):

        with st.form(
            "site_planning_create_form",
            clear_on_submit=True,
        ):

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Site Plan Name"
                )

                code = st.text_input(
                    "Site Code"
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Draft",
                        "Proposed",
                        "Approved",
                        "Archived",
                    ],
                )

                site_area = st.number_input(
                    "Site Area (m²)",
                    min_value=0.01,
                    value=5000.0,
                    step=100.0,
                )

                footprint = st.number_input(
                    "Building Footprint (m²)",
                    min_value=0.0,
                    value=2000.0,
                    step=100.0,
                )

                road = st.number_input(
                    "Road Area (m²)",
                    min_value=0.0,
                    value=800.0,
                    step=50.0,
                )

            with col2:

                parking = st.number_input(
                    "Parking Area (m²)",
                    min_value=0.0,
                    value=700.0,
                    step=50.0,
                )

                landscape = st.number_input(
                    "Landscape Area (m²)",
                    min_value=0.0,
                    value=1500.0,
                    step=50.0,
                )

                orientation = st.number_input(
                    "North Orientation (°)",
                    min_value=0.0,
                    max_value=359.99,
                    value=0.0,
                    step=1.0,
                )

                slope = st.number_input(
                    "Slope (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    step=0.5,
                )

                soil = st.selectbox(
                    "Soil Type",
                    [
                        "Clay",
                        "Sand",
                        "Rock",
                        "Silt",
                        "Mixed",
                    ],
                )

                drainage = st.text_input(
                    "Drainage Strategy"
                )

                access = st.text_input(
                    "Access Strategy"
                )

            submitted = st.form_submit_button(
                "Create Site Plan",
                use_container_width=True,
            )

            if not submitted:
                return

            if not name.strip():

                st.error(
                    "Site Plan Name is required."
                )

                return

            if not code.strip():

                st.error(
                    "Site Code is required."
                )

                return

            payload = {
                "name": name.strip(),
                "site_code": code.strip(),
                "status": status,
                "site_area_m2": Decimal(
                    str(site_area)
                ),
                "building_footprint_m2": Decimal(
                    str(footprint)
                ),
                "road_area_m2": Decimal(
                    str(road)
                ),
                "parking_area_m2": Decimal(
                    str(parking)
                ),
                "landscape_area_m2": Decimal(
                    str(landscape)
                ),
                "north_orientation_deg": Decimal(
                    str(orientation)
                ),
                "slope_percent": Decimal(
                    str(slope)
                ),
                "soil_type": soil,
                "drainage_strategy": (
                    drainage.strip()
                    or None
                ),
                "access_strategy": (
                    access.strip()
                    or None
                ),
                "active": True,
            }

            try:

                service.create_sync(
                    payload
                )

                st.success(
                    "Site plan created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Site plan could not be created."
                )

                with st.expander(
                    "Complete create error",
                    expanded=True,
                ):

                    st.exception(exc)


# ============================================================
# SITE PLAN LIST
# ============================================================


def _render_site_plan_list(
    service: SitePlanService,
) -> None:
    """
    Render existing Site Plans.
    """

    try:

        plans = service.list_sync()

    except Exception as exc:

        st.error(
            "Site Plans could not be loaded."
        )

        with st.expander(
            "Complete database error",
            expanded=True,
        ):

            st.exception(exc)

        return

    if not plans:

        st.info(
            "No site plans have been created yet."
        )

        return

    dataframe = _plans_to_dataframe(
        plans
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# MAIN RENDERER
# ============================================================


def render_site_planning() -> None:
    """
    Zero-argument Site Planning renderer.

    This is the renderer expected by the IMAGINE application
    registry:

        render_site_planning()

    The renderer obtains a sync-capable SitePlanService and
    delegates database work to its synchronous adapters.
    """

    st.title(
        "Site Planning"
    )

    st.caption(
        "Site organization, land allocation and development planning."
    )

    service = _get_sync_service()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    _render_summary(
        service
    )

    st.divider()

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    _render_create_form(
        service
    )

    st.divider()

    # --------------------------------------------------------
    # Existing plans
    # --------------------------------------------------------

    st.subheader(
        "Site Plans"
    )

    _render_site_plan_list(
        service
    )