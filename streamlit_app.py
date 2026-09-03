"""IMAGINE AEC Engine Streamlit application shell.

The shell provides a compact enterprise workspace without rendering the
entire module catalog in the sidebar. Users navigate by domain and search
for modules globally. Renderers remain lazy-loaded and isolated so one broken
module cannot take down the application.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable

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
    "PLATFORM": "Enterprise workspace and diagnostics.",
    "PROJECTS": "Project lifecycle, approvals, revisions, workflows and governance.",
    "ARCHITECTURE": "Zoning, site planning, floor planning, programming and generative design.",
    "STRUCTURAL": "Structural engineering workflows and Eurocode design.",
    "BIM": "Buildings, storeys, spaces, elements and OpenBIM.",
    "MEP": "Mechanical, electrical and plumbing engineering.",
    "COSTING": "BOQ, quantity takeoff, procurement and financial analysis.",
    "CONSTRUCTION": "Planning, scheduling, RFIs, submittals and site management.",
    "DOCUMENTS": "Drawings, documents, specifications, contracts and revision control.",
    "AI": "Architecture, engineering, MEP, QS and project management AI.",
    "ANALYTICS": "Portfolio analytics, KPIs, forecasting and reporting.",
    "REGIONAL": "Regional codes, regulations and zoning requirements.",
    "INTEGRATIONS": "AEC software, GIS, cloud and interoperability integrations.",
    "DIGITAL TWIN": "Assets, sensors, telemetry, maintenance and predictive AI.",
}


SECTION_ORDER = (
    "PLATFORM",
    "PROJECTS",
    "ARCHITECTURE",
    "STRUCTURAL",
    "BIM",
    "MEP",
    "COSTING",
    "CONSTRUCTION",
    "DOCUMENTS",
    "AI",
    "ANALYTICS",
    "REGIONAL",
    "INTEGRATIONS",
    "DIGITAL TWIN",
)


@st.cache_data(show_spinner=False)
def registry_snapshot() -> tuple[ModuleSpec, ...]:
    """Return the immutable module catalog after validation."""
    validate_registry()
    return MODULE_SPECS


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f7fa; }
        .block-container {
            max-width: 1550px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        section[data-testid="stSidebar"] {
            width: 320px !important;
            background: #ffffff;
            border-right: 1px solid #dfe4ea;
        }
        section[data-testid="stSidebar"] > div { padding-top: 1rem; }
        section[data-testid="stSidebar"] .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .imagine-sidebar-brand { padding: 0.4rem 0.25rem 0.9rem; }
        .imagine-sidebar-brand-title {
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            color: #162033;
        }
        .imagine-sidebar-brand-subtitle {
            margin-top: 0.3rem;
            color: #687386;
            font-size: 0.76rem;
            line-height: 1.45;
        }
        .imagine-sidebar-label {
            margin-top: 0.8rem;
            margin-bottom: 0.35rem;
            color: #697587;
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }
        .imagine-sidebar-status {
            margin-top: 1rem;
            padding: 0.8rem;
            border: 1px solid #dfe4ea;
            border-radius: 9px;
            background: #f8fafc;
        }
        .imagine-sidebar-status-title {
            color: #687386;
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .imagine-sidebar-status-value {
            margin-top: 0.25rem;
            color: #172033;
            font-size: 0.84rem;
            font-weight: 700;
        }
        .imagine-header { margin-bottom: 1.2rem; }
        .imagine-header-title {
            margin: 0;
            color: #172033;
            font-size: 2.15rem;
            line-height: 1.1;
            font-weight: 800;
            letter-spacing: -0.04em;
        }
        .imagine-header-subtitle {
            margin-top: 0.4rem;
            color: #687386;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .imagine-breadcrumb {
            display: inline-block;
            margin-top: 0.85rem;
            padding: 0.38rem 0.7rem;
            border: 1px solid #dfe4ea;
            border-radius: 7px;
            background: #eef2f6;
            color: #566276;
            font-size: 0.75rem;
        }
        .imagine-card {
            min-height: 118px;
            padding: 1.05rem;
            border: 1px solid #dfe4ea;
            border-radius: 10px;
            background: #ffffff;
        }
        .imagine-card-title {
            color: #687386;
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }
        .imagine-card-value {
            margin-top: 0.45rem;
            color: #172033;
            font-size: 1.65rem;
            font-weight: 800;
        }
        .imagine-card-description {
            margin-top: 0.25rem;
            color: #7b8798;
            font-size: 0.75rem;
        }
        .imagine-module-panel {
            margin-bottom: 1rem;
            padding: 1.25rem 1.35rem;
            border: 1px solid #dfe4ea;
            border-radius: 10px;
            background: #ffffff;
        }
        .imagine-module-title {
            color: #172033;
            font-size: 1.3rem;
            font-weight: 760;
        }
        .imagine-module-description {
            margin-top: 0.35rem;
            color: #687386;
            font-size: 0.86rem;
            line-height: 1.5;
        }
        div.stButton > button {
            min-height: 2.35rem;
            border-radius: 7px;
            font-weight: 650;
        }
        .imagine-footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #dfe4ea;
            color: #8791a0;
            font-size: 0.72rem;
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background: #0d131b; }
            section[data-testid="stSidebar"] {
                background: #111821;
                border-right-color: #293441;
            }
            .imagine-sidebar-brand-title,
            .imagine-header-title,
            .imagine-card-value,
            .imagine-module-title,
            .imagine-sidebar-status-value { color: #f1f4f8; }
            .imagine-sidebar-brand-subtitle,
            .imagine-header-subtitle,
            .imagine-module-description,
            .imagine-card-description { color: #a5afbd; }
            .imagine-sidebar-status {
                background: #151d27;
                border-color: #2b3745;
            }
            .imagine-sidebar-status-title,
            .imagine-card-title { color: #a5afbd; }
            .imagine-breadcrumb {
                background: #1a2330;
                border-color: #2b3745;
                color: #b8c1ce;
            }
            .imagine-card,
            .imagine-module-panel {
                background: #141b24;
                border-color: #2b3745;
            }
            .imagine-footer {
                border-top-color: #2b3745;
                color: #7e8998;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "module_search": "",
        "module_search_domain": "All domains",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def specs_for_section(section: str) -> list[ModuleSpec]:
    return [spec for spec in registry_snapshot() if spec.section == section]


def search_specs(query: str, section: str) -> list[ModuleSpec]:
    normalized = query.strip().casefold()
    candidates = registry_snapshot()
    if section != "All domains":
        candidates = tuple(spec for spec in candidates if spec.section == section)
    if not normalized:
        return []
    terms = normalized.split()
    scored: list[tuple[int, ModuleSpec]] = []
    for spec in candidates:
        haystack = " ".join(
            [spec.route, spec.label, spec.section, spec.module_path or ""]
        ).casefold()
        if all(term in haystack for term in terms):
            score = 0
            if spec.label.casefold().startswith(normalized):
                score += 100
            if spec.section.casefold() == normalized:
                score += 50
            score += max(0, 30 - len(spec.label))
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
            <div class="imagine-sidebar-brand">
                <div class="imagine-sidebar-brand-title">IMAGINE</div>
                <div class="imagine-sidebar-brand-subtitle">
                    Integrated Architecture, Engineering & Construction Engine
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown(
            '<div class="imagine-sidebar-label">Search Modules</div>',
            unsafe_allow_html=True,
        )
        st.text_input(
            "Search modules",
            key="module_search",
            placeholder="Search projects, zoning, beam design...",
            label_visibility="collapsed",
        )

        domain_options = ["All domains", *SECTION_ORDER]
        st.selectbox(
            "Search domain",
            options=domain_options,
            key="module_search_domain",
            label_visibility="collapsed",
        )

        query = st.session_state.module_search.strip()
        if query:
            matches = search_specs(query, st.session_state.module_search_domain)
            st.caption(f"{len(matches)} module result(s)")
            if not matches:
                st.info("No matching modules found.")
            else:
                for spec in matches[:12]:
                    status = "Ready" if spec.implemented else "Registered"
                    label = f"{spec.label}  ·  {spec.section}"
                    if st.button(
                        label,
                        key=f"search_result_{spec.route}",
                        use_container_width=True,
                    ):
                        set_active_route(spec.route)
                        st.rerun()
        else:
            st.caption("Search is global. Enter a module name, discipline, or keyword.")

        st.divider()
        st.markdown(
            '<div class="imagine-sidebar-label">Current Workspace</div>',
            unsafe_allow_html=True,
        )

        active = next(
            (spec for spec in registry_snapshot() if spec.route == st.session_state.active_route),
            registry_snapshot()[0],
        )

        st.markdown(
            f"**{active.label}**  \n"
            f"{active.section}  ·  {'Ready' if active.implemented else 'Registered'}"
        )

        st.divider()
        st.markdown(
            f"""
            <div class="imagine-sidebar-status">
                <div class="imagine-sidebar-status-title">Navigation Status</div>
                <div class="imagine-sidebar-status-value">Search-driven navigation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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


def render_overview() -> None:
    render_header(
        "IMAGINE",
        "Integrated Architecture, Engineering & Construction Engine",
        "Overview / Enterprise Workspace",
    )

    project_count = 0
    active_count = 0
    completed_count = 0
    database_status = "Not checked"

    try:
        from database.bootstrap import database_health
        health = database_health()
        database_status = "Connected" if health.get("ok") else "Unavailable"
    except Exception:
        database_status = "Unavailable"

    try:
        from projects.projects.service import ProjectService
        projects = ProjectService.get_all_sync()
        project_count = len(projects)
        active_count = sum(1 for project in projects if str(project.status).lower().endswith("active"))
        completed_count = sum(1 for project in projects if str(project.status).lower().endswith("completed"))
    except Exception:
        projects = []

    cards = [
        ("Registered Modules", len(registry_snapshot()), "Searchable enterprise catalog"),
        ("Projects", project_count, "Database project records"),
        ("Active Projects", active_count, "Current project portfolio"),
        ("Database", database_status, "Runtime database status"),
    ]

    columns = st.columns(4)
    for column, (title, value, description) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="imagine-card">
                    <div class="imagine-card-title">{title}</div>
                    <div class="imagine-card-value">{value}</div>
                    <div class="imagine-card-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown(
            """
            <div class="imagine-module-panel">
                <div class="imagine-module-title">Enterprise Workspace</div>
                <div class="imagine-module-description">
                    The sidebar now uses search-driven module discovery. The long
                    module list has been removed from the sidebar while the full
                    enterprise catalog remains registered and searchable.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Project Portfolio")
        if projects:
            for project in projects[:10]:
                st.write(
                    f"**{project.name}**  |  {project.status.value if hasattr(project.status, 'value') else project.status}"
                )
        else:
            st.info("No database project records are currently available.")

    with right:
        st.markdown("### Domains")
        for section in SECTION_ORDER:
            specs = specs_for_section(section)
            ready = sum(1 for spec in specs if spec.implemented)
            st.write(f"**{section}**  |  {ready}/{len(specs)} connected")
            st.caption(DOMAIN_DESCRIPTIONS.get(section, ""))


def render_system_health() -> None:
    render_header(
        "System Health",
        "Module availability, registry validation and database diagnostics",
        "Platform / System Health",
    )

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

    a, b, c = st.columns(3)
    a.metric("Registered Modules", len(registry_snapshot()))
    b.metric("Registry", "Healthy" if registry_ok else "Failed")
    c.metric("Database", "Connected" if db_health.get("ok") else "Unavailable")

    if not registry_ok:
        st.error(registry_error)

    if db_health.get("ok"):
        st.success("Database connectivity check passed.")
    else:
        st.warning(db_health.get("error", "Database connectivity check failed."))

    st.divider()
    st.markdown("### Registered Modules")
    rows = []
    for spec in registry_snapshot():
        rows.append(
            {
                "Module": spec.label,
                "Domain": spec.section,
                "Status": "Ready" if spec.implemented else "Registered",
                "Renderer": spec.module_path or "Pending",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


def load_renderer(spec: ModuleSpec) -> Callable[[], object]:
    if not spec.module_path or spec.module_path == "__builtin__":
        raise AttributeError(f"No external renderer is configured for {spec.route}.")
    module = importlib.import_module(spec.module_path)
    renderer = getattr(module, spec.renderer_name, None)
    if renderer is None:
        renderer = getattr(module, "render", None)
    if not callable(renderer):
        raise AttributeError(
            f"Module '{spec.module_path}' does not expose a callable renderer."
        )
    return renderer


def render_placeholder(spec: ModuleSpec) -> None:
    render_header(
        spec.label,
        f"{spec.section} workspace",
        f"{spec.section} / {spec.label}",
    )
    st.markdown(
        f"""
        <div class="imagine-module-panel">
            <div class="imagine-module-title">Module Registered</div>
            <div class="imagine-module-description">
                {spec.label} is present in the enterprise registry and remains
                searchable, but its dedicated renderer is not connected yet.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    render_header(
        spec.label,
        f"IMAGINE {spec.section.title()} Workspace",
        f"{spec.section} / {spec.label}",
    )

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
            st.code(
                f"Domain: {spec.section}\n"
                f"Module: {spec.label}\n"
                f"Python module: {spec.module_path}\n"
                f"Renderer: {spec.renderer_name}"
            )
            st.exception(exc)


def render_footer() -> None:
    st.markdown(
        """
        <div class="imagine-footer">
            IMAGINE AEC Engine | Integrated Architecture, Engineering & Construction Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    init_session_state()
    render_sidebar()
    render_selected_module(st.session_state.active_route)
    render_footer()


if __name__ == "__main__":
    main()
