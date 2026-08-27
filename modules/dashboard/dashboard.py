"""
IMAGINE Platform — Executive Portfolio Dashboard
Path: modules/dashboard/dashboard.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.utils.crud import CRUDService


def render() -> None:
    """Renders the executive cross-domain portfolio dashboard."""
    st.title("📊 Executive Portfolio Dashboard")
    st.caption(
        "Cross-domain executive summary: Projects, Structural Compliance, Cost Distribution, and Site Operations."
    )

    # Fetch real-time data from session state collections
    projects = CRUDService.get_all("projects")
    structural_calcs = CRUDService.get_all("structural_calcs")
    boq_items = CRUDService.get_all("boq_items")
    rfis = CRUDService.get_all("rfis")
    sensors = CRUDService.get_all("digital_twin_sensors")

    # ==============================================================================
    # 1. EXECUTIVE KPI SUMMARY
    # ==============================================================================
    col1, col2, col3, col4, col5 = st.columns(5)

    total_projects = len(projects)
    active_projects = sum(1 for p in projects if p.get("status") in ["active", "In Design", "Construction"])
    total_budget_m = sum(float(p.get("budget", 0.0)) for p in projects)
    avg_progress = (
        sum(float(p.get("progress_pct", 0.0)) for p in projects) / total_projects
        if total_projects > 0
        else 0.0
    )

    total_calcs = len(structural_calcs)
    passed_calcs = sum(1 for c in structural_calcs if c.get("status") == "Passed")
    safety_rate = (passed_calcs / total_calcs * 100.0) if total_calcs > 0 else 100.0

    open_rfis = sum(1 for r in rfis if r.get("status", "Open") == "Open")
    nominal_sensors = sum(1 for s in sensors if s.get("status") == "Nominal")

    col1.metric("Active Projects", f"{active_projects} / {total_projects}")
    col2.metric("Portfolio Value", f"${total_budget_m:,.1f}M")
    col3.metric("Avg Execution Progress", f"{avg_progress:.1f}%")
    col4.metric("Structural Compliance", f"{safety_rate:.0f}%", delta=f"{passed_calcs}/{total_calcs} Passed")
    col5.metric("Open RFIs / Telemetry", f"{open_rfis} RFIs", delta=f"{nominal_sensors}/{len(sensors)} Sensors OK")

    st.divider()

    # ==============================================================================
    # 2. CHARTS & ANALYTICS DASHBOARD
    # ==============================================================================
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("📈 Project Progress vs. Budget Allocation")
        if projects:
            df_p = pd.DataFrame(projects)
            fig_bar = px.bar(
                df_p,
                x="name",
                y="budget",
                color="progress_pct",
                labels={"name": "Project", "budget": "Budget ($M)", "progress_pct": "Progress (%)"},
                color_continuous_scale="Viridis",
                text_auto=".1f",
            )
            fig_bar.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No active projects found.")

    with c_right:
        st.subheader("🏗️ Structural Unity Check Distribution (Eurocodes)")
        if structural_calcs:
            df_c = pd.DataFrame(structural_calcs)
            fig_gauge = px.scatter(
                df_c,
                x="element_name",
                y="unity_check",
                color="status",
                size=[15] * len(df_c),
                hover_data=["code"],
                color_discrete_map={"Passed": "#48BB78", "Warning": "#ECC94B", "Failed": "#F56565"},
                labels={"unity_check": "Unity Check Ratio (η)", "element_name": "Element"},
            )
            fig_gauge.add_hline(y=1.0, line_dash="dash", line_color="#F56565", annotation_text="Limit State (η = 1.0)")
            fig_gauge.update_layout(
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E0"),
                yaxis=dict(range=[0, 1.2]),
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("No structural calculation checks recorded.")

    st.divider()

    # ==============================================================================
    # 3. DOMAIN SUMMARY & QUICK ACTIVITY LOG
    # ==============================================================================
    tab_calcs, tab_boq, tab_rfis, tab_iot = st.tabs(
        ["🧱 Structural Checks", "💰 Costing & BOQ", "📋 Active RFIs", "📡 Digital Twin Sensors"]
    )

    with tab_calcs:
        if structural_calcs:
            df_calcs = pd.DataFrame(structural_calcs)
            st.dataframe(
                df_calcs[["id", "code", "element_name", "unity_check", "status", "updated_at"]],
                column_config={
                    "unity_check": st.column_config.NumberColumn("Unity Check (η)", format="%.2f"),
                    "status": st.column_config.TextColumn("Status"),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No structural verifications found.")

    with tab_boq:
        if boq_items:
            df_boq = pd.DataFrame(boq_items)
            df_boq["total_cost_eur"] = df_boq["quantity"] * df_boq["unit_rate_eur"]
            st.dataframe(
                df_boq[["id", "code", "description", "quantity", "unit", "unit_rate_eur", "total_cost_eur"]],
                column_config={
                    "unit_rate_eur": st.column_config.NumberColumn("Unit Rate (€)", format="€%.2f"),
                    "total_cost_eur": st.column_config.NumberColumn("Total (€)", format="€%.2f"),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No BOQ records found.")

    with tab_rfis:
        if rfis:
            st.dataframe(pd.DataFrame(rfis), use_container_width=True, hide_index=True)
        else:
            st.caption("No RFIs logged.")

    with tab_iot:
        if sensors:
            st.dataframe(pd.DataFrame(sensors), use_container_width=True, hide_index=True)
        else:
            st.caption("No sensors active.")
