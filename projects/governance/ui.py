"""
IMAGINE Project Governance Streamlit UI.
"""

from __future__ import annotations

import streamlit as st


def render_governance() -> None:

    st.title("Governance")

    st.caption(
        "Project governance rules and controls."
    )

    try:

        from projects.governance.schemas import (
            GovernanceCreate,
        )

        from projects.governance.service import (
            create_rule,
            list_rules,
        )

        from database.connection import (
            SessionLocal,
        )

    except Exception as exc:

        st.error(
            "Governance could not be loaded."
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
        key="governance_project_id",
    )

    with st.form("governance_form"):

        rule_name = st.text_input(
            "Rule Name"
        )

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "Create Governance Rule",
            use_container_width=True,
        )

    if submitted:

        if not rule_name.strip():

            st.error(
                "Rule name is required."
            )

        else:

            db = SessionLocal()

            try:

                payload = GovernanceCreate(
                    project_id=int(project_id),
                    rule_name=rule_name.strip(),
                    description=(
                        description.strip()
                        or None
                    ),
                )

                create_rule(
                    db=db,
                    project_id=payload.project_id,
                    rule_name=payload.rule_name,
                    description=payload.description,
                )

                st.success(
                    "Governance rule created."
                )

                st.rerun()

            except Exception as exc:

                db.rollback()

                st.error(
                    "Governance rule could not be created."
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

        rules = list_rules(
            db=db,
            project_id=int(project_id),
        )

        st.dataframe(
            [
                {
                    "ID": rule.id,
                    "Project": rule.project_id,
                    "Rule": rule.rule_name,
                    "Description": rule.description,
                    "Status": rule.status,
                }
                for rule in rules
            ],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:

        st.error(
            "Governance rules could not be listed."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:
        db.close()