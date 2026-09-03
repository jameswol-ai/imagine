"""Preliminary railing, balustrade and guard screening workspace."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def calculate_railing(length_m: float, height_mm: float, post_spacing_m: float, line_load_kn_m: float, point_load_kn: float, rail_size_mm: float) -> dict[str, float]:
    posts = max(2, int(length_m / max(post_spacing_m, 0.1)) + 1)
    tributary = min(post_spacing_m, length_m)
    post_shear = line_load_kn_m * tributary
    rail_moment = line_load_kn_m * tributary**2 / 8
    post_moment = max(line_load_kn_m * tributary**2 / 8, point_load_kn * max(post_spacing_m, 0.1) / 4)
    return {"length_m": length_m, "height_mm": height_mm, "post_spacing_m": post_spacing_m, "posts": float(posts), "line_load_kn_m": line_load_kn_m, "point_load_kn": point_load_kn, "post_shear_kn": post_shear, "rail_moment_knm": rail_moment, "post_moment_knm": post_moment, "rail_size_mm": rail_size_mm}


def render() -> None:
    st.subheader("Railings & Balustrades Design")
    st.caption("Preliminary guard, balustrade and handrail geometry and load-path screening. Adopt the governing occupancy and local safety requirements for final design.")
    c1, c2, c3 = st.columns(3)
    with c1:
        length = st.number_input("Railing length (m)", min_value=0.5, value=4.0, step=0.1)
        height = st.number_input("Guard height (mm)", min_value=600.0, value=1100.0, step=25.0)
    with c2:
        spacing = st.number_input("Post spacing (m)", min_value=0.2, value=1.2, step=0.1)
        line = st.number_input("Horizontal line load (kN/m)", min_value=0.0, value=0.74, step=0.05)
    with c3:
        point = st.number_input("Horizontal point load (kN)", min_value=0.0, value=1.0, step=0.1)
        rail = st.number_input("Indicative rail diameter/size (mm)", min_value=10.0, value=50.0, step=5.0)
    if st.button("Assess railing scheme", type="primary"):
        st.session_state["railings_design_result"] = calculate_railing(length, height, spacing, line, point, rail)
    result = st.session_state.get("railings_design_result")
    if not result:
        return
    a, b, c, d = st.columns(4)
    a.metric("Guard height", f'{result["height_mm"]:.0f} mm')
    b.metric("Posts", int(result["posts"]))
    c.metric("Post moment", f'{result["post_moment_knm"]:.2f} kNm')
    d.metric("Rail moment", f'{result["rail_moment_knm"]:.2f} kNm')
    tabs = st.tabs(["Elevation", "Actions", "Checklist"])
    with tabs[0]:
        x = [0, length]
        y = [0, 0]
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines"))
        fig.add_hline(y=height/1000, line_width=3)
        for i in range(int(result["posts"])):
            px = min(length, i * spacing)
            fig.add_shape(type="line", x0=px, y0=0, x1=px, y1=height/1000)
        fig.update_layout(height=350, xaxis_title="Length (m)", yaxis_title="Height (m)", title="Conceptual railing elevation")
        st.plotly_chart(fig, use_container_width=True)
    with tabs[1]:
        st.dataframe(pd.DataFrame([{"Action": "Horizontal line load", "Value": result["line_load_kn_m"], "Unit": "kN/m"}, {"Action": "Horizontal point load", "Value": result["point_load_kn"], "Unit": "kN"}, {"Action": "Indicative rail moment", "Value": result["rail_moment_knm"], "Unit": "kNm"}, {"Action": "Indicative post moment", "Value": result["post_moment_knm"], "Unit": "kNm"}]), use_container_width=True, hide_index=True)
    with tabs[2]:
        items = ["Guard/handrail height", "Infill opening limits", "Horizontal imposed actions", "Post/base-plate capacity", "Anchorage and substrate", "Edge distance", "Corrosion/environment", "Fire and material compatibility", "Accessibility and handrail continuity"]
        st.dataframe(pd.DataFrame({"Check": items, "Status": ["Review"] * len(items)}), use_container_width=True, hide_index=True)
    st.warning("Preliminary only. Verify loads, infill, impact, deflection, connections, anchors, edge conditions, corrosion and dimensional safety requirements against the adopted code and occupancy classification.")


__all__ = ["calculate_railing", "render"]
