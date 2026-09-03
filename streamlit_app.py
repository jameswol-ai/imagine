"""IMAGINE AEC Engine Streamlit application shell.

The shell owns navigation, workspace composition, diagnostics and safe lazy
loading. Domain modules own their engineering calculations and persistence.
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
    page_title="IMAGINE | Integrated AEC Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DOMAIN_DESCRIPTIONS = {
    "PLATFORM": "Enterprise workspace, module registry and runtime diagnostics.",
    "PROJECTS": "Project lifecycle, approvals, revisions, workflows and governance.",
    "ARCHITECTURE": "Brief development, standards, site, planning, programming, compliance and generative design.",
    "STRUCTURAL": "Analysis, reinforced concrete, steel, timber, foundations, retaining walls and Eurocode workflows.",
    "BIM": "Buildings, storeys, spaces, elements and OpenBIM workflows.",
    "MEP": "Mechanical, electrical, plumbing and energy engineering.",
    "COSTING": "BOQ, quantity takeoff, procurement, currency, escalation and risk analysis.",
    "CONSTRUCTION": "Planning, scheduling, RFIs, submittals, snagging and site management.",
    "DOCUMENTS": "Drawings, specifications, contracts, revisions and transmittals.",
    "AI": "Architecture, engineering, MEP, QS and project-management assistants.",
    "ANALYTICS": "Dashboards, KPIs, portfolio intelligence, forecasting and reporting.",
    "REGIONAL": "Regional codes, regulations and zoning requirements.",
    "INTEGRATIONS": "AEC software, GIS, cloud and interoperability integrations.",
    "DIGITAL TWIN": "Assets, sensors, telemetry, maintenance and predictive intelligence.",
}
SECTION_ORDER = tuple(DOMAIN_DESCRIPTIONS)


def registry_snapshot() -> tuple[ModuleSpec, ...]:
    validate_registry()
    return MODULE_SPECS


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "module_search": "",
        "module_search_domain": "All domains",
        "sidebar_domain": "PLATFORM",
        "show_diagnostics": False,
        "last_route_load_ms": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f7fa; }
        .block-container { max-width: 1600px; padding-top: 1.2rem; padding-bottom: 3rem; }
        section[data-testid="stSidebar"] { width: 330px !important; }
        .imagine-brand { padding: .3rem .2rem .75rem; }
        .imagine-brand-title { font-size: 1.7rem; font-weight: 850; letter-spacing: -.05em; }
        .imagine-brand-subtitle { margin-top: .25rem; color: #697587; font-size: .76rem; line-height: 1.4; }
        .imagine-label { margin: .8rem 0 .35rem; color: #697587; font-size: .66rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
        .imagine-header { margin-bottom: 1.1rem; }
        .imagine-header-title { margin: 0; font-size: 2.25rem; line-height: 1.05; font-weight: 850; letter-spacing: -.05em; }
        .imagine-header-subtitle { margin-top: .42rem; color: #687386; font-size: .92rem; }
        .imagine-breadcrumb { display: inline-block; margin-top: .7rem; padding: .35rem .65rem; border: 1px solid #dfe4ea; border-radius: 7px; background: #eef2f6; color: #566276; font-size: .72rem; }
        .imagine-card { min-height: 110px; padding: 1rem; border: 1px solid #dfe4ea; border-radius: 11px; background: #fff; }
        .imagine-card-title { color: #687386; font-size: .66rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; }
        .imagine-card-value { margin-top: .38rem; font-size: 1.55rem; font-weight: 850; }
        .imagine-card-description { margin-top: .2rem; color: #7b8798; font-size: .72rem; }
        .imagine-panel { padding: 1.15rem 1.25rem; border: 1px solid #dfe4ea; border-radius: 11px; background: #fff; }
        .imagine-panel-title { font-size: 1.12rem; font-weight: 780; }
        .imagine-panel-description { margin-top: .3rem; color: #687386; font-size: .82rem; line-height: 1.55; }
        .imagine-footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #dfe4ea; color: #8791a0; font-size: .69rem; }
        div.stButton > button { min-height: 2.3rem; border-radius: 8px; font-weight: 650; }
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
        score = 0
        if spec.label.casefold().startswith(normalized):
            score += 100
        if spec.route.casefold().startswith(normalized):
            score += 60
        if spec.section.casefold() == normalized:
            score += 40
        if spec.implemented:
            score += 10
        scored.append((score, spec))
    scored.sort(key=lambda item: (-item[0], item[1].section, item[1].label))
    return [spec for _, spec in scored]


def set_active_route(route: str) -> None:
    spec = spec_for_route(route)
    if spec is not None:
        st.session_state.active_route = route
        st.session_state.sidebar_domain = spec.section


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


def probe_renderers() -> list[dict[str, str]]:
    rows = []
    for spec in registry_snapshot():
        if not spec.implemented or not spec.module_path or spec.module_path == "__builtin__":
            continue
        try:
            module = importlib.import_module(spec.module_path)
            renderer = getattr(module, spec.renderer_name, None) or getattr(module, "render", None)
            status = "Ready" if callable(renderer) else "Missing renderer"
            detail = "Callable renderer found" if callable(renderer) else f"Expected {spec.renderer_name}"
        except Exception as exc:
            status = "Import error"
            detail = f"{type(exc).__name__}: {exc}"
        rows.append({"Module": spec.label, "Domain": spec.section, "Status": status, "Detail": detail})
    return rows


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand"><div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div></div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="imagine-label">Find a workspace</div>', unsafe_allow_html=True)
        st.text_input("Search modules", key="module_search", placeholder="beam, project, zoning, BIM...", label_visibility="collapsed")
        st.selectbox("Search domain", ["All domains", *SECTION_ORDER], key="module_search_domain", label_visibility="collapsed")

        query = st.session_state.module_search.strip()
        if query:
            matches = search_specs(query, st.session_state.module_search_domain)
            st.caption(f"{len(matches)} matching workspace(s)")
            if not matches:
                st.info("No matching workspaces found.")
            for spec in matches[:15]:
                status = "Ready" if spec.implemented else "Registered"
                if st.button(f"{spec.label} · {status}", key=f"search_{spec.route}", use_container_width=True):
                    set_active_route(spec.route)
                    st.rerun()
        else:
            st.caption("Search the complete enterprise module catalog.")

        st.divider()
        st.markdown('<div class="imagine-label">Domains</div>', unsafe_allow_html=True)
        for section in SECTION_ORDER:
            specs = specs_for_section(section)
            ready = sum(spec.implemented for spec in specs)
            with st.expander(f"{section}  ·  {ready}/{len(specs)}", expanded=(section == st.session_state.sidebar_domain)):
                st.caption(DOMAIN_DESCRIPTIONS[section])
                for spec in specs[:12]:
                    if st.button(spec.label, key=f"domain_{section}_{spec.route}", use_container_width=True, disabled=not spec.implemented):
                        set_active_route(spec.route)
                        st.rerun()
                if len(specs) > 12:
                    st.caption(f"{len(specs) - 12} additional workspace(s) available through search.")

        st.divider()
        active = spec_for_route(st.session_state.active_route) or registry_snapshot()[0]
        st.markdown('<div class="imagine-label">Current workspace</div>', unsafe_allow_html=True)
        st.markdown(f"**{active.label}**  \n{active.section} · {'Ready' if active.implemented else 'Registered'}")
        if st.button("Return to Overview", use_container_width=True):
            set_active_route("Overview")
            st.rerun()


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
    cards = [
        ("Workspaces", len(specs), "Registered enterprise modules"),
        ("Ready", ready, "Modules with connected renderers"),
        ("Projects", len(projects), "Database project records"),
        ("Database", database_status, "Runtime connectivity"),
    ]
    cols = st.columns(4)
    for col, (title, value, description) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{description}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="imagine-panel"><div class="imagine-panel-title">One AEC workspace, one navigation model</div><div class="imagine-panel-description">IMAGINE connects the project lifecycle from brief and architecture through structural engineering, BIM, MEP, costing, construction, documents, analytics and digital-twin workflows. Use the sidebar search to jump directly to any registered workspace.</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Portfolio Snapshot")
        if projects:
            rows = []
            for project in projects[:25]:
                status = project.status.value if hasattr(project.status, "value") else str(project.status)
                rows.append({"Project": project.name, "Status": status})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No database project records are currently available.")

    with right:
        st.subheader("Domain Readiness")
        rows = []
        for section in SECTION_ORDER:
            domain_specs = specs_for_section(section)
            rows.append({"Domain": section, "Ready": sum(x.implemented for x in domain_specs), "Registered": len(domain_specs)})
        df = pd.DataFrame(rows)
        fig = px.bar(df, x="Domain", y=["Ready", "Registered"], barmode="group", height=390)
        fig.update_layout(margin=dict(l=10, r=10, t=15, b=90), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Start Here")
    quick_routes = [
        ("Projects", "PROJECTS"), ("Architecture Assistant", "ARCHITECTURE"),
        ("Design Standards", "ARCHITECTURE"), ("Beam Design", "STRUCTURAL"),
        ("Roof Design", "STRUCTURAL"), ("Structural Analysis", "STRUCTURAL"),
        ("Buildings", "BIM"), ("Integrated MEP Analysis", "MEP"),
        ("BOQ", "COSTING"), ("Planning", "CONSTRUCTION"),
        ("Drawing Management", "DOCUMENTS"), ("Dashboards", "ANALYTICS"),
    ]
    quick_cols = st.columns(4)
    for index, (route, domain) in enumerate(quick_routes):
        spec = spec_for_route(route)
        if spec is None:
            continue
        with quick_cols[index % 4]:
            if st.button(spec.label, key=f"overview_{route}", use_container_width=True, disabled=not spec.implemented):
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

    st.subheader("Renderer Probe")
    with st.spinner("Checking registered renderers..."):
        rows = probe_renderers()
    df = pd.DataFrame(rows)
    if not df.empty:
        counts = df["Status"].value_counts().to_dict()
        st.caption(" · ".join(f"{key}: {value}" for key, value in counts.items()))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No external implemented renderers were available to probe.")


def render_site_planning_registered() -> None:
    try:
        from architecture.site_planning.repository import SitePlanningRepository  # noqa: F401
        from architecture.site_planning.ui import render_site_planning
        render_site_planning()
    except Exception as exc:
        st.error("Site Planning could not be rendered.")
        with st.expander("Complete renderer traceback", expanded=True):
            st.exception(exc)


SPECIAL_RENDERERS: dict[str, Callable[[], object]] = {
    "architecture_site_planning": render_site_planning_registered,
}


def render_route(route: str) -> None:
    special = SPECIAL_RENDERERS.get(route)
    if special is not None:
        special()
        return
    aliases = {"architecture_site_planning": "Site Planning", "site_planning": "Site Planning"}
    render_selected_module(aliases.get(route, route))


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(spec.label, f"{spec.section} workspace", f"{spec.section} / {spec.label}")
    st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">Workspace registered, renderer pending</div><div class="imagine-panel-description">{spec.label} is present in the enterprise registry but its dedicated renderer is not connected yet. It remains discoverable so the platform can grow without changing navigation architecture.</div></div>', unsafe_allow_html=True)


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
    except ModuleNotFoundError as exc:
        st.error(f"{spec.label} could not be imported because a module dependency is missing.")
        with st.expander("Import details", expanded=True):
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
        st.error(f"{spec.label} encountered a runtime error. The application shell is still available.")
        with st.expander("Complete module error", expanded=True):
            st.code(f"Domain: {spec.section}\nModule: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)


def render_footer() -> None:
    load_ms = st.session_state.get("last_route_load_ms")
    timing = f" · last workspace load {load_ms} ms" if load_ms is not None else ""
    st.markdown(f'<div class="imagine-footer">IMAGINE AEC Engine · Integrated Architecture, Engineering & Construction Platform{timing}</div>', unsafe_allow_html=True)


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_selected_module(st.session_state.active_route)
    render_footer()


if __name__ == "__main__":
    main()
