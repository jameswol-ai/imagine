"""
Streamlit UI for Architecture Compliance.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from database.connection import SessionLocal

from .schemas import ComplianceAssessmentCreate, ComplianceCheckInput
from .service import ComplianceService


def _get_db():
    return SessionLocal()


def render_compliance() -> None:
    """
    Render the Architecture → Compliance interface.

    Designed to replace the previous placeholder implementation
    without changing the surrounding Architecture navigation.
    """

    st.subheader("Compliance Checking")

    db = _get_db()

    try:
        service = ComplianceService(db)

        assessments = service.list_assessments()

        assessment_options = {
            assessment.name: assessment.id
            for assessment in assessments
        }

        selected_name = None

        if assessment_options:
            selected_name = st.selectbox(
                "Compliance Assessment",
                list(assessment_options.keys()),
            )

        with st.expander(
            "➕ Create Compliance Assessment",
            expanded=not bool(assessment_options),
        ):
            with st.form("compliance_assessment_form"):
                name = st.text_input(
                    "Assessment Name",
                    value="New Compliance Assessment",
                )

                notes = st.text_area(
                    "Notes",
                )

                submitted = st.form_submit_button(
                    "Create Assessment",
                )

                if submitted:
                    if not name.strip():
                        st.error(
                            "Assessment name is required."
                        )
                    else:
                        service.create_assessment(
                            ComplianceAssessmentCreate(
                                name=name.strip(),
                                notes=notes or None,
                            )
                        )

                        st.success(
                            "Compliance assessment created."
                        )

                        st.rerun()

        st.divider()

        st.markdown("### Building & Site Inputs")

        col1, col2, col3 = st.columns(3)

        with col1:
            site_area = st.number_input(
                "Site Area (m²)",
                min_value=0.01,
                value=5000.0,
                step=100.0,
            )

            building_footprint = st.number_input(
                "Building Footprint (m²)",
                min_value=0.0,
                value=2500.0,
                step=50.0,
            )

            gross_floor_area = st.number_input(
                "Gross Floor Area (m²)",
                min_value=0.0,
                value=10000.0,
                step=100.0,
            )

        with col2:
            building_height = st.number_input(
                "Building Height (m)",
                min_value=0.0,
                value=25.0,
                step=0.5,
            )

            front_setback = st.number_input(
                "Front Setback (m)",
                min_value=0.0,
                value=5.0,
                step=0.5,
            )

            side_setback = st.number_input(
                "Side Setback (m)",
                min_value=0.0,
                value=3.0,
                step=0.5,
            )

        with col3:
            rear_setback = st.number_input(
                "Rear Setback (m)",
                min_value=0.0,
                value=3.0,
                step=0.5,
            )

            max_height = st.number_input(
                "Maximum Height (m)",
                min_value=0.0,
                value=30.0,
                step=0.5,
            )

            max_coverage = st.number_input(
                "Maximum Site Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=1.0,
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            max_far = st.number_input(
                "Maximum FAR",
                min_value=0.01,
                value=2.0,
                step=0.1,
            )

        with col5:
            min_front = st.number_input(
                "Required Front Setback (m)",
                min_value=0.0,
                value=5.0,
                step=0.5,
            )

        with col6:
            min_side = st.number_input(
                "Required Side Setback (m)",
                min_value=0.0,
                value=3.0,
                step=0.5,
            )

        min_rear = st.number_input(
            "Required Rear Setback (m)",
            min_value=0.0,
            value=3.0,
            step=0.5,
        )

        if st.button(
            "🔍 Run Compliance Check",
            type="primary",
        ):
            data = ComplianceCheckInput(
                site_area_m2=site_area,
                building_footprint_m2=building_footprint,
                gross_floor_area_m2=gross_floor_area,
                building_height_m=building_height,
                front_setback_m=front_setback,
                side_setback_m=side_setback,
                rear_setback_m=rear_setback,
                max_height_m=max_height,
                max_coverage_percent=max_coverage,
                max_far=max_far,
                min_front_setback_m=min_front,
                min_side_setback_m=min_side,
                min_rear_setback_m=min_rear,
            )

            if selected_name:
                assessment_id = assessment_options[
                    selected_name
                ]

                result = service.run_and_save(
                    assessment_id,
                    data,
                )
            else:
                result = service.evaluate(data)

            st.divider()

            status = result.status

            if status == "PASS":
                st.success(
                    f"✅ Overall Compliance: PASS "
                    f"({result.score:.1f}%)"
                )
            elif status == "FAIL":
                st.error(
                    f"❌ Overall Compliance: FAIL "
                    f"({result.score:.1f}%)"
                )
            elif status == "WARNING":
                st.warning(
                    f"⚠️ Overall Compliance: WARNING "
                    f"({result.score:.1f}%)"
                )
            else:
                st.info(
                    f"Compliance Status: {status}"
                )

            k1, k2, k3, k4 = st.columns(4)

            k1.metric(
                "Score",
                f"{result.score:.1f}%",
            )

            k2.metric(
                "Passed",
                result.passed,
            )

            k3.metric(
                "Warnings",
                result.warnings,
            )

            k4.metric(
                "Failed",
                result.failed,
            )

            rows = [
                {
                    "Rule": item.rule_name,
                    "Category": item.category,
                    "Required": item.required_value,
                    "Actual": item.actual_value,
                    "Unit": item.unit,
                    "Status": item.status,
                    "Message": item.message,
                }
                for item in result.results
            ]

            df = pd.DataFrame(rows)

            st.subheader("Compliance Results")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

        if assessments:
            st.divider()

            st.subheader("Saved Assessments")

            rows = [
                {
                    "ID": assessment.id,
                    "Assessment": assessment.name,
                    "Status": assessment.status,
                    "Score": assessment.score,
                    "Created": assessment.created_at,
                }
                for assessment in assessments
            ]

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

    finally:
        db.close()


def render() -> None:
    """
    Compatibility entry point.
    """

    render_compliance()