"""
IMAGINE Architecture
Floor Planning Streamlit UI
"""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st


def _format_bool(value: bool) -> str:
    return "✓ Pass" if value else "✗ Fail"


def render_floor_planning(
    service,
    site_plans=None,
    zoning_records=None,
):
    """
    Render the existing Architecture > Floor Planning interface.

    The service is responsible for all planning validation.
    """

    st.subheader("Floor Planning")

    site_plans = site_plans or []
    zoning_records = zoning_records or []

    st.caption(
        "Floor planning is constrained by Site Planning and Zoning."
    )

    if not site_plans:
        st.warning(
            "Create a Site Plan before creating a Floor Plan."
        )
        return

    if not zoning_records:
        st.warning(
            "Create a Zoning record before creating a Floor Plan."
        )
        return

    st.markdown("### Existing Floor Plans")

    plans = service.list_sync()

    if plans:

        data = []

        for plan in plans:

            data.append(
                {
                    "ID": str(plan.id),
                    "Plan": plan.name,
                    "Code": plan.plan_code,
                    "Building": plan.building_type,
                    "Floors": plan.number_of_floors,
                    "Footprint (m²)": float(
                        plan.building_footprint_m2
                    ),
                    "GFA (m²)": float(
                        plan.gross_floor_area_m2
                    ),
                    "Status": plan.status,
                }
            )

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No floor plans have been created yet."
        )

    st.markdown("### Create Floor Plan")

    site_options = {
        f"{site.name} ({site.site_code})": site
        for site in site_plans
    }

    zoning_options = {
        getattr(
            zoning,
            "zone_name",
            getattr(
                zoning,
                "name",
                f"Zoning {zoning.id}",
            ),
        ): zoning
        for zoning in zoning_records
    }

    with st.form(
        "floor_planning_create_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Floor Plan Name"
            )

            plan_code = st.text_input(
                "Plan Code"
            )

            building_type = st.selectbox(
                "Building Type",
                [
                    "Office",
                    "Residential",
                    "Mixed-Use",
                    "Hospital",
                    "School",
                    "Retail",
                    "Industrial",
                ],
            )

            selected_site_name = st.selectbox(
                "Site Plan",
                list(site_options.keys()),
            )

            selected_zoning_name = st.selectbox(
                "Zoning",
                list(zoning_options.keys()),
            )

        with col2:

            number_of_floors = st.number_input(
                "Number of Floors",
                min_value=1,
                max_value=200,
                value=5,
                step=1,
            )

            floor_area = st.number_input(
                "Floor Area (m²)",
                min_value=0.01,
                value=1000.0,
                step=50.0,
            )

            footprint = st.number_input(
                "Building Footprint (m²)",
                min_value=0.01,
                value=1000.0,
                step=50.0,
            )

            front_setback = st.number_input(
                "Front Setback (m)",
                min_value=0.0,
                value=5.0,
                step=0.5,
            )

            rear_setback = st.number_input(
                "Rear Setback (m)",
                min_value=0.0,
                value=5.0,
                step=0.5,
            )

            side_setback = st.number_input(
                "Side Setback (m)",
                min_value=0.0,
                value=4.0,
                step=0.5,
            )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Create Floor Plan"
        )

        if submitted:

            if not name.strip():
                st.error(
                    "Floor Plan Name is required."
                )

                return

            if not plan_code.strip():
                st.error(
                    "Plan Code is required."
                )

                return

            site = site_options[
                selected_site_name
            ]

            zoning = zoning_options[
                selected_zoning_name
            ]

            payload = {
                "name": name,
                "plan_code": plan_code,
                "site_plan_id": site.id,
                "zoning_id": zoning.id,
                "building_type": building_type,
                "number_of_floors": number_of_floors,
                "floor_area_m2": Decimal(
                    str(floor_area)
                ),
                "building_footprint_m2": Decimal(
                    str(footprint)
                ),
                "gross_floor_area_m2": (
                    Decimal(str(floor_area))
                    * Decimal(
                        str(number_of_floors)
                    )
                ),
                "front_setback_m": Decimal(
                    str(front_setback)
                ),
                "rear_setback_m": Decimal(
                    str(rear_setback)
                ),
                "side_setback_m": Decimal(
                    str(side_setback)
                ),
                "notes": notes or None,
                "status": "Draft",
                "active": True,
            }

            try:

                service.create_sync(
                    payload
                )

                st.success(
                    "Floor plan created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Unable to create floor plan: {exc}"
                )

    st.markdown("### Planning Validation")

    if plans:

        selected_plan = st.selectbox(
            "Select Floor Plan",
            plans,
            format_func=lambda p: (
                f"{p.name} ({p.plan_code})"
            ),
            key="floor_planning_validation_plan",
        )

        if st.button(
            "Run Planning Compliance Check",
            key="floor_planning_validate",
        ):

            try:

                result = (
                    service.validate_constraints_sync(
                        selected_plan.id
                    )
                )

                if result.overall_compliant:

                    st.success(
                        "✓ Floor plan complies with "
                        "the current Site Planning and "
                        "Zoning constraints."
                    )

                else:

                    st.error(
                        "✗ Floor plan is not compliant."
                    )

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Site Area",
                    f"{result.site_area_m2:,.0f} m²",
                )

                c2.metric(
                    "Coverage",
                    f"{result.proposed_coverage_percent:.1f}%",
                )

                c3.metric(
                    "FAR",
                    f"{result.proposed_far:.2f}",
                )

                c4.metric(
                    "GFA",
                    f"{result.proposed_gfa_m2:,.0f} m²",
                )

                validation = pd.DataFrame(
                    [
                        {
                            "Constraint": "Site Area",
                            "Status": _format_bool(
                                result.site_area_compliant
                            ),
                        },
                        {
                            "Constraint": "Setbacks",
                            "Status": _format_bool(
                                result.setbacks_compliant
                            ),
                        },
                        {
                            "Constraint": "Site Coverage",
                            "Status": _format_bool(
                                result.coverage_compliant
                            ),
                        },
                        {
                            "Constraint": "FAR",
                            "Status": _format_bool(
                                result.far_compliant
                            ),
                        },
                        {
                            "Constraint": "Maximum GFA",
                            "Status": _format_bool(
                                result.gfa_compliant
                            ),
                        },
                    ]
                )

                st.dataframe(
                    validation,
                    use_container_width=True,
                    hide_index=True,
                )

                if result.violations:

                    st.markdown(
                        "#### Planning Violations"
                    )

                    for violation in result.violations:
                        st.error(violation)

            except Exception as exc:

                st.error(
                    f"Validation failed: {exc}"
                )