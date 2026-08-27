"""
IMAGINE
Project Revisions Streamlit UI.
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


def render_revisions() -> None:

    st.title(
        "Revisions"
    )

    st.caption(
        "Project revision history."
    )

    try:

        from projects.revisions.schemas import (
            RevisionCreate,
        )

        from projects.revisions.service import (
            create_revision,
            list_revisions,
        )

    except Exception as exc:

        st.error(
            "Revisions could not be loaded."
        )

        with st.expander(
            "Complete import traceback",
            expanded=True,
        ):
            st.exception(exc)

        return

    project_id_text = st.text_input(
        "Project ID",
        key="revisions_project_id",
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
        "Create Revision"
    )

    with st.form(
        "revisions_create_form"
    ):

        description = st.text_area(
            "Revision Description"
        )

        created_by = st.number_input(
            "Created By User ID",
            min_value=1,
            value=1,
            step=1,
        )

        submitted = st.form_submit_button(
            "Create Revision",
            use_container_width=True,
        )

    if submitted:

        if project_id is None:

            st.error(
                "A valid Project UUID is required."
            )

        elif not description.strip():

            st.error(
                "Revision description is required."
            )

        else:

            db = None

            try:

                payload = RevisionCreate(
                    project_id=project_id,
                    description=description.strip(),
                    created_by=int(
                        created_by
                    ),
                )

                db = _session()

                create_revision(
                    db=db,
                    project_id=payload.project_id,
                    description=payload.description,
                    created_by=payload.created_by,
                )

                st.success(
                    "Revision created successfully."
                )

                st.rerun()

            except Exception as exc:

                if db is not None:
                    db.rollback()

                st.error(
                    "Revision could not be created."
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
            "Enter a valid Project UUID to load revision records."
        )

        return

    db = None

    try:

        db = _session()

        revisions = list_revisions(
            db=db,
            project_id=project_id,
        )

        revisions = list(
            revisions or []
        )

        st.subheader(
            "Revision Records"
        )

        if not revisions:

            st.info(
                "No revisions exist for this project."
            )

            return

        rows = []

        for revision in revisions:

            rows.append(
                {
                    "ID": _get_attr(
                        revision,
                        "id",
                    ),
                    "Project ID": _get_attr(
                        revision,
                        "project_id",
                    ),
                    "Description": _get_attr(
                        revision,
                        "description",
                        "",
                    ),
                    "Created By": _get_attr(
                        revision,
                        "created_by",
                    ),
                    "Created": _get_attr(
                        revision,
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
            "Revision records could not be loaded."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:

        if db is not None:
            db.close()