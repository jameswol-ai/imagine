"""
IMAGINE
Project Approvals Streamlit UI.
"""

from __future__ import annotations

from typing import Any

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
    from database.connection import (
        SessionLocal,
    )

    return SessionLocal()


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

    project_id = st.number_input(
        "Project ID",
        min_value=1,
        value=1,
        step=1,
        key="approvals_project_id",
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

        try:

            payload = ApprovalCreate(
                project_id=int(
                    project_id
                ),
                approver_id=int(
                    approver_id
                ),
                comment=(
                    comment.strip()
                    or None
                ),
            )

            db = _session()

            try:

                create_approval(
                    db=db,
                    project_id=payload.project_id,
                    approver_id=payload.approver_id,
                    comment=payload.comment,
                )

            except Exception:

                db.rollback()
                raise

            finally:

                db.close()

            st.success(
                "Approval created successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                "Approval could not be created."
            )

            with st.expander(
                "Complete error",
                expanded=True,
            ):
                st.exception(exc)

    st.divider()

    db = None

    try:

        db = _session()

        approvals = list_approvals(
            db=db,
            project_id=int(
                project_id
            ),
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