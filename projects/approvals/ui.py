"""
IMAGINE Project Approvals Streamlit UI.
"""

from __future__ import annotations

import streamlit as st


def _get_db():
    from database.connection import SessionLocal

    return SessionLocal()


def render_approvals() -> None:

    st.title("Approvals")

    st.caption(
        "Project approval records and authorization workflow."
    )

    try:

        from projects.approvals.schemas import (
            ApprovalCreate,
        )

        from projects.approvals.service import (
            create_approval,
            list_approvals,
        )

    except Exception as exc:

        st.error(
            "Approvals could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    project_id = st.number_input(
        "Project ID",
        min_value=1,
        step=1,
        key="approval_project_id",
    )

    st.subheader("Create Approval")

    with st.form("approval_create_form"):

        approver_id = st.number_input(
            "Approver ID",
            min_value=1,
            step=1,
        )

        comment = st.text_area(
            "Comment"
        )

        submitted = st.form_submit_button(
            "Create Approval",
            use_container_width=True,
        )

    if submitted:

        db = _get_db()

        try:

            payload = ApprovalCreate(
                project_id=int(project_id),
                approver_id=int(approver_id),
                comment=comment or None,
            )

            create_approval(
                db=db,
                project_id=payload.project_id,
                approver_id=payload.approver_id,
                comment=payload.comment,
            )

            st.success(
                "Approval created."
            )

            st.rerun()

        except Exception as exc:

            db.rollback()

            st.error(
                "Approval could not be created."
            )

            with st.expander(
                "Complete error",
                expanded=True,
            ):
                st.exception(exc)

        finally:
            db.close()

    st.divider()

    db = _get_db()

    try:

        approvals = list_approvals(
            db=db,
            project_id=int(project_id),
        )

        st.subheader("Approvals")

        rows = [
            {
                "ID": item.id,
                "Project": item.project_id,
                "Approver": item.approver_id,
                "Status": item.status,
                "Comment": item.comment,
            }
            for item in approvals
        ]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Approvals could not be listed."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:
        db.close()