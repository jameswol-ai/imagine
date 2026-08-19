"""
IMAGINE
Project Governance Streamlit UI.
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


def render_governance() -> None:

    st.title(
        "Governance"
    )

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
        value=1,
        step=1,
        key="governance_project_id",
    )

    st.subheader(
        "Create Governance Rule"
    )

    with st.form(
        "governance_create_form"
    ):

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

            db = None

            try:

                payload = GovernanceCreate(
                    project_id=int(
                        project_id
                    ),
                    rule_name=rule_name.strip(),
                    description=(
                        description.strip()
                        or None
                    ),
                )

                db = _session()

                create_rule(
                    db=db,
                    project_id=payload.project_id,
                    rule_name=payload.rule_name,
                    description=payload.description,
                )

                st.success(
                    "Governance rule created successfully."
                )

                st.rerun()

            except Exception as exc:

                if db is not None:

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

                if db is not None:

                    db.close()

    st.divider()

    db = None

    try:

        db = _session()

        rules = list_rules(
            db=db,
            project_id=int(
                project_id
            ),
        )

        rules = list(
            rules or []
        )

        st.subheader(
            "Governance Rules"
        )

        if not rules:

            st.info(
                "No governance rules exist for this project."
            )

            return

        rows = []

        for rule in rules:

            rows.append(
                {
                    "ID": _get_attr(
                        rule,
                        "id",
                    ),
                    "Project ID": _get_attr(
                        rule,
                        "project_id",
                    ),
                    "Rule Name": _get_attr(
                        rule,
                        "rule_name",
                        "",
                    ),
                    "Description": _get_attr(
                        rule,
                        "description",
                        "",
                    ),
                    "Status": _status_value(
                        _get_attr(
                            rule,
                            "status",
                        )
                    ),
                    "Created": _get_attr(
                        rule,
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
            "Governance rules could not be loaded."
        )

        with st.expander(
            "Complete error",
            expanded=True,
        ):
            st.exception(exc)

    finally:

        if db is not None:

            db.close()