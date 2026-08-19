"""
IMAGINE
Architecture / Site Planning UI

Streamlit interface for Site Planning.

UI responsibilities:
    - Render the Site Planning interface.
    - Construct the synchronous service once per render.
    - Pass the same service instance to all UI helpers.
    - Keep the Streamlit renderer zero-argument.

Domain responsibilities remain inside:
    models.py
    repository.py
    service.py
"""


from __future__ import annotations

from typing import Any

import streamlit as st

from .service import SitePlanService


# ============================================================
# SERVICE FACTORY
# ============================================================


def _get_sync_service() -> SitePlanService:
    """
    Construct the Site Planning service.

    The service exposes synchronous adapters for Streamlit:

        list_sync()
        create_sync()
        update_sync()
        delete_sync()
        summary_sync()

    A single service instance is shared across the entire
    render_site_planning() call.
    """

    return SitePlanService()


# ============================================================
# SUMMARY
# ============================================================


def _render_summary(
    service: SitePlanService,
) -> None:
    """
    Render Site Planning summary information.

    The service instance is supplied by render_site_planning()
    so that the same synchronous service is used throughout
    the page.
    """

    try:

        summary = service.summary_sync()

    except Exception as exc:

        st.error(
            "Site Planning summary could not be loaded."
        )

        with st.expander(
            "Complete summary traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    if not isinstance(summary, dict):

        st.warning(
            "Site Planning summary returned an unexpected format."
        )

        return

    total = summary.get(
        "total",
        summary.get(
            "count",
            0,
        ),
    )

    active = summary.get(
        "active",
        0,
    )

    completed = summary.get(
        "completed",
        0,
    )

    area = summary.get(
        "total_area",
        summary.get(
            "area",
            0,
        ),
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Site Plans",
            total,
        )

    with col2:

        st.metric(
            "Active",
            active,
        )

    with col3:

        st.metric(
            "Completed",
            completed,
        )

    with col4:

        st.metric(
            "Total Area",
            area,
        )


# ============================================================
# CREATE FORM
# ============================================================


def _render_create_form(
    service: SitePlanService,
) -> None:
    """
    Render the Site Plan creation form.

    The supplied service is used for creation so that the
    renderer does not construct another service instance.
    """

    st.subheader(
        "Create Site Plan"
    )

    with st.form(
        "site_planning_create_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Site Plan Name",
                key="site_planning_create_name",
            )

            site_name = st.text_input(
                "Site Name",
                key="site_planning_create_site_name",
            )

            project_id = st.text_input(
                "Project ID",
                key="site_planning_create_project_id",
            )

        with col2:

            site_area = st.number_input(
                "Site Area",
                min_value=0.0,
                step=1.0,
                key="site_planning_create_site_area",
            )

            building_coverage = st.number_input(
                "Building Coverage",
                min_value=0.0,
                step=0.01,
                key="site_planning_create_building_coverage",
            )

            notes = st.text_area(
                "Notes",
                key="site_planning_create_notes",
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

    payload: dict[str, Any] = {
        "name": name.strip(),
        "site_name": site_name.strip(),
        "project_id": project_id.strip(),
        "site_area": site_area,
        "building_coverage": building_coverage,
        "notes": notes.strip(),
    }

    try:

        service.create_sync(
            payload
        )

    except TypeError:

        # ----------------------------------------------------
        # Compatibility path for services whose create_sync()
        # accepts keyword arguments rather than a dictionary.
        # ----------------------------------------------------

        try:

            service.create_sync(
                name=name.strip(),
                site_name=site_name.strip(),
                project_id=project_id.strip(),
                site_area=site_area,
                building_coverage=building_coverage,
                notes=notes.strip(),
            )

        except Exception as exc:

            st.error(
                "Site Plan could not be created."
            )

            with st.expander(
                "Complete create traceback",
                expanded=True,
            ):

                st.exception(exc)

            return

    except Exception as exc:

        st.error(
            "Site Plan could not be created."
        )

        with st.expander(
            "Complete create traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    st.success(
        "Site Plan created successfully."
    )

    st.rerun()


# ============================================================
# SITE PLAN LIST
# ============================================================


def _render_site_plan_list(
    service: SitePlanService,
) -> None:
    """
    Render the Site Plan records.

    The supplied service is reused for list, update and delete
    operations.
    """

    try:

        site_plans = service.list_sync()

    except Exception as exc:

        st.error(
            "Site Plans could not be loaded."
        )

        with st.expander(
            "Complete list traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    if site_plans is None:

        site_plans = []

    if not isinstance(
        site_plans,
        (list, tuple),
    ):

        st.warning(
            "Site Planning returned an unexpected record format."
        )

        return

    if not site_plans:

        st.info(
            "No Site Plans have been created yet."
        )

        return

    for site_plan in site_plans:

        _render_site_plan_record(
            service,
            site_plan,
        )


# ============================================================
# SITE PLAN RECORD
# ============================================================


def _render_site_plan_record(
    service: SitePlanService,
    site_plan: Any,
) -> None:
    """
    Render one Site Plan record.

    Supports either ORM-style objects or dictionary records.
    """

    if isinstance(
        site_plan,
        dict,
    ):

        site_plan_id = site_plan.get(
            "id"
        )

        name = site_plan.get(
            "name",
            "Unnamed Site Plan",
        )

        site_name = site_plan.get(
            "site_name",
            "",
        )

        status = site_plan.get(
            "status",
            "Draft",
        )

        site_area = site_plan.get(
            "site_area",
            "",
        )

        project_id = site_plan.get(
            "project_id",
            "",
        )

    else:

        site_plan_id = getattr(
            site_plan,
            "id",
            None,
        )

        name = getattr(
            site_plan,
            "name",
            "Unnamed Site Plan",
        )

        site_name = getattr(
            site_plan,
            "site_name",
            "",
        )

        status = getattr(
            site_plan,
            "status",
            "Draft",
        )

        site_area = getattr(
            site_plan,
            "site_area",
            "",
        )

        project_id = getattr(
            site_plan,
            "project_id",
            "",
        )

    title = str(
        name or "Unnamed Site Plan"
    )

    with st.container(
        border=True,
    ):

        st.markdown(
            f"### {title}"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.caption(
                "Site"
            )

            st.write(
                site_name or "-"
            )

        with col2:

            st.caption(
                "Project"
            )

            st.write(
                project_id or "-"
            )

        with col3:

            st.caption(
                "Area"
            )

            st.write(
                site_area or "-"
            )

        with col4:

            st.caption(
                "Status"
            )

            st.write(
                status or "-"
            )

        if site_plan_id is None:

            return

        edit_key = (
            f"site_plan_edit_{site_plan_id}"
        )

        delete_key = (
            f"site_plan_delete_{site_plan_id}"
        )

        with st.expander(
            "Actions",
            expanded=False,
        ):

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Edit",
                    key=edit_key,
                    use_container_width=True,
                ):

                    st.session_state[
                        f"site_plan_editing_{site_plan_id}"
                    ] = True

                    st.rerun()

            with col2:

                if st.button(
                    "Delete",
                    key=delete_key,
                    use_container_width=True,
                ):

                    try:

                        service.delete_sync(
                            site_plan_id
                        )

                    except Exception as exc:

                        st.error(
                            "Site Plan could not be deleted."
                        )

                        with st.expander(
                            "Complete delete traceback",
                            expanded=True,
                        ):

                            st.exception(exc)

                        return

                    st.success(
                        "Site Plan deleted successfully."
                    )

                    st.rerun()

        if st.session_state.get(
            f"site_plan_editing_{site_plan_id}",
            False,
        ):

            _render_edit_form(
                service,
                site_plan,
                site_plan_id,
            )


# ============================================================
# EDIT FORM
# ============================================================


def _render_edit_form(
    service: SitePlanService,
    site_plan: Any,
    site_plan_id: Any,
) -> None:
    """
    Render the Site Plan edit form.
    """

    if isinstance(
        site_plan,
        dict,
    ):

        current_name = site_plan.get(
            "name",
            "",
        )

        current_site_name = site_plan.get(
            "site_name",
            "",
        )

        current_project_id = site_plan.get(
            "project_id",
            "",
        )

        current_site_area = site_plan.get(
            "site_area",
            0.0,
        )

        current_coverage = site_plan.get(
            "building_coverage",
            0.0,
        )

        current_notes = site_plan.get(
            "notes",
            "",
        )

    else:

        current_name = getattr(
            site_plan,
            "name",
            "",
        )

        current_site_name = getattr(
            site_plan,
            "site_name",
            "",
        )

        current_project_id = getattr(
            site_plan,
            "project_id",
            "",
        )

        current_site_area = getattr(
            site_plan,
            "site_area",
            0.0,
        )

        current_coverage = getattr(
            site_plan,
            "building_coverage",
            0.0,
        )

        current_notes = getattr(
            site_plan,
            "notes",
            "",
        )

    with st.form(
        f"site_plan_edit_form_{site_plan_id}"
    ):

        name = st.text_input(
            "Site Plan Name",
            value=str(
                current_name or ""
            ),
        )

        site_name = st.text_input(
            "Site Name",
            value=str(
                current_site_name or ""
            ),
        )

        project_id = st.text_input(
            "Project ID",
            value=str(
                current_project_id or ""
            ),
        )

        site_area = st.number_input(
            "Site Area",
            min_value=0.0,
            value=float(
                current_site_area or 0
            ),
            step=1.0,
        )

        building_coverage = st.number_input(
            "Building Coverage",
            min_value=0.0,
            value=float(
                current_coverage or 0
            ),
            step=0.01,
        )

        notes = st.text_area(
            "Notes",
            value=str(
                current_notes or ""
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            save = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
            )

        with col2:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancel:

        st.session_state[
            f"site_plan_editing_{site_plan_id}"
        ] = False

        st.rerun()

    if not save:

        return

    if not name.strip():

        st.error(
            "Site Plan Name is required."
        )

        return

    payload: dict[str, Any] = {
        "name": name.strip(),
        "site_name": site_name.strip(),
        "project_id": project_id.strip(),
        "site_area": site_area,
        "building_coverage": building_coverage,
        "notes": notes.strip(),
    }

    try:

        service.update_sync(
            site_plan_id,
            payload,
        )

    except TypeError:

        # ----------------------------------------------------
        # Compatibility path for keyword-based update_sync()
        # implementations.
        # ----------------------------------------------------

        try:

            service.update_sync(
                site_plan_id,
                name=name.strip(),
                site_name=site_name.strip(),
                project_id=project_id.strip(),
                site_area=site_area,
                building_coverage=building_coverage,
                notes=notes.strip(),
            )

        except Exception as exc:

            st.error(
                "Site Plan could not be updated."
            )

            with st.expander(
                "Complete update traceback",
                expanded=True,
            ):

                st.exception(exc)

            return

    except Exception as exc:

        st.error(
            "Site Plan could not be updated."
        )

        with st.expander(
            "Complete update traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

    st.session_state[
        f"site_plan_editing_{site_plan_id}"
    ] = False

    st.success(
        "Site Plan updated successfully."
    )

    st.rerun()


# ============================================================
# MAIN ZERO-ARGUMENT RENDERER
# ============================================================


def render_site_planning() -> None:
    """
    Render the complete Site Planning interface.

    IMPORTANT:

    This function intentionally takes no arguments.

    The application shell can therefore call:

        render_site_planning()

    The synchronous service is constructed exactly once here
    and passed consistently to every helper:

        _render_summary(service)
        _render_create_form(service)
        _render_site_plan_list(service)

    This preserves the zero-argument Streamlit renderer
    contract while keeping service construction inside the
    Site Planning UI boundary.
    """

    st.title(
        "Site Planning"
    )

    st.caption(
        "Site organization, development allocation and planning controls."
    )

    # --------------------------------------------------------
    # Construct ONE synchronous service instance.
    # --------------------------------------------------------

    try:

        service = _get_sync_service()

    except Exception as exc:

        st.error(
            "The Site Planning service could not be initialized."
        )

        with st.expander(
            "Complete service initialization traceback",
            expanded=True,
        ):

            st.exception(exc)

        return

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
    # Existing Site Plans
    # --------------------------------------------------------

    st.subheader(
        "Site Plans"
    )

    _render_site_plan_list(
        service
    )