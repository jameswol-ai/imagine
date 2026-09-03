"""IMAGINE AEC Engine Streamlit application shell.

The application shell keeps renderer imports lazy, provides searchable domain
navigation, and gives the enterprise workspace a consistent overview. Heavy
engineering calculations remain inside the dedicated module engines.
"""

from __future__ import annotations

import importlib
import sys
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
    page_title="IMAGINE | Integrated AEC Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DOMAIN_DESCRIPTIONS = {
    "PLATFORM": "Enterprise workspace, registry validation and diagnostics.",
    "PROJECTS": "Project lifecycle, approvals, revisions, workflows and governance.",
    "ARCHITECTURE": "Architecture Assistant, zoning, site planning, floor planning, programming, compliance and generative design.",
    "STRUCTURAL": "Structural analysis, reinforced concrete, steel and Eurocode workflows.",
    "BIM": "Buildings, storeys, spaces, elements and OpenBIM workflows.",
    "MEP": "Mechanical, electrical, plumbing and energy engineering.",
    "COSTING": "BOQ, quantity takeoff, procurement and financial analysis.",
    "CONSTRUCTION": "Planning, scheduling, RFIs, submittals and site management.",
    "DOCUMENTS": "Drawings, specifications, contracts and revision control.",
    "AI": "Architecture, engineering, MEP, QS and project-management AI.",
    "ANALYTICS": "Portfolio analytics, KPIs, forecasting and reporting.",
    "REGIONAL": "Regional codes, regulations and zoning requirements.",
    "INTEGRATIONS": "AEC software, GIS, cloud and interoperability integrations.",
    "DIGITAL TWIN": "Assets, sensors, telemetry, maintenance and predictive AI.",
}

SECTION_ORDER = tuple(DOMAIN_DESCRIPTIONS)


@st.cache_data(show_spinner=False)
def registry_snapshot() -> tuple[ModuleSpec, ...]:
    validate_registry()
    return MODULE_SPECS


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "module_search": "",
        "module_search_domain": "All domains",
        "sidebar_domain": "PLATFORM",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f7fa; }
        .block-container { max-width: 1550px; padding-top: 1.4rem; padding-bottom: 3rem; }
        section[data-testid="stSidebar"] { width: 330px !important; }
        .imagine-brand { padding: .3rem .2rem .8rem; }
        .imagine-brand-title { font-size: 1.65rem; font-weight: 850; letter-spacing: -.045em; }
        .imagine-brand-subtitle { margin-top: .25rem; color: #697587; font-size: .76rem; line-height: 1.4; }
        .imagine-label { margin: .75rem 0 .35rem; color: #697587; font-size: .67rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
        .imagine-header { margin-bottom: 1rem; }
        .imagine-header-title { margin: 0; font-size: 2.15rem; line-height: 1.05; font-weight: 850; letter-spacing: -.045em; }
        .imagine-header-subtitle { margin-top: .4rem; color: #687386; font-size: .92rem; }
        .imagine-breadcrumb { display: inline-block; margin-top: .75rem; padding: .35rem .65rem; border: 1px solid #dfe4ea; border-radius: 7px; background: #eef2f6; color: #566276; font-size: .73rem; }
        .imagine-card { min-height: 112px; padding: 1rem; border: 1px solid #dfe4ea; border-radius: 10px; background: #fff; }
        .imagine-card-title { color: #687386; font-size: .68rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; }
        .imagine-card-value { margin-top: .4rem; font-size: 1.55rem; font-weight: 850; }
        .imagine-card-description { margin-top: .2rem; color: #7b8798; font-size: .73rem; }
        .imagine-panel { padding: 1.15rem 1.25rem; border: 1px solid #dfe4ea; border-radius: 10px; background: #fff; }
        .imagine-panel-title { font-size: 1.15rem; font-weight: 780; }
        .imagine-panel-description { margin-top: .3rem; color: #687386; font-size: .82rem; line-height: 1.5; }
        .imagine-footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #dfe4ea; color: #8791a0; font-size: .7rem; }
        div.stButton > button { min-height: 2.25rem; border-radius: 7px; font-weight: 650; }
        @media (prefers-color-scheme: dark) {
            .stApp { background: #0d131b; }
            .imagine-brand-title, .imagine-header-title, .imagine-card-value, .imagine-panel-title { color: #f1f4f8; }
            .imagine-brand-subtitle, .imagine-header-subtitle, .imagine-panel-description, .imagine-card-description { color: #a5afbd; }
            .imagine-breadcrumb { background: #1a2330; border-color: #2b3745; color: #b8c1ce; }
            .imagine-card, .imagine-panel { background: #141b24; border-color: #2b3745; }
            .imagine-card-title, .imagine-label { color: #a5afbd; }
            .imagine-footer { border-top-color: #2b3745; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def specs_for_section(section: str) -> list[ModuleSpec]:
    return [spec for spec in registry_snapshot() if spec.section == section]


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
        if all(term in haystack for term in terms):
            score = 0
            if spec.label.casefold().startswith(normalized):
                score += 100
            if spec.section.casefold() == normalized:
                score += 50
            if spec.implemented:
                score += 10
            scored.append((score, spec))
    scored.sort(key=lambda item: (-item[0], item[1].section, item[1].label))
    return [spec for _, spec in scored]


def set_active_route(route: str) -> None:
    if route in {spec.route for spec in registry_snapshot()}:
        st.session_state.active_route = route


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="imagine-brand">
                <div class="imagine-brand-title">IMAGINE</div>
                <div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown('<div class="imagine-label">Module Search</div>', unsafe_allow_html=True)
        st.text_input("Search modules", key="module_search", placeholder="Try assistant, beam, zoning, BIM, project...", label_visibility="collapsed")
        st.selectbox("Search domain", ["All domains", *SECTION_ORDER], key="module_search_domain", label_visibility="collapsed")

        query = st.session_state.module_search.strip()
        if query:
            matches = search_specs(query, st.session_state.module_search_domain)
            st.caption(f"{len(matches)} result(s)")
            if not matches:
                st.info("No matching modules found.")
            for spec in matches[:12]:
                status = "Ready" if spec.implemented else "Registered"
                if st.button(f"{spec.label} · {status}", key=f"search_{spec.route}", use_container_width=True):
                    set_active_route(spec.route)
                    st.rerun()
        else:
            st.caption("Search the full enterprise module catalog.")

        st.divider()
        st.markdown('<div class="imagine-label">Domains</div>', unsafe_allow_html=True)
        for section in SECTION_ORDER:
            specs = specs_for_section(section)
            ready = sum(spec.implemented for spec in specs)
            label = f"{section}  ·  {ready}/{len(specs)}"
            with st.expander(label, expanded=(section == st.session_state.sidebar_domain)):
                st.caption(DOMAIN_DESCRIPTIONS[section])
                for spec in specs[:10]:
                    if st.button(spec.label, key=f"domain_{section}_{spec.route}", use_container_width=True, disabled=not spec.implemented):
                        st.session_state.sidebar_domain = section
                        set_active_route(spec.route)
                        st.rerun()
                if len(specs) > 10:
                    st.caption(f"Use search to find the remaining {len(specs) - 10} modules.")

        st.divider()
        active = next((spec for spec in registry_snapshot() if spec.route == st.session_state.active_route), registry_snapshot()[0])
        st.markdown('<div class="imagine-label">Current Workspace</div>', unsafe_allow_html=True)
        st.markdown(f"**{active.label}**  \n{active.section} · {'Ready' if active.implemented else 'Registered'}")
        st.caption(f"{len(registry_snapshot())} registered modules")


def render_header(title: str, subtitle: str, breadcrumb: str) -> None:
    st.markdown(
        f"""
        <div class="imagine-header">
            <div class="imagine-header-title">{title}</div>
            <div class="imagine-header-subtitle">{subtitle}</div>
            <div class="imagine-breadcrumb">{breadcrumb}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_project_summary() -> tuple[list[object], str]:
    """Load project records with the repository's actual synchronous session API."""
    try:
        from database.bootstrap import database_health
        from database.connection import SessionLocal
        health = database_health()
        database_status = "Connected" if health.get("ok") else "Unavailable"
        if not health.get("ok"):
            return [], database_status
        from projects.projects.service import ProjectService
        with SessionLocal() as db:
            projects = ProjectService.get_all_sync(db=db, skip=0, limit=10000)
        return projects, database_status
    except Exception:
        return [], "Unavailable"


def render_overview() -> None:
    render_header("IMAGINE", "Integrated Architecture, Engineering & Construction Engine", "Overview / Enterprise Workspace")
    projects, database_status = get_project_summary()
    project_count = len(projects)
    active_count = sum(1 for project in projects if str(project.status).lower().endswith("active"))
    completed_count = sum(1 for project in projects if str(project.status).lower().endswith("completed"))
    ready_count = sum(spec.implemented for spec in registry_snapshot())

    cards = [
        ("Registered Modules", len(registry_snapshot()), "Full searchable enterprise catalog"),
        ("Ready Modules", ready_count, "Connected renderers"),
        ("Projects", project_count, "Database project records"),
        ("Database", database_status, "Runtime connectivity"),
    ]
    cols = st.columns(4)
    for col, (title, value, description) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{description}</div></div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<div class="imagine-panel"><div class="imagine-panel-title">Engineering Workspace</div><div class="imagine-panel-description">Use the searchable sidebar to open Architecture, Structural, BIM, MEP, Costing and Construction workflows. The Architecture Assistant coordinates the early design brief and produces traceable preliminary recommendations.</div></div>', unsafe_allow_html=True)
        st.write("")
        st.subheader("Portfolio Snapshot")
        if projects:
            rows = []
            for project in projects[:20]:
                status = project.status.value if hasattr(project.status, "value") else str(project.status)
                rows.append({"Project": project.name, "Status": status})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No database project records are currently available.")

    with right:
        st.subheader("Domain Readiness")
        domain_rows = []
        for section in SECTION_ORDER:
            specs = specs_for_section(section)
            ready = sum(spec.implemented for spec in specs)
            domain_rows.append({"Domain": section, "Ready": ready, "Registered": len(specs)})
        df_domains = pd.DataFrame(domain_rows)
        fig = px.bar(df_domains, x="Domain", y=["Ready", "Registered"], barmode="group", height=360)
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=80), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Portfolio: {active_count} active, {completed_count} completed project record(s).")

    st.subheader("Architecture Workspace")
    architecture_routes = ["Architecture Assistant", "Zoning", "Site Planning", "Floor Planning", "Room Programming", "Compliance", "Generative Design"]
    architecture_cols = st.columns(4)
    for index, route in enumerate(architecture_routes):
        spec = next((item for item in registry_snapshot() if item.route == route), None)
        if spec is None:
            continue
        with architecture_cols[index % 4]:
            if st.button(spec.label, key=f"quick_arch_{route}", use_container_width=True, disabled=not spec.implemented):
                set_active_route(route)
                st.session_state.sidebar_domain = "ARCHITECTURE"
                st.rerun()

    st.subheader("Structural Quick Access")
    structural_routes = ["Beam Design", "Column Design", "Slab Design", "Foundation Design", "Retaining Walls", "Steel Connections", "Eurocode Suite"]
    quick_cols = st.columns(4)
    for index, route in enumerate(structural_routes):
        spec = next((item for item in registry_snapshot() if item.route == route), None)
        if spec is None:
            continue
        with quick_cols[index % 4]:
            if st.button(spec.label, key=f"quick_{route}", use_container_width=True, disabled=not spec.implemented):
                set_active_route(route)
                st.session_state.sidebar_domain = "STRUCTURAL"
                st.rerun()


def render_system_health() -> None:
    render_header("System Health", "Registry validation, renderer availability and database diagnostics", "Platform / System Health")
    try:
        validate_registry()
        registry_ok = True
        registry_error = ""
    except Exception as exc:
        registry_ok = False
        registry_error = f"{type(exc).__name__}: {exc}"
    try:
        from database.bootstrap import database_health
        db_health = database_health()
    except Exception as exc:
        db_health = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    ready = sum(spec.implemented for spec in registry_snapshot())
    a, b, c, d = st.columns(4)
    a.metric("Registered", len(registry_snapshot()))
    b.metric("Ready", ready)
    c.metric("Registry", "Healthy" if registry_ok else "Failed")
    d.metric("Database", "Connected" if db_health.get("ok") else "Unavailable")
    if not registry_ok:
        st.error(registry_error)
    if db_health.get("ok"):
        st.success("Database connectivity check passed.")
    else:
        st.warning(db_health.get("error", "Database connectivity check failed."))
    rows = [{"Module": spec.label, "Domain": spec.section, "Status": "Ready" if spec.implemented else "Registered", "Renderer": spec.module_path or "Pending"} for spec in registry_snapshot()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def load_renderer(spec: ModuleSpec) -> Callable[[], object]:
    if not spec.module_path or spec.module_path == "__builtin__":
        raise AttributeError(f"No external renderer is configured for {spec.route}.")
    module = importlib.import_module(spec.module_path)
    renderer = getattr(module, spec.renderer_name, None)
    if renderer is None:
        renderer = getattr(module, "render", None)
    if not callable(renderer):
        raise AttributeError(f"Module '{spec.module_path}' does not expose a callable renderer.")
    return renderer


def render_site_planning_registered() -> None:
    """Compatibility adapter for the legacy Site Planning route."""
    try:
        from architecture.site_planning.repository import SitePlanningRepository  # noqa: F401
        from architecture.site_planning.ui import render_site_planning
    except Exception as exc:
        st.error("The Site Planning module could not be loaded.")
        with st.expander("Complete import traceback", expanded=True):
            st.exception(exc)
        return
    try:
        render_site_planning()
    except Exception as exc:
        st.error("Site Planning could not be rendered.")
        with st.expander("Complete renderer traceback", expanded=True):
            st.exception(exc)


SPECIAL_RENDERERS: dict[str, Callable[[], object]] = {
    "architecture_site_planning": render_site_planning_registered,
}


def render_route(route: str) -> None:
    """Render a route using a registered special renderer or enterprise spec."""
    special = SPECIAL_RENDERERS.get(route)
    if special is not None:
        special()
        return
    route_aliases = {"architecture_site_planning": "Site Planning", "site_planning": "Site Planning"}
    enterprise_route = route_aliases.get(route, route)
    set_active_route(enterprise_route)
    render_selected_module(enterprise_route)


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(spec.label, f"{spec.section} workspace", f"{spec.section} / {spec.label}")
    st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">Module Registered</div><div class="imagine-panel-description">{spec.label} is present in the enterprise registry and remains searchable, but its dedicated renderer is not connected yet.</div></div>', unsafe_allow_html=True)


def render_selected_module(route: str) -> None:
    spec = next((item for item in registry_snapshot() if item.route == route), None)
    if spec is None:
        st.session_state.active_route = "Overview"
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
    try:
        renderer = load_renderer(spec)
        renderer()
    except ModuleNotFoundError as exc:
        st.warning(f"{spec.label} is not currently available.")
        with st.expander("Module import details", expanded=True):
            st.code(f"Module: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)
    except ImportError as exc:
        st.error(f"{spec.label} could not be imported.")
        with st.expander("Import error", expanded=True):
            st.code(f"Module: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)
    except AttributeError as exc:
        st.error(f"{spec.label} does not expose its expected renderer.")
        with st.expander("Renderer details", expanded=True):
            st.code(f"Expected: {spec.module_path}.{spec.renderer_name}")
            st.exception(exc)
    except Exception as exc:
        st.error(f"{spec.label} encountered a runtime error.")
        with st.expander("Complete module error", expanded=True):
            st.code(f"Domain: {spec.section}\nModule: {spec.label}\nPython module: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)


def render_footer() -> None:
    st.markdown('<div class="imagine-footer">IMAGINE AEC Engine | Integrated Architecture, Engineering & Construction Platform</div>', unsafe_allow_html=True)


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_selected_module(st.session_state.active_route)
    render_footer()


if __name__ == "__main__":
    main()
