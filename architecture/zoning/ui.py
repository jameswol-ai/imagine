from __future__ import annotations

import asyncio
from uuid import UUID

import pandas as pd
import streamlit as st

from database.connection import AsyncSessionLocal

from .models import ZoningStatus, ZoningUse
from .schemas import ZoningRuleCreate, ZoningRuleUpdate
from .service import (
    ZoningConflictError,
    ZoningNotFoundError,
    ZoningService,
)


def _run(coro):
    return asyncio.run(coro)


def _with_db(operation):
    async def runner():
        async with AsyncSessionLocal() as db:
            return await operation(db)

    return _run(runner())


def _list_rules(project_id: UUID | None = None):
    return _with_db(
        lambda db: ZoningService.list(
            db,
            project_id=project_id,
            limit=500,
        )
    )


def _create_rule(payload: ZoningRuleCreate):
    return _with_db(
        lambda db: ZoningService.create(db, payload)
    )


def _update_rule(
    zoning_id: UUID,
    payload: ZoningRuleUpdate,
):
    return _with_db(
        lambda db: ZoningService.update(
            db,
            zoning_id,
            payload,
        )
    )


def _delete_rule(zoning_id: UUID):
    return _with_db(
        lambda db: ZoningService.delete(
            db,
            zoning_id,
        )
    )


def render_zoning():
    """Render the production Zoning tab while preserving the existing UI."""
    st.subheader("Zoning & Land Use")

    try:
        rules = _list_rules()
    except Exception as exc:
        st.error(f"Unable to load zoning rules: {exc}")
        return

    if rules:
        rows = [
            {
                "ID": str(rule.id),
                "Code": rule.code,
                "Zone": rule.name,
                "Allowed Use": (
                    rule.allowed_use.value
                    .replace("_", " ")
                    .title()
                ),
                "Max Height (m)": rule.max_height_m,
                "Coverage (%)": rule.site_coverage_pct,
                "Setback (m)": rule.setback_m,
                "FAR": rule.far,
                "Status": rule.status.value.title(),
            }
            for rule in rules
        ]

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No zoning rules found. Add the first rule below."
        )

    with st.expander(
        "➕ Add Zoning Rule",
        expanded=not bool(rules),
    ):
        with st.form(
            "zoning_create_form",
            clear_on_submit=True,
        ):
            c1, c2, c3 = st.columns(3)

            code = c1.text_input(
                "Zone Code",
                placeholder="RES-01",
            )

            name = c2.text_input(
                "Zone Name",
                placeholder="Residential",
            )

            allowed_use = c3.selectbox(
                "Allowed Use",
                list(ZoningUse),
                format_func=lambda item: (
                    item.value.replace("_", " ").title()
                ),
            )

            c4, c5, c6, c7 = st.columns(4)

            max_height = c4.number_input(
                "Max Height (m)",
                min_value=0.0,
                value=15.0,
            )

            coverage = c5.number_input(
                "Coverage (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
            )

            setback = c6.number_input(
                "Setback (m)",
                min_value=0.0,
                value=3.0,
            )

            far = c7.number_input(
                "FAR",
                min_value=0.0,
                value=1.5,
            )

            description = st.text_area(
                "Description"
            )

            submitted = st.form_submit_button(
                "Create Zoning Rule",
                type="primary",
            )

            if submitted:
                if not code.strip() or not name.strip():
                    st.error(
                        "Zone code and zone name are required."
                    )
                else:
                    try:
                        _create_rule(
                            ZoningRuleCreate(
                                code=code.strip().upper(),
                                name=name.strip(),
                                description=(
                                    description.strip()
                                    or None
                                ),
                                allowed_use=allowed_use,
                                max_height_m=max_height,
                                site_coverage_pct=coverage,
                                setback_m=setback,
                                far=far,
                            )
                        )

                        st.success(
                            "Zoning rule created."
                        )
                        st.rerun()

                    except ZoningConflictError as exc:
                        st.error(str(exc))

                    except Exception as exc:
                        st.error(
                            f"Unable to create zoning rule: {exc}"
                        )

    if not rules:
        return

    st.subheader("Manage Zoning Rules")

    labels = {
        f"{rule.code} · {rule.name}": rule
        for rule in rules
    }

    selected_label = st.selectbox(
        "Select rule",
        list(labels),
        key="zoning_selected_rule",
    )

    selected = labels[selected_label]

    with st.form("zoning_edit_form"):
        c1, c2 = st.columns(2)

        edit_name = c1.text_input(
            "Zone Name",
            value=selected.name,
        )

        edit_code = c2.text_input(
            "Zone Code",
            value=selected.code,
        )

        edit_use = st.selectbox(
            "Allowed Use",
            list(ZoningUse),
            index=list(ZoningUse).index(
                selected.allowed_use
            ),
            format_func=lambda item: (
                item.value.replace("_", " ").title()
            ),
        )

        c1, c2, c3, c4 = st.columns(4)

        edit_height = c1.number_input(
            "Max Height (m)",
            min_value=0.0,
            value=float(selected.max_height_m),
        )

        edit_coverage = c2.number_input(
            "Coverage (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(selected.site_coverage_pct),
        )

        edit_setback = c3.number_input(
            "Setback (m)",
            min_value=0.0,
            value=float(selected.setback_m),
        )

        edit_far = c4.number_input(
            "FAR",
            min_value=0.0,
            value=float(selected.far),
        )

        edit_status = st.selectbox(
            "Status",
            list(ZoningStatus),
            index=list(ZoningStatus).index(
                selected.status
            ),
            format_func=lambda item: item.value.title(),
        )

        edit_description = st.text_area(
            "Description",
            value=selected.description or "",
        )

        save, delete = st.columns(2)

        save_clicked = save.form_submit_button(
            "Save Changes",
            type="primary",
        )

        delete_clicked = delete.form_submit_button(
            "Delete Rule"
        )

    if save_clicked:
        try:
            _update_rule(
                selected.id,
                ZoningRuleUpdate(
                    code=edit_code.strip().upper(),
                    name=edit_name.strip(),
                    allowed_use=edit_use,
                    status=edit_status,
                    max_height_m=edit_height,
                    site_coverage_pct=edit_coverage,
                    setback_m=edit_setback,
                    far=edit_far,
                    description=(
                        edit_description.strip()
                        or None
                    ),
                ),
            )

            st.success("Zoning rule updated.")
            st.rerun()

        except (
            ZoningNotFoundError,
            ZoningConflictError,
        ) as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                f"Unable to update zoning rule: {exc}"
            )

    if delete_clicked:
        try:
            _delete_rule(selected.id)

            st.success("Zoning rule deleted.")
            st.rerun()

        except ZoningNotFoundError as exc:
            st.error(str(exc))

        except Exception as exc:
            st.error(
                f"Unable to delete zoning rule: {exc}"
            )
