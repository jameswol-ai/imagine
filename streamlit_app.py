"""IMAGINE AEC Engine Streamlit application shell."""
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
    "structural": ("structural design handbook", "building materials", "eurocode suite", "beam design", "column design", "slab design", "stairs design", "openings design", "railings & balustrades", "structural analysis"),
    "concrete": ("beam", "column", "slab", "foundation", "punching", "en 1992", "building materials"),
    "rc": ("beam", "column", "slab", "foundation", "punching", "en 1992"),
    "steel": ("steel members", "steel connections", "section shapes", "en 1993"),
    "timber": ("en 1995", "roof design", "building materials"),
    "masonry": ("en 1996", "building materials"),
    "aluminium": ("en 1999", "building materials"),
    "aluminum": ("en 1999", "building materials"),
    "geotechnical": ("en 1997", "foundation design", "retaining walls"),
    "seismic": ("en 1998", "structural analysis"),
    "composite": ("en 1994", "steel members", "beam design", "slab design"),
    "materials": ("building materials", "concrete", "steel", "timber", "masonry", "aluminium"),
    "handbook": ("structural design handbook", "architectural design handbook"),
    "eurocode": tuple(f"en 199{i}" for i in range(10)) + ("eurocode suite",),
    "analysis": ("structural analysis", "finite element analysis"),
    "architecture": ("architecture assistant", "design standards", "architectural design handbook", "zoning", "site planning", "floor planning", "room programming", "compliance", "generative design"),
    "stairs": ("stairs design", "architecture", "compliance"),
    "stair": ("stairs design", "architecture", "compliance"),
    "opening": ("openings design", "beam design", "architecture"),
    "openings": ("openings design", "beam design", "architecture"),
    "railing": ("railings & balustrades", "architecture"),
    "railings": ("railings & balustrades", "architecture"),
    "bim": ("buildings", "storeys", "spaces", "elements", "ifc", "cobie", "digital twin"),
    "mep": ("integrated mep analysis", "hvac", "ventilation", "chilled water", "electrical load analysis", "water supply", "drainage"),
    "cost": ("boq", "quantity takeoff", "procurement", "forex", "inflation / escalation", "risk analysis"),
    "construction": ("planning", "scheduling", "rfis", "submittals", "snagging", "site diaries"),
    "documents": ("drawing management", "document register", "specifications", "contracts", "version control", "transmittals"),
    "files": ("project files", "file center", "documents", "drawings", "bim"),
}


def registry_snapshot() -> tuple[ModuleSpec, ...]:
    validate_registry()
    return MODULE_SPECS


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview", "module_search": "", "module_search_domain": "All domains",
        "active_domain": "PLATFORM", "recent_routes": [], "selected_project_id": None,
        "selected_project_name": None, "last_route_load_ms": None, "sidebar_nav_domain": "HOME",
        "sidebar_nav_workspace": "Overview",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def inject_styles() -> None:
    st.markdown("""
    <style>
    .stApp{background:linear-gradient(135deg,#f6f8fb,#edf2f7 52%,#f9fbfd)}.block-container{max-width:1700px;padding-top:1rem;padding-bottom:3rem}
    [data-testid="stSidebar"]{border-right:1px solid rgba(100,115,135,.18)}[data-testid="stSidebar"] .block-container{padding:1.15rem .85rem}
    .imagine-brand-title{font-size:1.9rem;font-weight:950;letter-spacing:-.07em}.imagine-brand-subtitle{color:#697689;font-size:.72rem;line-height:1.45;margin-bottom:.7rem}
    .imagine-header,.imagine-hero,.imagine-panel,.imagine-card,.imagine-section{border:1px solid rgba(110,125,145,.17);border-radius:20px;background:rgba(255,255,255,.86);box-shadow:0 14px 38px rgba(30,50,75,.055)}
    .imagine-header{padding:1.2rem 1.35rem;margin-bottom:1rem}.imagine-header-title{font-size:2.2rem;font-weight:920;letter-spacing:-.055em}.imagine-header-subtitle{color:#687588;margin-top:.3rem;line-height:1.5}
    .imagine-breadcrumb{display:inline-block;margin-top:.7rem;padding:.3rem .65rem;border-radius:999px;background:#eef2f6;color:#566276;font-size:.67rem}.imagine-hero{padding:1.5rem;margin-bottom:1rem;overflow:hidden}
    .imagine-hero-title{font-size:1.65rem;font-weight:900;letter-spacing:-.04em}.imagine-hero-copy{color:#647184;line-height:1.65;margin-top:.4rem;max-width:900px}
    .imagine-panel{padding:1rem;margin-bottom:.75rem}.imagine-panel-title{font-weight:850;font-size:1rem}.imagine-panel-description{color:#687588;font-size:.75rem;margin-top:.25rem;line-height:1.45}
    .imagine-card{min-height:108px;padding:1rem 1.05rem}.imagine-card-title{color:#687588;font-size:.61rem;font-weight:850;letter-spacing:.11em;text-transform:uppercase}.imagine-card-value{font-size:1.65rem;font-weight:930;margin-top:.35rem;letter-spacing:-.04em}.imagine-card-description{color:#7a8697;font-size:.7rem;margin-top:.15rem}
    .imagine-section{padding:1.05rem;margin-bottom:1rem}.imagine-section-title{font-size:1.05rem;font-weight:850}.imagine-section-copy{color:#748093;font-size:.76rem;margin-top:.2rem}
    .sidebar-heading{font-size:.61rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#718096;margin:.7rem 0 .35rem}.sidebar-result{padding:.55rem .65rem;border:1px solid rgba(110,125,145,.14);border-radius:11px;background:rgba(255,255,255,.48);margin:.35rem 0}.sidebar-result-title{font-size:.76rem;font-weight:750}.sidebar-result-meta{font-size:.62rem;color:#7a8697;margin-top:.12rem}.imagine-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(120,135,155,.2);color:#8792a1;font-size:.67rem}
    @media(prefers-color-scheme:dark){.stApp{background:#0a1017}.imagine-header,.imagine-hero,.imagine-panel,.imagine-card,.imagine-section{background:rgba(18,27,38,.9);border-color:#293746}.imagine-header-title,.imagine-hero-title,.imagine-card-value,.imagine-panel-title,.imagine-section-title,.sidebar-result-title{color:#f1f5f9}.imagine-header-subtitle,.imagine-hero-copy,.imagine-panel-description,.imagine-card-description,.imagine-section-copy,.imagine-brand-subtitle,.sidebar-result-meta{color:#aab5c3}.imagine-breadcrumb{background:#17212c;color:#b9c4d1}.sidebar-result{background:#111b25;border-color:#2b3948}}
    </style>
    """, unsafe_allow_html=True)


def spec_for_route(route: str) -> ModuleSpec | None:
    return next((s for s in registry_snapshot() if s.route == route), None)


def domains() -> list[str]:
    return sorted({s.section for s in registry_snapshot()})


def domain_specs(domain: str) -> list[ModuleSpec]:
    return [s for s in registry_snapshot() if s.section == domain]


def search_specs(query: str, domain: str = "All domains") -> list[ModuleSpec]:
    normalized = " ".join(query.casefold().split())
    if not normalized:
        return []
    candidates = [s for s in registry_snapshot() if domain == "All domains" or s.section == domain]
    terms = normalized.split(); expanded = set(terms)
    for term in terms:
        expanded.update(SEARCH_ALIASES.get(term, ()))
    scored: list[tuple[int, ModuleSpec]] = []
    for spec in candidates:
        hay = " ".join((spec.route, spec.label, spec.section, spec.module_path or "")).casefold()
        direct = sum(term in hay for term in terms); alias = sum(term in hay for term in expanded); phrase = normalized in hay
        if not (direct or alias or phrase):
            continue
        score = direct * 80 + alias * 15 + (100 if spec.implemented else 0) + (120 if phrase else 0)
        if normalized in {spec.route.casefold(), spec.label.casefold()}: score += 180
        elif normalized in spec.label.casefold(): score += 80
        scored.append((score, spec))
    return [spec for _, spec in sorted(scored, key=lambda x: (-x[0], x[1].section, x[1].label))]


def set_active_route(route: str) -> None:
    spec = spec_for_route(route)
    if not spec:
        return
    st.session_state.active_route = route
    st.session_state.active_domain = spec.section
    if route != "Overview":
        st.session_state.sidebar_nav_domain = "HOME" if spec.section == "PLATFORM" else spec.section
        st.session_state.sidebar_nav_workspace = spec.label
    else:
        st.session_state.sidebar_nav_workspace = "Discipline Overview" if st.session_state.get("sidebar_nav_domain") not in {None, "", "HOME"} else "Overview"
    recent = [r for r in st.session_state.recent_routes if r != route]
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
            module = importlib.import_module(spec.module_path); renderer = getattr(module, spec.renderer_name, None) or getattr(module, "render", None)
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Ready" if callable(renderer) else "Missing renderer", "Detail": "Callable renderer found" if callable(renderer) else f"Expected {spec.renderer_name}"})
        except Exception as exc:
            rows.append({"Module": spec.label, "Domain": spec.section, "Status": "Import error", "Detail": f"{type(exc).__name__}: {exc}"})
    return rows


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-heading">Navigate</div>', unsafe_allow_html=True)
        nav_domains = ["HOME", *[d for d in domains() if d != "PLATFORM"]]
        current_domain = st.session_state.sidebar_nav_domain if st.session_state.sidebar_nav_domain in nav_domains else "HOME"
        selected_domain = st.selectbox("Discipline", nav_domains, index=nav_domains.index(current_domain), key="sidebar_domain_select", label_visibility="collapsed")
        if selected_domain != current_domain:
            st.session_state.sidebar_nav_domain = selected_domain
            st.session_state.sidebar_nav_workspace = "Overview" if selected_domain == "HOME" else "Discipline Overview"
            set_active_route("Overview")
            st.session_state.sidebar_nav_domain = selected_domain
            st.session_state.sidebar_nav_workspace = "Overview" if selected_domain == "HOME" else "Discipline Overview"
            st.rerun()

        domain = "PLATFORM" if selected_domain == "HOME" else selected_domain
        pages = domain_specs(domain)
        page_labels = (["Discipline Overview"] if selected_domain != "HOME" else []) + [p.label + ("" if p.implemented else " · Registered") for p in pages]
        current_label = st.session_state.sidebar_nav_workspace
        if current_label not in page_labels:
            current_label = "Discipline Overview" if selected_domain != "HOME" else (page_labels[0] if page_labels else "")
        selected_page = st.selectbox("Workspace", page_labels, index=page_labels.index(current_label) if current_label in page_labels else 0, key="sidebar_workspace_select", label_visibility="collapsed") if page_labels else ""
        if selected_page == "Discipline Overview":
            st.session_state.sidebar_nav_workspace = selected_page
            if st.session_state.active_route != "Overview":
                set_active_route("Overview")
                st.rerun()
        elif selected_page:
            chosen = pages[page_labels.index(selected_page) - (1 if selected_domain != "HOME" else 0)]
            if chosen.route != st.session_state.active_route:
                set_active_route(chosen.route)
                st.rerun()

        st.markdown('<div class="sidebar-heading">Search all workspaces</div>', unsafe_allow_html=True)
        st.text_input("Search", key="module_search", placeholder="Search stairs, EN 1992, BIM...", label_visibility="collapsed")
        query = st.session_state.module_search.strip()
        if query:
            matches = search_specs(query)
            st.markdown(f'<div class="sidebar-heading">Search results · {len(matches)}</div>', unsafe_allow_html=True)
            if not matches:
                st.caption("No matching workspace. Try a discipline, handbook, material or design tool.")
            else:
                for index, spec in enumerate(matches[:15]):
                    st.markdown(f'<div class="sidebar-result"><div class="sidebar-result-title">{spec.label}</div><div class="sidebar-result-meta">{spec.section} · {"Ready" if spec.implemented else "Registered"}</div></div>', unsafe_allow_html=True)
                    if spec.implemented and st.button("Open", key=f"sidebar_search_open_{index}_{spec.route}", use_container_width=True):
                        set_active_route(spec.route); st.session_state.module_search = ""; st.rerun()
                    elif not spec.implemented:
                        st.caption("Registered, renderer pending")
        st.markdown('<div class="sidebar-heading">Recent workspaces</div>', unsafe_allow_html=True)
        recent = [r for r in st.session_state.recent_routes if r != st.session_state.active_route and spec_for_route(r)]
        if recent:
            for index, route in enumerate(recent[:5]):
                if st.button(route, key=f"sidebar_recent_{index}_{route}", use_container_width=True):
                    set_active_route(route); st.rerun()
        else:
            st.caption("Recently opened workspaces will appear here.")
        st.divider(); st.caption("Navigation stays in the sidebar. Search is global and selected workspaces open in the main area.")


def render_header(title: str, subtitle: str, breadcrumb: str) -> None:
    st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{title}</div><div class="imagine-header-subtitle">{subtitle}</div><div class="imagine-breadcrumb">{breadcrumb}</div></div>', unsafe_allow_html=True)


def render_workspace_controls() -> None:
    active = st.session_state.active_route; a, b = st.columns([1, 2.2])
    with a:
        if active != "Overview" and st.button("Back to Home", use_container_width=True):
            set_active_route("Overview"); st.rerun()
    with b:
        recent = [r for r in st.session_state.recent_routes if r != active and spec_for_route(r)]
        if recent:
            choice = st.selectbox("Recent workspace", ["Select recent workspace", *recent], key="recent_workspace_main")
            if choice != "Select recent workspace": set_active_route(choice); st.rerun()


def render_search_landing() -> None:
    query = st.session_state.module_search.strip(); matches = search_specs(query)
    render_header("Search", "Find a workspace, then open it from the sidebar results.", "Search / All workspaces")
    if not matches: st.info(f"No workspace matched '{query}'."); return
    st.markdown(f'<div class="imagine-section"><div class="imagine-section-title">{len(matches)} matching workspaces</div><div class="imagine-section-copy">Search results remain in the sidebar so navigation and the workspace canvas stay visually separate.</div></div>', unsafe_allow_html=True)
    rows = [{"Workspace": s.label, "Discipline": s.section, "Status": "Ready" if s.implemented else "Registered"} for s in matches[:30]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(520, 80 + len(rows) * 35))


def render_discipline_dashboard(domain: str) -> None:
    specs = registry_snapshot(); group = [s for s in specs if s.section == domain]; ready = [s for s in group if s.implemented]; pending = [s for s in group if not s.implemented]
    coverage = round(100 * len(ready) / len(group), 1) if group else 0
    render_header(f"{domain.title()} Dashboard", f"Discipline command center for {domain.title()} workspaces", f"Home / {domain.title()}")
    st.markdown(f'<div class="imagine-hero"><div class="imagine-hero-title">{domain.title()} at a glance.</div><div class="imagine-hero-copy">The Home dashboard is now discipline-aware. Use the workspace selector for direct navigation, or open a ready workspace below.</div></div>', unsafe_allow_html=True)
    cards = [("Workspaces", len(group), "Registered in this discipline"), ("Ready", len(ready), "Executable renderers"), ("Coverage", f"{coverage}%", "Renderer readiness"), ("Pending", len(pending), "Registered but not connected")]
    cols = st.columns(4)
    for i, (title, value, description) in enumerate(cards):
        with cols[i]: st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{description}</div></div>', unsafe_allow_html=True)
    status_df = pd.DataFrame({"Status": ["Ready", "Pending"], "Count": [len(ready), len(pending)]})
    left, right = st.columns([1.15, 1.85])
    with left:
        st.markdown('<div class="imagine-section"><div class="imagine-section-title">Workspace readiness</div><div class="imagine-section-copy">Executable versus registered workspaces.</div></div>', unsafe_allow_html=True)
        fig = px.pie(status_df, names="Status", values="Count", hole=.62, height=310); fig.update_layout(margin=dict(l=10,r=10,t=15,b=10), showlegend=True); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.markdown('<div class="imagine-section"><div class="imagine-section-title">Workspace portfolio</div><div class="imagine-section-copy">The discipline registry and current execution state.</div></div>', unsafe_allow_html=True)
        portfolio = pd.DataFrame([{"Workspace": s.label, "Status": "Ready" if s.implemented else "Pending", "Route": s.route} for s in group]); st.dataframe(portfolio, use_container_width=True, hide_index=True, height=310)
    st.markdown('<div class="imagine-section"><div class="imagine-section-title">Key workspaces</div><div class="imagine-section-copy">Open the most useful ready tools directly from the command center.</div></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, spec in enumerate(ready[:8]):
        with cols[i % 4]:
            st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">{spec.label}</div><div class="imagine-panel-description">{spec.section.title()} workspace</div></div>', unsafe_allow_html=True)
            if st.button("Open workspace", key=f"discipline_open_{domain}_{spec.route}", use_container_width=True): set_active_route(spec.route); st.rerun()
    if not ready: st.info("No executable workspaces are connected to this discipline yet.")


def render_overview() -> None:
    specs = registry_snapshot(); selected_domain = st.session_state.get("sidebar_nav_domain", "HOME")
    if selected_domain not in {"HOME", ""}: return render_discipline_dashboard(selected_domain)
    ready = sum(s.implemented for s in specs); registered = len(specs); coverage = round(100 * ready / registered, 1) if registered else 0
    render_header("Home", "IMAGINE Integrated Architecture, Engineering & Construction Engine", "Home / Command Center")
    st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">Design intelligence, organized as one workspace.</div><div class="imagine-hero-copy">Select a discipline in the sidebar to turn Home into its command center. Global search finds specialist tools across the entire platform.</div></div>', unsafe_allow_html=True)
    cards = [("Workspaces", registered, "Central enterprise registry"), ("Ready", ready, f"{coverage}% renderer coverage"), ("Disciplines", len([d for d in domains() if d != "PLATFORM"]), "Architecture to Digital Twin"), ("Recent", len(st.session_state.recent_routes), "Recently opened workspaces")]
    cols = st.columns(4)
    for i, (title, value, description) in enumerate(cards):
        with cols[i]: st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div><div class="imagine-card-description">{description}</div></div>', unsafe_allow_html=True)
    rows = []
    for domain in domains():
        group = [s for s in specs if s.section == domain]; ready_count = sum(s.implemented for s in group)
        rows.append({"Domain": "Home" if domain == "PLATFORM" else domain.title(), "Ready": ready_count, "Registered": len(group), "Coverage %": round(100 * ready_count / len(group), 1) if group else 0})
    df = pd.DataFrame(rows)
    st.markdown('<div class="imagine-section"><div class="imagine-section-title">Platform coverage</div><div class="imagine-section-copy">A compact view of executable renderer coverage.</div></div>', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1.35])
    with left: st.dataframe(df, use_container_width=True, hide_index=True, height=390)
    with right:
        fig = px.bar(df, x="Domain", y="Coverage %", text="Coverage %", height=390); fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside", cliponaxis=False); fig.update_layout(margin=dict(l=10,r=10,t=25,b=100), yaxis=dict(range=[0,110]), xaxis_tickangle=-35, showlegend=False); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="imagine-section"><div class="imagine-section-title">Discipline snapshot</div><div class="imagine-section-copy">Select a discipline in the sidebar to transform Home into its command center.</div></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, domain in enumerate([d for d in domains() if d != "PLATFORM"]):
        group = [s for s in specs if s.section == domain]; ready_count = sum(s.implemented for s in group)
        with cols[i % 4]: st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">{domain.title()}</div><div class="imagine-panel-description">{ready_count} ready of {len(group)} registered</div></div>', unsafe_allow_html=True)


def render_system_health() -> None:
    render_header("System Health", "Registry, renderer and runtime diagnostics", "Home / System Health"); rows = probe_renderers(); ready = sum(r["Status"] == "Ready" for r in rows); errors = len(rows) - ready
    a,b,c = st.columns(3); a.metric("Registered", len(registry_snapshot())); b.metric("Ready renderers", ready); c.metric("Import / renderer issues", errors)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=560) if rows else st.info("No external renderers available to probe.")


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(spec.label, f"{spec.section} workspace", f"{spec.section} / {spec.label}"); st.warning("This workspace is registered in the enterprise menu but its execution renderer is not connected yet.")


def render_selected_module(route: str) -> None:
    spec = spec_for_route(route)
    if not spec: return render_overview()
    if route == "Overview": return render_overview()
    if route == "System Health": return render_system_health()
    if not spec.implemented or not spec.module_path: return render_placeholder(spec)
    render_header(spec.label, f"IMAGINE {spec.section.title()} Workspace", f"{spec.section} / {spec.label}"); render_workspace_controls(); started = time.perf_counter()
    try:
        load_renderer(spec)(); st.session_state.last_route_load_ms = round((time.perf_counter()-started)*1000,1)
    except Exception as exc:
        st.error(f"{spec.label} could not be loaded safely. The sidebar remains available for navigation.")
        with st.expander("Technical details", expanded=False): st.code(f"Module: {spec.module_path}\nRenderer: {spec.renderer_name}"); st.exception(exc)


def main() -> None:
    init_session_state(); inject_styles(); render_sidebar(); query = st.session_state.module_search.strip()
    if query and st.session_state.active_route == "Overview": render_search_landing()
    else: render_selected_module(st.session_state.active_route)
    load_ms = st.session_state.get("last_route_load_ms"); timing = f" · last workspace load {load_ms} ms" if load_ms else ""
    st.markdown(f'<div class="imagine-footer">IMAGINE AEC Engine · Sidebar navigation + global workspace search + discipline-aware Home{timing}</div>', unsafe_allow_html=True)


if __name__ == "__main__": main()
