"""
IMAGINE Project Revisions Streamlit UI.
"""

from __future__ import annotations

import streamlit as st


def render_revisions() -> None:

    st.title("Revisions")

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

        from database.connection import (
            SessionLocal,
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

    project_id = st.number_input(
        "Project ID",
        min_value=1,
        step=1,
        key="revision_project_id",
    )

    with st.form("revision_form"):

        description = st.text_area(
            "Revision Description"
        )

        created_by = st.number_input(
            "Created By",
            min_value=1,
            step=1,
        )

        submitted = st.form_submit_button(
            "Create Revision",
            use_container_width=True,
        )

    if submitted:

        if not description.strip():

            st.error(
                "Revision description is required."
            )

        else:

            db = SessionLocal()

            try:

                payload = RevisionCreate(
                    project_id=int(project_id),
                    description=description.strip(),
                    created_by=int(created_by),
                )

                create_revision(
                    db=db,
                    project_id=payload.project_id,
                    description=payload.description,
                    created_by=payload.created_by,
                )

                st.success(
                    "Revision created."
                )

                st.rerun()

            except Exception as exc:

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
                db.close()

    st.divider()

    db = SessionLocal()

    try:

        revisions = list_revisions(
            db=db,
            project_id=int(project_id),
        )

        st.dataframe(
            [
                {
                    "ID": revision.id,
                    "Project": revision.project_id,
                    "Description": revision.description,
                    "Created By": revision.created_by,
                }
                for revision in revisions
            ],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Revisions could not be listed."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:
        db.close()