"""IMAGINE AEC Engine Streamlit application shell.

The shell provides search-first navigation, a compact domain navigator and a
workspace-oriented presentation layer. Domain pages are discovered from the
central registry so navigation does not drift away from the module inventory.
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

st.set_page_config(page_title="IMAGINE | AEC Engine", page_icon=None, layout="wide", initial_sidebar_state="expanded")

SEARCH_ALIASES = {
    "concrete": ("beam", "column", "slab", "foundation", "punching", "en 1992"),
    "rc": ("beam", "column", "slab", "foundation", "punching", "en 1992"),
    "reinforced": ("beam", "column", "slab", "foundation", "punching"),
    "steel": ("steel members", "steel connections", "section shapes", "en 1993"),
    "bim": ("buildings", "storeys", "spaces", "elements", "ifc", "cobie", "digital twin"),
    "mep": ("integrated mep analysis", "hvac", "ventilation", "chilled water", "electrical load analysis", "water supply", "drainage"),
    "cost": ("boq", "quantity takeoff", "procurement", "forex", "inflation / escalation", "risk analysis"),
    "construction": ("planning", "scheduling", "rfis", "submittals", "snagging", "site diaries"),
    "documents": ("drawing management", "document register", "specifications", "contracts", "version control", "transmittals"),
    "ai": ("imagine architect", "imagine engineer", "imagine mep", "imagine qs", "imagine pm"),
    "project": ("projects", "approvals", "revisions", "workflows", "governance"),
    "analysis": ("structural analysis", "finite element analysis", "eurocode suite"),
    "ec": ("en1990-1998", "eurocode suite", "design standards"),
    "architecture": ("architecture assistant", "design standards", "zoning", "site planning", "floor planning", "room programming", "compliance", "generative design"),
    "roof": ("roof design",),
    "energy": ("energy", "hvac", "chilled water", "energy simulation"),
    "digital": ("digital twin", "assets", "sensors", "telemetry", "energy", "maintenance", "predictive ai"),
    "regional": ("uganda", "kenya", "tanzania", "rwanda", "south sudan", "codes", "zoning laws"),
    "integration": ("microsoft", "autocad", "revit", "archicad", "tekla", "ifcopenshell", "arcgis", "azure", "mapbox"),
    "files": ("project files", "file center", "documents", "drawings", "bim"),
}


def registry_snapshot() -> tuple[ModuleSpec, ...]:
    validate_registry()
    return MODULE_SPECS


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "module_search": "",
        "module_search_domain": "All domains",
        "active_domain": "PLATFORM",
        "last_route_load_ms": None,
        "recent_routes": [],
        "selected_project_id": None,
        "selected_project_name": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp{background:linear-gradient(135deg,#f7f9fc 0%,#eef3f8 52%,#f8fafc 100%)}
        .block-container{max-width:1600px;padding-top:.85rem;padding-bottom:3rem}
        .imagine-brand{padding:.2rem .1rem .8rem}.imagine-brand-title{font-size:1.8rem;font-weight:900;letter-spacing:-.06em}.imagine-brand-subtitle{margin-top:.25rem;color:#687588;font-size:.74rem;line-height:1.45}
        .imagine-label{margin:.7rem 0 .35rem;color:#687588;font-size:.64rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase}
        .imagine-header{padding:1.2rem 1.35rem;margin-bottom:1rem;border:1px solid rgba(120,135,155,.18);border-radius:18px;background:rgba(255,255,255,.78);box-shadow:0 16px 40px rgba(35,55,80,.07)}
        .imagine-header-title{margin:0;font-size:2.2rem;line-height:1;font-weight:900;letter-spacing:-.055em}.imagine-header-subtitle{margin-top:.45rem;color:#687588;font-size:.9rem}.imagine-breadcrumb{display:inline-block;margin-top:.7rem;padding:.3rem .6rem;border:1px solid #dce3eb;border-radius:999px;background:#f3f6f9;color:#566276;font-size:.68rem}
        .imagine-hero{padding:1.5rem;margin-bottom:1rem;border-radius:20px;background:linear-gradient(135deg,rgba(255,255,255,.94),rgba(238,244,250,.86));border:1px solid rgba(120,135,155,.17);box-shadow:0 18px 55px rgba(35,55,80,.08)}.imagine-hero-title{font-size:1.5rem;font-weight:850;letter-spacing:-.035em}.imagine-hero-copy{margin-top:.45rem;color:#647184;line-height:1.6}
        .imagine-card{min-height:105px;padding:1rem;border:1px solid rgba(120,135,155,.17);border-radius:16px;background:rgba(255,255,255,.84);box-shadow:0 10px 30px rgba(35,55,80,.05)}.imagine-card-title{color:#687588;font-size:.62rem;font-weight:850;letter-spacing:.09em;text-transform:uppercase}.imagine-card-value{margin-top:.35rem;font-size:1.45rem;font-weight:900}.imagine-card-description{margin-top:.2rem;color:#7a8697;font-size:.7rem}
        .imagine-panel{padding:1rem 1.1rem;border:1px solid rgba(120,135,155,.17);border-radius:15px;background:rgba(255,255,255,.8);box-shadow:0 10px 30px rgba(35,55,80,.045)}.imagine-panel-title{font-size:1rem;font-weight:800}.imagine-panel-description{margin-top:.25rem;color:#687588;font-size:.78rem;line-height:1.5}
        .imagine-nav{padding:.65rem .75rem;margin-bottom:1rem;border:1px solid rgba(120,135,155,.18);border-radius:15px;background:rgba(255,255,255,.76);box-shadow:0 8px 25px rgba(35,55,80,.05)}
        .imagine-search-hint{padding:.7rem .8rem;margin-top:.5rem;border:1px dashed rgba(120,135,155,.35);border-radius:12px;color:#687588;font-size:.75rem;line-height:1.5}.imagine-footer{margin-top:2.5rem;padding-top:1rem;border-top:1px solid rgba(120,135,155,.2);color:#8792a1;font-size:.67rem}
        div.stButton>button{min-height:2.25rem;border-radius:10px;font-weight:680;transition:transform .14s ease,box-shadow .14s ease}div.stButton>button:hover{transform:translateY(-1px);box-shadow:0 7px 18px rgba(35,55,80,.12)}
        @media(prefers-color-scheme:dark){.stApp{background:radial-gradient(circle at top right,#172231 0%,#0b1118 55%,#0b1118 100%)}.imagine-header,.imagine-hero,.imagine-card,.imagine-panel,.imagine-nav{background:rgba(19,28,39,.84);border-color:#293746}.imagine-brand-title,.imagine-header-title,.imagine-hero-title,.imagine-card-value,.imagine-panel-title{color:#f1f5f9}.imagine-brand-subtitle,.imagine-header-subtitle,.imagine-hero-copy,.imagine-panel-description,.imagine-card-description,.imagine-search-hint{color:#aab5c3}.imagine-breadcrumb{background:#17212c;border-color:#2b3948;color:#b9c4d1}.imagine-label,.imagine-card-title{color:#aab5c3}.imagine-footer{border-top-color:#293746}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def spec_for_route(route: str) -> ModuleSpec | None:
    return next((spec for spec in registry_snapshot() if spec.route == route), None)


def domains() -> list[str]:
    return sorted({spec.section for spec in registry_snapshot()})


def domain_specs(domain: str) -> list[ModuleSpec]:
    return [spec for spec in registry_snapshot() if spec.section == domain]


def search_specs(query: str, domain: str = "All domains") -> list[ModuleSpec]:
    normalized = " ".join(query.strip().casefold().split())
    if not normalized:
        return []
    candidates = [s for s in registry_snapshot() if domain == "All domains" or s.section == domain]
    terms = normalized.split()
    expanded_terms = set(terms)
    for term in terms:
        expanded_terms.update(SEARCH_ALIASES.get(term, ()))
    scored: list[tuple[int, ModuleSpec]] = []
    for spec in candidates:
        haystack = " ".join((spec.route, spec.label, spec.section, spec.module_path or "")).casefold()
        direct_hits = sum(1 for term in terms if term in haystack)
        alias_hits = sum(1 for term in expanded_terms if term in haystack)
        phrase_hit = normalized in haystack
        if direct_hits == 0 and alias_hits == 0 and not phrase_hit:
            continue
        score = direct_hits * 80 + alias_hits * 15 + (100 if spec.implemented else 0)
        if phrase_hit:
            score += 120
        if normalized in {spec.label.casefold(), spec.route.casefold()}:
            score += 180
        elif normalized in spec.label.casefold():
            score += 80
        elif normalized in spec.route.casefold():
            score += 60
        elif normalized in spec.section.casefold():
            score += 40
        scored.append((score, spec))
    scored.sort(key=lambda item: (-item[0], item[1].section, item[1].label))
    return [spec for _, spec in scored]


def set_active_route(route: str) -> None:
    spec = spec_for_route(route)
    if spec is None:
        return
    st.session_state.active_route = route
    st.session_state.active_domain = spec.section
    recent = [r for r in st.session_state.get("recent_routes", []) if r != route]
    st.session_state.recent_routes = [route, *recent][:6]


def load_renderer(spec: ModuleSpec) -> Callable[[], object]:
    if not spec.module_path or spec.module_path == "__builtin__":
        raise AttributeError(f"No external renderer is configured for {spec.route}.")
    module = importlib.import_module(spec.module_path)
    renderer = getattr(module, spec.renderer_name, None) or getattr(module, "render", None)
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
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Ready" if callable(renderer) else "Missing renderer", "Detail": "Callable renderer found" if callable(renderer) else f"Expected {spec.renderer_name}"})
        except Exception as exc:
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Import error", "Detail": f"{type(exc).__name__}: {exc}"})
    return rows


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


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand"><div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div></div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="imagine-label">Workspace search</div>', unsafe_allow_html=True)
        st.text_input("Search modules", key="module_search", placeholder="Search beam, zoning, BIM, files...", label_visibility="collapsed")
        domains_for_search = ["All domains", *domains()]
        current = st.session_state.get("module_search_domain", "All domains")
        if current not in domains_for_search:
            current = "All domains"
        st.selectbox("Search domain", domains_for_search, index=domains_for_search.index(current), key="module_search_domain")
        st.caption("Use the main navigator to browse a discipline. Search is reserved for finding a specific workspace quickly.")


def render_navigation() -> None:
    current = st.session_state.get("active_domain", "PLATFORM")
    if current not in domains():
        current = "PLATFORM"
    st.markdown('<div class="imagine-nav">', unsafe_allow_html=True)
    labels = ["HOME" if d == "PLATFORM" else d for d in domains()]
    selected_label = "HOME" if current == "PLATFORM" else current
    choice = st.radio("Primary navigation", labels, index=labels.index(selected_label), horizontal=True, label_visibility="collapsed", key="primary_navigation")
    selected_domain = "PLATFORM" if choice == "HOME" else choice
    if selected_domain != current:
        st.session_state.active_domain = selected_domain
        candidates = domain_specs(selected_domain)
        if selected_domain == "PLATFORM":
            set_active_route("Overview")
        elif candidates:
            ready = next((x for x in candidates if x.implemented), candidates[0])
            set_active_route(ready.route)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if selected_domain != "PLATFORM":
        pages = domain_specs(selected_domain)
        labels = [spec.label + ("" if spec.implemented else " · Registered") for spec in pages]
        active = st.session_state.get("active_route")
        active_index = next((i for i, spec in enumerate(pages) if spec.route == active), 0)
        page_choice = st.radio("Domain pages", labels, index=active_index, horizontal=True, label_visibility="collapsed", key=f"domain_pages_{selected_domain}")
        selected = pages[labels.index(page_choice)]
        if selected.route != active:
            set_active_route(selected.route)
            st.rerun()


def render_header(title: str, subtitle: str, breadcrumb: str) -> None:
    st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{title}</div><div class="imagine-header-subtitle">{subtitle}</div><div class="imagine-breadcrumb">{breadcrumb}</div></div>', unsafe_allow_html=True)


def render_workspace_controls() -> None:
    active = st.session_state.get("active_route", "Overview")
    left, middle, right = st.columns([1.1, 1.5, 1.1])
    with left:
        if active != "Overview" and st.button("Back to Overview", use_container_width=True):
            set_active_route("Overview")
            st.rerun()
    with middle:
        recent = [r for r in st.session_state.get("recent_routes", []) if r != active and spec_for_route(r)]
        if recent:
            choice = st.selectbox("Recent workspace", ["Select recent workspace", *recent], key="recent_workspace_selector")
            if choice != "Select recent workspace":
                set_active_route(choice)
                st.rerun()
    with right:
        st.caption(f"Active workspace: {active}")


def render_search_results() -> bool:
    query = st.session_state.get("module_search", "").strip()
    if not query:
        return False
    domain = st.session_state.get("module_search_domain", "All domains")
    matches = search_specs(query, domain)
    st.subheader("Workspace Search")
    st.caption(f"{len(matches)} result(s) for '{query}' · {domain}")
    if not matches:
        st.info("No matching workspace was found. Try beam, BIM, HVAC, BOQ, RFIs, files or a discipline name.")
        return True
    cols = st.columns(3)
    for index, spec in enumerate(matches[:30]):
        with cols[index % 3]:
            status = "Ready" if spec.implemented else "Registered"
            st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">{spec.label}</div><div class="imagine-panel-description">{spec.section} · {status}<br>{spec.module_path or "Built-in workspace"}</div></div>', unsafe_allow_html=True)
            if spec.implemented and st.button("Open workspace", key=f"search_open_{spec.route}", use_container_width=True):
                set_active_route(spec.route)
                st.session_state.module_search = ""
                st.rerun()
    return True


def render_project_context(projects: list[object]) -> None:
    if not projects:
        return
    options = {getattr(p, "name", f"Project {getattr(p, 'id', '')}"): getattr(p, "id", None) for p in projects}
    names = list(options)
    current = st.session_state.get("selected_project_name")
    if current not in names:
        current = names[0]
    selected = st.selectbox("Active project context", names, index=names.index(current), key="active_project_selector")
    st.session_state.selected_project_name = selected
    st.session_state.selected_project_id = options[selected]


def render_domain_summary(specs: tuple[ModuleSpec, ...]) -> None:
    st.subheader("Workspace Coverage")
    rows = []
    for section in domains():
        group = [spec for spec in specs if spec.section == section]
        ready = sum(spec.implemented for spec in group)
        rows.append({"Domain": section, "Ready": ready, "Registered": len(group), "Coverage": round(ready / len(group) * 100, 1)})
    frame = pd.DataFrame(rows)
    left, right = st.columns([1.15, 1])
    with left:
        st.dataframe(frame, use_container_width=True, hide_index=True, column_config={"Coverage": st.column_config.NumberColumn(format="%.1f%%")})
    with right:
        fig = px.bar(frame, x="Domain", y="Coverage", height=330)
        fig.update_layout(margin=dict(l=10, r=10, t=15, b=90), yaxis_title="Ready coverage (%)", xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)


def render_overview() -> None:
    render_header("IMAGINE", "Integrated Architecture, Engineering & Construction Engine", "Home / Enterprise Workspace")
    specs = registry_snapshot()
    projects, database_status = get_project_summary()
    ready = sum(spec.implemented for spec in specs)
    coverage = round(ready / len(specs) * 100, 1) if specs else 0
    st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">Design. Engineer. Build. Operate.</div><div class="imagine-hero-copy">One workspace for project delivery, architecture, structural engineering, BIM, MEP, cost, construction, documents, AI and operational intelligence.</div></div>', unsafe_allow_html=True)
    render_workspace_controls()
    if projects:
        render_project_context(projects)
    cards = [("Workspaces", len(specs), "Enterprise registry"), ("Ready", ready, f"{coverage}% coverage"), ("Projects", len(projects), "Database records"), ("Database", database_status, "Runtime connectivity")]
    cols = st.columns(4)
    for i, (title, value, desc) in enumerate(cards):
        with cols[i]:
            st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{desc}</div></div>', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("Portfolio Snapshot")
        if projects:
            rows = [{"Project": getattr(p, "name", "Unnamed project"), "Status": p.status.value if hasattr(p.status, "value") else str(p.status)} for p in projects[:25]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No database project records are currently available.")
    with right:
        st.subheader("Platform Coverage")
        rows = [{"Domain": section, "Ready": sum(x.implemented for x in specs if x.section == section), "Registered": sum(1 for x in specs if x.section == section)} for section in domains()]
        fig = px.bar(pd.DataFrame(rows), x="Domain", y=["Ready", "Registered"], barmode="group", height=390)
        fig.update_layout(margin=dict(l=10, r=10, t=15, b=95), legend_title_text="", xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
    render_domain_summary(specs)


def render_system_health() -> None:
    render_header("System Health", "Registry validation, renderer probing and database diagnostics", "Platform / System Health")
    try:
        validate_registry(); registry_status = "Healthy"; registry_error = ""
    except Exception as exc:
        registry_status = "Failed"; registry_error = f"{type(exc).__name__}: {exc}"
    try:
        from database.bootstrap import database_health
        db_health = database_health()
    except Exception as exc:
        db_health = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    specs = registry_snapshot()
    a, b, c, d = st.columns(4)
    a.metric("Registered", len(specs)); b.metric("Marked Ready", sum(x.implemented for x in specs)); c.metric("Registry", registry_status); d.metric("Database", "Connected" if db_health.get("ok") else "Unavailable")
    if registry_error: st.error(registry_error)
    if db_health.get("ok"): st.success("Database connectivity check passed.")
    else: st.warning(db_health.get("error", "Database connectivity check failed."))
    st.subheader("Renderer Health")
    rows = probe_renderers()
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True) if rows else st.info("No external implemented renderers were available to probe.")


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(spec.label, f"{spec.section} workspace", f"{spec.section} / {spec.label}")
    st.warning("This page is registered but its execution renderer is not connected yet.")


def render_selected_module(route: str) -> None:
    spec = spec_for_route(route)
    if spec is None:
        set_active_route("Overview"); render_overview(); return
    if route == "Overview":
        render_overview(); return
    if route == "System Health":
        render_system_health(); return
    if not spec.implemented or not spec.module_path:
        render_placeholder(spec); return
    render_header(spec.label, f"IMAGINE {spec.section.title()} Workspace", f"{spec.section} / {spec.label}")
    render_workspace_controls()
    started = time.perf_counter()
    try:
        load_renderer(spec)()
        st.session_state.last_route_load_ms = round((time.perf_counter() - started) * 1000, 1)
    except Exception as exc:
        st.error(f"{spec.label} could not be loaded safely. The navigation shell remains available.")
        with st.expander("Technical details", expanded=False):
            st.code(f"Domain: {spec.section}\nModule: {spec.module_path}\nRenderer: {spec.renderer_name}")
            st.exception(exc)


def render_footer() -> None:
    load_ms = st.session_state.get("last_route_load_ms")
    timing = f" · last workspace load {load_ms} ms" if load_ms is not None else ""
    st.markdown(f'<div class="imagine-footer">IMAGINE AEC Engine · Domain navigation + workspace search{timing}</div>', unsafe_allow_html=True)


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_navigation()
    query = st.session_state.get("module_search", "").strip()
    if query:
        render_header("Workspace Search", "Find an engineering, project, delivery or file workspace", "Search / Workspace")
        render_search_results()
    else:
        render_selected_module(st.session_state.active_route)
    render_footer()


if __name__ == "__main__":
    main()
