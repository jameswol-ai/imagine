"""
IMAGINE
Project Approvals Streamlit UI.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import streamlit as st


def _get_attr(
    obj: Any,
    name: str,
    default: Any = None,
) -> Any:
    return getattr(
        obj,
        name,
        default,
    )


def _status_value(
    value: Any,
) -> str:
    if value is None:
        return "unknown"

    return str(
        getattr(
            value,
            "value",
            value,
        )
    )


def _session():
    from database.connection import SessionLocal

    return SessionLocal()


def _parse_project_id(value: str) -> UUID | None:
    value = value.strip()

    if not value:
        return None

    try:
        return UUID(value)
    except ValueError:
        return None


def render_approvals() -> None:

    st.title(
        "Approvals"
    )

    st.caption(
        "Project approval records and authorization workflow."
    )

    try:

        from projects.approvals.service import (
            create_approval,
            list_approvals,
        )

        from projects.approvals.schemas import (
            ApprovalCreate,
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

    project_id_text = st.text_input(
        "Project ID",
        key="approvals_project_id",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        help="Enter the UUID of an existing project.",
    )

    project_id = _parse_project_id(
        project_id_text
    )

    if project_id_text.strip() and project_id is None:
        st.error(
            "Project ID must be a valid UUID."
        )

    st.subheader(
        "Create Approval"
    )

    with st.form(
        "approvals_create_form"
    ):

        approver_id = st.number_input(
            "Approver ID",
            min_value=1,
            value=1,
            step=1,
        )

        comment = st.text_area(
            "Comment",
        )

        submitted = st.form_submit_button(
            "Create Approval",
            use_container_width=True,
        )

    if submitted:

        if project_id is None:

            st.error(
                "A valid Project UUID is required."
            )

        else:

            db = None

            try:

                payload = ApprovalCreate(
                    project_id=project_id,
                    approver_id=int(
                        approver_id
                    ),
                    comment=(
                        comment.strip()
                        or None
                    ),
                )

                db = _session()

                create_approval(
                    db=db,
                    project_id=payload.project_id,
                    approver_id=payload.approver_id,
                    comment=payload.comment,
                )

                st.success(
                    "Approval created successfully."
                )

                st.rerun()

            except Exception as exc:

                if db is not None:
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

                if db is not None:
                    db.close()

    st.divider()

    if project_id is None:

        st.info(
            "Enter a valid Project UUID to load approval records."
        )

        return

    db = None

    try:

        db = _session()

        approvals = list_approvals(
            db=db,
            project_id=project_id,
        )

        approvals = list(
            approvals or []
        )

        st.subheader(
            "Approval Records"
        )

        if not approvals:

            st.info(
                "No approval records exist for this project."
            )

            return

        rows = []

        for approval in approvals:

            rows.append(
                {
                    "ID": _get_attr(
                        approval,
                        "id",
                    ),
                    "Project ID": _get_attr(
                        approval,
                        "project_id",
                    ),
                    "Approver ID": _get_attr(
                        approval,
                        "approver_id",
                    ),
                    "Status": _status_value(
                        _get_attr(
                            approval,
                            "status",
                        )
                    ),
                    "Comment": _get_attr(
                        approval,
                        "comment",
                        "",
                    ),
                    "Created": _get_attr(
                        approval,
                        "created_at",
                        "",
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Approval records could not be loaded."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:

        if db is not None:
            db.close()