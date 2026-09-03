"""IMAGINE AEC Engine Streamlit application shell.

The shell owns navigation, presentation, diagnostics and safe lazy loading.
Domain modules own engineering calculations, persistence and domain-specific UI.
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path
from typing import Callable

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.enterprise_registry import MODULE_SPECS, ModuleSpec, validate_registry

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(
    page_title="IMAGINE | AEC Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DOMAIN_DESCRIPTIONS = {
    "PLATFORM": "Enterprise workspace and runtime diagnostics.",
    "PROJECTS": "Project lifecycle, approvals, revisions, workflows and governance.",
    "ARCHITECTURE": "Briefs, standards, site planning, programming, compliance and generative design.",
    "STRUCTURAL": "Analysis, concrete, steel, timber, foundations, retaining walls and Eurocodes.",
    "BIM": "Buildings, storeys, spaces, elements and OpenBIM workflows.",
    "MEP": "Mechanical, electrical, plumbing and energy engineering.",
    "COSTING": "BOQ, quantity takeoff, procurement, currency, escalation and risk.",
    "CONSTRUCTION": "Planning, scheduling, RFIs, submittals, snagging and site management.",
    "DOCUMENTS": "Drawings, specifications, contracts, revisions and transmittals.",
    "AI": "Architecture, engineering, MEP, QS and project-management assistants.",
    "ANALYTICS": "Dashboards, KPIs, portfolio intelligence, forecasting and reporting.",
    "REGIONAL": "Regional codes, regulations and zoning requirements.",
    "INTEGRATIONS": "AEC software, GIS, cloud and interoperability integrations.",
    "DIGITAL TWIN": "Assets, sensors, telemetry, maintenance and predictive intelligence.",
}


def registry_snapshot() -> tuple[ModuleSpec, ...]:
    validate_registry()
    return MODULE_SPECS


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "module_search": "",
        "module_search_domain": "All domains",
        "last_route_load_ms": None,
        "recent_routes": [],
        "show_diagnostics": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(135deg, #f7f9fc 0%, #eef3f8 52%, #f8fafc 100%); }
        .block-container { max-width: 1600px; padding-top: 1.1rem; padding-bottom: 3rem; }
        .imagine-brand { padding: .25rem .15rem .8rem; }
        .imagine-brand-title { font-size: 1.8rem; font-weight: 900; letter-spacing: -.06em; }
        .imagine-brand-subtitle { margin-top: .25rem; color: #687588; font-size: .74rem; line-height: 1.45; }
        .imagine-label { margin: .75rem 0 .35rem; color: #687588; font-size: .64rem; font-weight: 850; letter-spacing: .12em; text-transform: uppercase; }
        .imagine-header { padding: 1.35rem 1.45rem; margin-bottom: 1.15rem; border: 1px solid rgba(120,135,155,.18); border-radius: 18px; background: rgba(255,255,255,.76); box-shadow: 0 16px 40px rgba(35,55,80,.08); animation: imagine-enter .55s ease-out both; }
        .imagine-header-title { margin: 0; font-size: 2.35rem; line-height: 1; font-weight: 900; letter-spacing: -.055em; }
        .imagine-header-subtitle { margin-top: .45rem; color: #687588; font-size: .92rem; }
        .imagine-breadcrumb { display: inline-block; margin-top: .75rem; padding: .34rem .62rem; border: 1px solid #dce3eb; border-radius: 999px; background: #f3f6f9; color: #566276; font-size: .69rem; }
        .imagine-hero { padding: 1.7rem; margin-bottom: 1rem; border-radius: 20px; background: linear-gradient(135deg, rgba(255,255,255,.94), rgba(238,244,250,.86)); border: 1px solid rgba(120,135,155,.17); box-shadow: 0 18px 55px rgba(35,55,80,.09); animation: imagine-float 6s ease-in-out infinite; }
        .imagine-hero-title { font-size: 1.55rem; font-weight: 850; letter-spacing: -.035em; }
        .imagine-hero-copy { margin-top: .45rem; color: #647184; line-height: 1.6; }
        .imagine-card { min-height: 118px; padding: 1rem 1.05rem; border: 1px solid rgba(120,135,155,.17); border-radius: 16px; background: rgba(255,255,255,.84); box-shadow: 0 10px 30px rgba(35,55,80,.055); animation: imagine-rise .55s ease-out both; }
        .imagine-card-title { color: #687588; font-size: .63rem; font-weight: 850; letter-spacing: .09em; text-transform: uppercase; }
        .imagine-card-value { margin-top: .4rem; font-size: 1.55rem; font-weight: 900; }
        .imagine-card-description { margin-top: .2rem; color: #7a8697; font-size: .71rem; }
        .imagine-panel { padding: 1.2rem 1.3rem; border: 1px solid rgba(120,135,155,.17); border-radius: 16px; background: rgba(255,255,255,.78); box-shadow: 0 10px 30px rgba(35,55,80,.045); }
        .imagine-panel-title { font-size: 1.08rem; font-weight: 800; }
        .imagine-panel-description { margin-top: .3rem; color: #687588; font-size: .82rem; line-height: 1.6; }
        .imagine-footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid rgba(120,135,155,.2); color: #8792a1; font-size: .68rem; }
        div.stButton > button { min-height: 2.35rem; border-radius: 10px; font-weight: 680; transition: transform .16s ease, box-shadow .16s ease; }
        div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 7px 18px rgba(35,55,80,.12); }
        @keyframes imagine-enter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes imagine-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes imagine-float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-2px); } }
        @media (prefers-color-scheme: dark) {
            .stApp { background: radial-gradient(circle at top right, #172231 0%, #0b1118 55%, #0b1118 100%); }
            .imagine-header, .imagine-hero, .imagine-card, .imagine-panel { background: rgba(19,28,39,.82); border-color: #293746; }
            .imagine-brand-title, .imagine-header-title, .imagine-hero-title, .imagine-card-value, .imagine-panel-title { color: #f1f5f9; }
            .imagine-brand-subtitle, .imagine-header-subtitle, .imagine-hero-copy, .imagine-panel-description, .imagine-card-description { color: #aab5c3; }
            .imagine-breadcrumb { background: #17212c; border-color: #2b3948; color: #b9c4d1; }
            .imagine-label, .imagine-card-title { color: #aab5c3; }
            .imagine-footer { border-top-color: #293746; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def spec_for_route(route: str) -> ModuleSpec | None:
    return next((spec for spec in registry_snapshot() if spec.route == route), None)


def search_specs(query: str, section: str = "All domains") -> list[ModuleSpec]:
    normalized = query.strip().casefold()
    if not normalized:
        return []
    candidates = registry_snapshot()
    if section != "All domains":
        candidates = tuple(spec for spec in candidates if spec.section == section)
    terms = normalized.split()
    scored: list[tuple[int, ModuleSpec]] = []
    for spec in candidates:
        haystack = " ".join((spec.route, spec.label, spec.section, spec.module_path or "")).casefold()
        if not all(term in haystack for term in terms):
            continue
        score = 10 if spec.implemented else 0
        if spec.label.casefold().startswith(normalized):
            score += 100
        elif normalized in spec.label.casefold():
            score += 50
        if spec.section.casefold() == normalized:
            score += 40
        scored.append((score, spec))
    scored.sort(key=lambda item: (-item[0], item[1].section, item[1].label))
    return [spec for _, spec in scored]


def set_active_route(route: str) -> None:
    spec = spec_for_route(route)
    if spec is None:
        return
    st.session_state.active_route = route
    recent = [r for r in st.session_state.get("recent_routes", []) if r != route]
    st.session_state.recent_routes = [route, *recent][:6]


def load_renderer(spec: ModuleSpec) -> Callable[[], object]:
    if not spec.module_path or spec.module_path == "__builtin__":
        raise AttributeError(f"No external renderer is configured for {spec.route}.")
    module = importlib.import_module(spec.module_path)
    renderer = getattr(module, spec.renderer_name, None)
    if not callable(renderer):
        renderer = getattr(module, "render", None)
    if not callable(renderer):
        raise AttributeError(f"Module '{spec.module_path}' does not expose a callable renderer.")
    return renderer


def probe_renderers() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in registry_snapshot():
        if not spec.implemented or not spec.module_path or spec.module_path == "__builtin__":
            continue
        try:
            module = importlib.import_module(spec.module_path)
            renderer = getattr(module, spec.renderer_name, None)
            if not callable(renderer):
                renderer = getattr(module, "render", None)
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Ready" if callable(renderer) else "Missing renderer", "Detail": "Callable renderer found" if callable(renderer) else f"Expected {spec.renderer_name}"})
        except Exception as exc:
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Import error", "Detail": f"{type(exc).__name__}: {exc}"})
    return rows


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand"><div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div></div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="imagine-label">Workspace search</div>', unsafe_allow_html=True)
        st.text_input("Search modules", key="module_search", placeholder="Try beam, zoning, BIM, project...", label_visibility="collapsed")
        st.selectbox("Search domain", ["All domains", *DOMAIN_DESCRIPTIONS.keys()], key="module_search_domain", label_visibility="collapsed")

        query = st.session_state.module_search.strip()
        matches = search_specs(query, st.session_state.module_search_domain) if query else []
        if query:
            st.caption(f"{len(matches)} workspace(s) found")
            for spec in matches[:20]:
                label = f"{spec.label} · {'Ready' if spec.implemented else 'Registered'}"
                if st.button(label, key=f"search_{spec.route}", use_container_width=True, disabled=not spec.implemented):
                    set_active_route(spec.route)
                    st.rerun()
            if len(matches) > 20:
                st.caption(f"Showing 20 of {len(matches)} results. Refine the search.")
        else:
            st.info("Search is the primary module navigation. Type a workspace name, discipline or function above.")

        st.divider()
        recent = [r for r in st.session_state.get("recent_routes", []) if spec_for_route(r)]
        if recent:
            st.markdown('<div class="imagine-label">Recent workspaces</div>', unsafe_allow_html=True)
            for route in recent:
                spec = spec_for_route(route)
                if spec and st.button(spec.label, key=f"recent_{route}", use_container_width=True):
                    set_active_route(route)
                    st.rerun()
        st.divider()
        if st.button("Overview", use_container_width=True):
            set_active_route("Overview")
            st.rerun()
        if st.button("System Health", use_container_width=True):
            set_active_route("System Health")
            st.rerun()
        st.caption("All registered modules remain discoverable through search. Unready modules are intentionally hidden from direct execution until their renderer is connected.")


def render_header(title: str, subtitle: str, breadcrumb: str) -> None:
    st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{title}</div><div class="imagine-header-subtitle">{subtitle}</div><div class="imagine-breadcrumb">{breadcrumb}</div></div>', unsafe_allow_html=True)


def get_project_summary() -> tuple[list[object], str]:
    try:
        from database.bootstrap import database_health
        from database.connection import SessionLocal
        health = database_health()
        if not health.get("ok"):
            return [], "Unavailable"
        from projects.projects.service import ProjectService
        with SessionLocal() as db:
            return ProjectService.get_all_sync(db=db, skip=0, limit=10000), "Connected"
    except Exception:
        return [], "Unavailable"


def render_overview() -> None:
    render_header("IMAGINE", "Integrated Architecture, Engineering & Construction Engine", "Overview / Enterprise Workspace")
    specs = registry_snapshot()
    projects, database_status = get_project_summary()
    ready = sum(spec.implemented for spec in specs)
    coverage = round(ready / len(specs) * 100, 1) if specs else 0

    st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">Design. Engineer. Build. Operate.</div><div class="imagine-hero-copy">A unified AEC workspace for project delivery, engineering decision support, BIM coordination, cost control, construction management and operational intelligence. Use the search panel to move directly to the workspace you need.</div></div>', unsafe_allow_html=True)

    cards = [
        ("Workspaces", len(specs), "Enterprise registry"),
        ("Ready", ready, f"{coverage}% registry coverage"),
        ("Projects", len(projects), "Database records"),
        ("Database", database_status, "Runtime connectivity"),
    ]
    cols = st.columns(4)
    for index, (title, value, description) in enumerate(cards):
        with cols[index]:
            st.markdown(f'<div class="imagine-card" style="animation-delay:{index * 70}ms"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{description}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Portfolio Snapshot")
        if projects:
            rows = []
            for project in projects[:25]:
                status = project.status.value if hasattr(project.status, "value") else str(project.status)
                rows.append({"Project": getattr(project, "name", "Unnamed project"), "Status": status})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No database project records are currently available.")
    with right:
        st.subheader("Platform Coverage")
        domain_rows = []
        for section in DOMAIN_DESCRIPTIONS:
            domain_specs = [x for x in specs if x.section == section]
            ready_count = sum(x.implemented for x in domain_specs)
            domain_rows.append({"Domain": section, "Ready": ready_count, "Registered": len(domain_specs)})
        df = pd.DataFrame(domain_rows)
        fig = px.bar(df, x="Domain", y=["Ready", "Registered"], barmode="group", height=390)
        fig.update_layout(margin=dict(l=10, r=10, t=15, b=95), legend_title_text="", xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recommended Starting Points")
    quick_routes = ["Projects", "Architecture Assistant", "Design Standards", "Beam Design", "Roof Design", "Structural Analysis", "Buildings", "Integrated MEP Analysis", "BOQ", "Planning", "Drawing Management", "Dashboards"]
    quick_cols = st.columns(4)
    for index, route in enumerate(quick_routes):
        spec = spec_for_route(route)
        if spec is None or not spec.implemented:
            continue
        with quick_cols[index % 4]:
            if st.button(spec.label, key=f"overview_{route}", use_container_width=True):
                set_active_route(route)
                st.rerun()


def render_system_health() -> None:
    render_header("System Health", "Registry validation, renderer probing and database diagnostics", "Platform / System Health")
    try:
        validate_registry()
        registry_status = "Healthy"
        registry_error = ""
    except Exception as exc:
        registry_status = "Failed"
        registry_error = f"{type(exc).__name__}: {exc}"

    try:
        from database.bootstrap import database_health
        db_health = database_health()
    except Exception as exc:
        db_health = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    specs = registry_snapshot()
    a, b, c, d = st.columns(4)
    a.metric("Registered", len(specs))
    b.metric("Marked Ready", sum(x.implemented for x in specs))
    c.metric("Registry", registry_status)
    d.metric("Database", "Connected" if db_health.get("ok") else "Unavailable")

    if registry_error:
        st.error(registry_error)
    if db_health.get("ok"):
        st.success("Database connectivity check passed.")
    else:
        st.warning(db_health.get("error", "Database connectivity check failed."))

    st.subheader("Renderer Health")
    with st.spinner("Checking registered renderers..."):
        rows = probe_renderers()
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No external implemented renderers were available to probe.")
        return
    counts = df["Status"].value_counts().to_dict()
    st.caption(" · ".join(f"{key}: {value}" for key, value in counts.items()))
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(spec.label, f"{spec.section} workspace", f"{spec.section} / {spec.label}")
    st.info("This workspace is registered but not enabled for execution yet. It remains searchable while its renderer is being connected.")


def render_selected_module(route: str) -> None:
    spec = spec_for_route(route)
    if spec is None:
        set_active_route("Overview")
        render_overview()
        return
    if route == "Overview":
        render_overview()
        return
    if route == "System Health":
        render_system_health()
        return
    if not spec.implemented or not spec.module_path:
        render_placeholder(spec)
        return

    render_header(spec.label, f"IMAGINE {spec.section.title()} Workspace", f"{spec.section} / {spec.label}")
    started = time.perf_counter()
    try:
        renderer = load_renderer(spec)
        renderer()
        st.session_state.last_route_load_ms = round((time.perf_counter() - started) * 1000, 1)
    except Exception as exc:
        st.error(f"{spec.label} could not be loaded safely. The navigation shell remains available.")
        with st.expander("Technical details", expanded=False):
            st.code(f"Domain: {spec.section}\nModule: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)


def render_footer() -> None:
    load_ms = st.session_state.get("last_route_load_ms")
    timing = f" · last workspace load {load_ms} ms" if load_ms is not None else ""
    st.markdown(f'<div class="imagine-footer">IMAGINE AEC Engine · Search-driven enterprise workspace{timing}</div>', unsafe_allow_html=True)


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_selected_module(st.session_state.active_route)
    render_footer()


if __name__ == "__main__":
    main()
