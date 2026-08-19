"""
IMAGINE Site Planning Streamlit interface.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _render_summary(
    service,
) -> None:

    summary = service.summary_sync()

    st.subheader(
        "Site Planning Summary"
    )

    if isinstance(summary, dict):

        columns = st.columns(4)

        values = [
            ("Site Plans", summary.get("total", 0)),
            ("Approved", summary.get("approved", 0)),
            ("Draft", summary.get("draft", 0)),
            ("Rejected", summary.get("rejected", 0)),
        ]

        for column, (label, value) in zip(
            columns,
            values,
        ):

            with column:

                st.metric(
                    label,
                    value,
                )

    else:

        st.info(
            "No site planning summary is available."
        )


def _render_create_form(
    service,
) -> None:

    st.subheader(
        "Create Site Plan"
    )

    with st.form(
        "site_planning_create_form",
        clear_on_submit=True,
    ):

        name = st.text_input(
            "Site Plan Name"
        )

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "Create Site Plan"
        )

        if submitted:

            if not name.strip():

                st.error(
                    "Site Plan Name is required."
                )

                return

            data = {
                "name": name.strip(),
                "description": description.strip(),
            }

            try:

                service.create_sync(
                    data
                )

                st.success(
                    "Site Plan created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Site Plan could not be created."
                )

                st.exception(exc)


def _render_site_plan_list(
    service,
) -> None:

    st.subheader(
        "Site Plans"
    )

    try:

        site_plans = service.list_sync()

    except Exception as exc:

        st.error(
            "Site Plans could not be loaded."
        )

        st.exception(exc)

        return

    if not site_plans:

        st.info(
            "No Site Plans have been created yet."
        )

        return

    for site_plan in site_plans:

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

        description = getattr(
            site_plan,
            "description",
            "",
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {name}"
            )

            if description:

                st.write(
                    description
                )

            if site_plan_id is not None:

                st.caption(
                    f"ID: {site_plan_id}"
                )


def render_site_planning(
    service,
) -> None:
    """
    Render Site Planning using one synchronous service.

    The Streamlit application supplies the service.
    """

    st.title(
        "Site Planning"
    )

    st.caption(
        "Site organization and development planning."
    )

    try:

        _render_summary(
            service
        )

    except Exception as exc:

        st.error(
            "Site Planning summary could not be loaded."
        )

        with st.expander(
            "Complete summary traceback",
            expanded=True,
        ):

            st.exception(exc)

    st.divider()

    _render_create_form(
        service
    )

    st.divider()

    _render_site_plan_list(
        service
    )