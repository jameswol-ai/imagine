"""
IMAGINE Platform — Bill of Quantities (BOQ) & Cost Estimation Engine
Path: modules/costing/boq.py
App: imagine
"""

import pandas as pd
import plotly.express as px
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "boq_items"


def render() -> None:
    """Renders the real-time Bill of Quantities management module."""
    st.title("💰 Bill of Quantities (BOQ) & Cost Estimation")
    st.caption("Real-time cost breakdown, rate management, and material quantity tracking.")

    # Ensure demo seed records exist if key is empty
    items = CRUDService.get_all(STATE_KEY)
    if not items:
        _initialize_demo_data()
        items = CRUDService.get_all(STATE_KEY)

    # Convert session state records into DataFrame for analytics
    df_boq = pd.DataFrame(items) if items else pd.DataFrame(columns=[
        "id", "code", "description", "category", "quantity", "unit", "unit_rate_eur", "total_cost_eur"
    ])

    if not df_boq.empty and "quantity" in df_boq.columns and "unit_rate_eur" in df_boq.columns:
        df_boq["total_cost_eur"] = df_boq["quantity"] * df_boq["unit_rate_eur"]

    tab_overview, tab_manage, tab_analytics = st.tabs([
        "📊 Summary & BOQ Table",
        "➕ Add / Manage Items",
        "📈 Cost Analytics & Pareto"
    ])

    # ==============================================================================
    # TAB 1: SUMMARY & DATA TABLE
    # ==============================================================================
    with tab_overview:
        m1, m2, m3, m4 = st.columns(4)
        total_val = df_boq["total_cost_eur"].sum() if not df_boq.empty else 0.0
        total_items = len(df_boq)
        categories_count = df_boq["category"].nunique() if not df_boq.empty else 0
        avg_item_val = total_val / total_items if total_items > 0 else 0.0

        m1.metric("Total BOQ Value", f"€{total_val:,.2f}")
        m2.metric("Line Items", f"{total_items}")
        m3.metric("Cost Categories", f"{categories_count}")
        m4.metric("Avg. Item Cost", f"€{avg_item_val:,.2f}")

        st.divider()

        if not df_boq.empty:
            col_filt, col_search = st.columns([1, 2])
            with col_filt:
                all_cats = ["All"] + list(df_boq["category"].unique())
                selected_cat = st.selectbox("Filter by Category", all_cats)
            with col_search:
                search_query = st.text_input("Search Code or Description", "")

            filtered_df = df_boq.copy()
            if selected_cat != "All":
                filtered_df = filtered_df[filtered_df["category"] == selected_cat]
            if search_query:
                filtered_df = filtered_df[
                    filtered_df["description"].str.contains(search_query, case=False, na=False) |
                    filtered_df["code"].str.contains(search_query, case=False, na=False)
                ]

            st.dataframe(
                filtered_df,
                column_config={
                    "id": "ID",
                    "code": "Item Code",
                    "description": "Description",
                    "category": "Category",
                    "quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                    "unit": "Unit",
                    "unit_rate_eur": st.column_config.NumberColumn("Unit Rate (€)", format="€%.2f"),
                    "total_cost_eur": st.column_config.NumberColumn("Total Cost (€)", format="€%.2f"),
                },
                use_container_width=True,
                hide_index=True,
            )

            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export BOQ to CSV",
                data=csv_data,
                file_name="imagine_boq_schedule.csv",
                mime="text/csv",
            )
        else:
            st.info("No BOQ records available.")

    # ==============================================================================
    # TAB 2: ADD / MANAGE ITEMS
    # ==============================================================================
    with tab_manage:
        col_add, col_del = st.columns([2, 1])

        with col_add:
            st.subheader("Add New Line Item")
            with st.form("add_boq_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    code = st.text_input("Item Code", value=f"BOQ-{len(items) + 1:03d}")
                    desc = st.text_input("Description", value="C30/37 Concrete in Foundations")
                    category = st.selectbox("Category", [
                        "Substructure", "Superstructure Concrete", "Structural Steel",
                        "Masonry & Earthworks", "MEP & Services", "Finishes & Joinery"
                    ])
                with c2:
                    qty = st.number_input("Quantity", min_value=0.01, value=150.0, step=10.0)
                    unit = st.selectbox("Unit", ["m³", "m²", "m", "kg", "tonnes", "nr", "ls"])
                    rate = st.number_input("Unit Rate (€)", min_value=0.0, value=145.0, step=5.0)

                submitted = st.form_submit_button("➕ Save Line Item", type="primary")
                if submitted:
                    new_item = {
                        "id": f"ITEM-{len(items) + 1:03d}",
                        "code": code,
                        "description": desc,
                        "category": category,
                        "quantity": float(qty),
                        "unit": unit,
                        "unit_rate_eur": float(rate),
                        "total_cost_eur": float(qty * rate),
                    }
                    CRUDService.create(STATE_KEY, new_item)
                    st.success(f"Added item `{code}` successfully!")
                    st.rerun()

        with col_del:
            st.subheader("Record Management")
            if items:
                item_ids = [it["id"] for it in items]
                selected_del = st.selectbox("Select Item ID to Remove", item_ids)
                if st.button("🗑️ Delete Selected Item"):
                    CRUDService.delete(STATE_KEY, selected_del)
                    st.warning(f"Removed item `{selected_del}`.")
                    st.rerun()

                st.markdown("---")
                if st.button("🧹 Reset to Demo Data"):
                    st.session_state[STATE_KEY] = []
                    _initialize_demo_data()
                    st.rerun()

    # ==============================================================================
    # TAB 3: COST ANALYTICS & PARETO
    # ==============================================================================
    with tab_analytics:
        if not df_boq.empty:
            ca1, ca2 = st.columns(2)

            with ca1:
                st.subheader("Cost Allocation by Category")
                cat_chart = df_boq.groupby("category")["total_cost_eur"].sum().reset_index()
                fig_pie = px.pie(
                    cat_chart,
                    values="total_cost_eur",
                    names="category",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig_pie.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with ca2:
                st.subheader("Top Cost Drivers (Pareto)")
                top_items = df_boq.sort_values(by="total_cost_eur", ascending=False).head(5)
                fig_bar = px.bar(
                    top_items,
                    x="total_cost_eur",
                    y="description",
                    orientation="h",
                    color="category",
                    labels={"total_cost_eur": "Total Cost (€)", "description": "Item Description"},
                )
                fig_bar.update_layout(
                    height=350,
                    yaxis=dict(autorange="reversed"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E0"),
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Insufficient data for cost distribution visualizers.")


def _initialize_demo_data() -> None:
    """Seeds initial Bill of Quantities demo items into session state."""
    demo_items = [
        {
            "id": "ITEM-001",
            "code": "SUB-01",
            "description": "Site Excavation & Bulk Earthworks",
            "category": "Masonry & Earthworks",
            "quantity": 850.0,
            "unit": "m³",
            "unit_rate_eur": 28.50,
            "total_cost_eur": 24225.0,
        },
        {
            "id": "ITEM-002",
            "code": "CONC-01",
            "description": "C30/37 Reinforced Concrete Footings",
            "category": "Substructure",
            "quantity": 320.0,
            "unit": "m³",
            "unit_rate_eur": 165.00,
            "total_cost_eur": 52800.0,
        },
        {
            "id": "ITEM-003",
            "code": "STEEL-01",
            "description": "Structural Steelwork S355 Beams & Columns",
            "category": "Structural Steel",
            "quantity": 42.5,
            "unit": "tonnes",
            "unit_rate_eur": 2400.00,
            "total_cost_eur": 102000.0,
        },
        {
            "id": "ITEM-004",
            "code": "MEP-01",
            "description": "HVAC Chilled Water Piping Network",
            "category": "MEP & Services",
            "quantity": 1.0,
            "unit": "ls",
            "unit_rate_eur": 45000.00,
            "total_cost_eur": 45000.0,
        },
    ]
    st.session_state[STATE_KEY] = demo_items
