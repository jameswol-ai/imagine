"""IMAGINE AEC Engine Streamlit application shell.

The application shell is deliberately thin: it owns navigation, registry
loading, diagnostics, and error isolation. Specialist workspaces are imported
only when opened so one broken domain cannot prevent the rest of IMAGINE from
starting on Streamlit Cloud.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

import streamlit as st

st.set_page_config(
    page_title="IMAGINE | AEC Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# UI sanitization is installed here, not from modules/__init__.py. This keeps
# package imports side-effect free while preserving the emoji-free UI policy.
try:
    from modules.ui_sanitizer import install_emoji_free_ui

    install_emoji_free_ui()
except Exception:
    # The application must remain bootable even if the optional UI adapter
    # cannot be imported in an unusual deployment environment.
    pass

MODULE_SPECS: tuple[Any, ...] = ()
ModuleSpec: Any = Any
REGISTRY_IMPORT_ERROR: str | None = None


def _load_registry() -> None:
    """Load the registry without executing modules/__init__.py."""
    global MODULE_SPECS, ModuleSpec, REGISTRY_IMPORT_ERROR

    path = ROOT_DIR / "modules" / "enterprise_registry.py"
    module_name = "_imagine_enterprise_registry"

    try:
        if not path.exists():
            raise FileNotFoundError(f"Registry file not found: {path}")

        loader_spec = importlib.util.spec_from_file_location(module_name, path)
        if loader_spec is None or loader_spec.loader is None:
            raise ImportError("Unable to create registry module loader")

        module = importlib.util.module_from_spec(loader_spec)
        # dataclasses and introspection code expect the executing module to be
        # present in sys.modules while the source is being executed.
        sys.modules[module_name] = module
        try:
            loader_spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise

        ModuleSpec = module.ModuleSpec
        MODULE_SPECS = tuple(module.MODULE_SPECS)
        module.validate_registry()
        REGISTRY_IMPORT_ERROR = None
    except Exception as exc:
        REGISTRY_IMPORT_ERROR = "".join(
            traceback.format_exception_only(type(exc), exc)
        ).strip()
        MODULE_SPECS = ()


_load_registry()

SEARCH_ALIASES = {
    "projects": ("projects", "approvals", "revisions", "workflows", "governance"),
    "bim": (
        "bim dashboard", "buildings", "storeys", "spaces", "elements",
        "assemblies & types", "ifc", "cobie", "bim coordination",
        "bim quantities", "bim costing", "bim digital twin",
    ),
    "ifc": ("ifc", "bim coordination", "bim dashboard"),
    "cobie": ("cobie", "bim digital twin"),
    "boq": ("bim quantities", "bim costing", "boq", "quantity takeoff"),
    "digital twin": ("bim digital twin", "assets", "sensors", "telemetry"),
    "structural": (
        "structural engineering dashboard", "eurocode suite", "beam design",
        "column design", "slab design",
    ),
    "architecture": (
        "architecture assistant", "site planning", "zoning", "floor planning",
        "room programming", "compliance",
    ),
    "mep": (
        "integrated mep analysis", "hvac", "ventilation", "electrical load analysis",
        "water supply", "drainage",
    ),
    "cost": (
        "boq", "quantity takeoff", "procurement", "forex", "risk analysis",
        "escalation",
    ),
    "construction": (
        "planning", "scheduling", "progress tracking", "rfis", "submittals",
        "snagging", "site diaries",
    ),
    "documents": (
        "drawing management", "drawings", "document register", "specifications",
        "contracts", "transmittals",
    ),
}


# ---------------------------------------------------------------------------
# Navigation state
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "active_domain": "PLATFORM",
        "module_search": "",
        "recent_routes": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def specs(domain: str | None = None) -> list[Any]:
    return [
        spec for spec in MODULE_SPECS
        if domain is None or spec.section == domain
    ]


def spec_for(route: str) -> Any | None:
    return next((spec for spec in MODULE_SPECS if spec.route == route), None)


def set_active(route: str) -> None:
    spec = spec_for(route)
    if spec is None:
        return

    st.session_state.active_route = route
    st.session_state.active_domain = spec.section
    recent = st.session_state.get("recent_routes", [])
    st.session_state.recent_routes = [
        route,
        *[item for item in recent if item != route][:7],
    ]


def search_specs(query: str) -> list[Any]:
    normalized = " ".join(query.lower().split())
    if not normalized:
        return []

    terms = normalized.split()
    expanded: set[str] = set(terms)
    for term in terms:
        expanded.update(SEARCH_ALIASES.get(term, ()))

    found: list[tuple[float, Any]] = []
    for spec in MODULE_SPECS:
        haystack = (
            f"{spec.route} {spec.label} {spec.section} "
            f"{spec.module_path or ''}"
        ).lower()
        score = sum(term in haystack for term in terms)
        score += 0.2 * sum(term in haystack for term in expanded)
        if normalized in haystack:
            score += 8
        if score:
            found.append((score, spec))

    return [
        item
        for _, item in sorted(
            found,
            key=lambda item: (-item[0], item[1].section, item[1].label),
        )
    ]


# ---------------------------------------------------------------------------
# Runtime loading
# ---------------------------------------------------------------------------


def import_renderer(spec: Any) -> tuple[Callable | None, str | None]:
    """Import one renderer and return a concise diagnostic on failure."""
    if not spec.module_path or spec.module_path == "__builtin__":
        return None, "Built-in workspace"

    try:
        module = importlib.import_module(spec.module_path)
        renderer = getattr(module, spec.renderer_name, None)
        if not callable(renderer):
            renderer = getattr(module, "render", None)
        if not callable(renderer):
            return (
                None,
                f"RendererError: no callable '{spec.renderer_name}' or "
                f"'render' in {spec.module_path}",
            )
        return renderer, None
    except Exception as exc:
        return None, "".join(
            traceback.format_exception_only(type(exc), exc)
        ).strip()


def registry_summary() -> dict[str, int]:
    all_specs = list(MODULE_SPECS)
    implemented = [spec for spec in all_specs if spec.implemented]
    fallback = [
        spec for spec in implemented
        if spec.module_path == "modules.enterprise_missing"
    ]
    return {
        "workspaces": len(all_specs),
        "implemented": len(implemented),
        "fallback": len(fallback),
        "domains": len({spec.section for spec in all_specs}),
    }


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def inject_styles() -> None:
    st.markdown(
        """<style>
        .stApp{background:linear-gradient(135deg,#f7f9fc,#eef3f8 52%,#fbfcfe)}
        .block-container{max-width:1720px;padding-top:1rem}
        .imagine-brand-title{font-size:2rem;font-weight:950;letter-spacing:-.075em}
        .imagine-brand-subtitle{color:#718096;font-size:.7rem;margin-bottom:1rem}
        .imagine-header,.imagine-hero,.imagine-panel,.imagine-card{border:1px solid rgba(110,125,145,.16);border-radius:22px;background:rgba(255,255,255,.88);box-shadow:0 16px 42px rgba(30,50,75,.055)}
        .imagine-header{padding:1.2rem 1.35rem;margin-bottom:1rem}
        .imagine-header-title{font-size:2.25rem;font-weight:930;letter-spacing:-.06em}
        .imagine-header-subtitle{color:#687588;margin-top:.3rem}
        .imagine-hero{padding:1.5rem;margin-bottom:1rem}
        .imagine-hero-title{font-size:1.7rem;font-weight:900}
        .imagine-hero-copy{color:#647184;line-height:1.6}
        .imagine-panel{padding:1rem;margin-bottom:.75rem}
        .imagine-card{min-height:100px;padding:1rem}
        .imagine-card-title{color:#687588;font-size:.6rem;font-weight:850;text-transform:uppercase;letter-spacing:.1em}
        .imagine-card-value{font-size:1.7rem;font-weight:930;margin-top:.35rem}
        .imagine-status{display:inline-block;padding:.28rem .55rem;border-radius:999px;font-size:.65rem;font-weight:800;border:1px solid rgba(110,125,145,.18)}
        .sidebar-heading{font-size:.59rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#718096;margin:.7rem 0 .35rem}
        .sidebar-result{padding:.55rem .65rem;border:1px solid rgba(110,125,145,.14);border-radius:11px;margin:.35rem 0}
        .sidebar-result-title{font-size:.76rem;font-weight:750}
        .sidebar-result-meta{font-size:.62rem;color:#7a8697}
        .imagine-footer{margin-top:2rem;padding:1rem 0;color:#7b8796;font-size:.68rem;text-align:center;border-top:1px solid rgba(110,125,145,.12)}
        @media(prefers-color-scheme:dark){
          .stApp{background:#0a1017}
          .imagine-header,.imagine-hero,.imagine-panel,.imagine-card{background:#121b26;border-color:#293746}
          .imagine-header-title,.imagine-hero-title,.imagine-card-value,.sidebar-result-title{color:#f1f5f9}
          .imagine-header-subtitle,.imagine-hero-copy,.imagine-card-title,.sidebar-result-meta,.imagine-footer{color:#aab5c3}
          .sidebar-result{background:#111b25}
        }
        </style>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="imagine-brand-title">IMAGINE</div>'
            '<div class="imagine-brand-subtitle">Integrated Architecture, '
            'Engineering & Construction Engine</div>',
            unsafe_allow_html=True,
        )

        if not MODULE_SPECS:
            st.error("Module registry unavailable")
            if REGISTRY_IMPORT_ERROR:
                st.code(REGISTRY_IMPORT_ERROR, language="text")
            return

        domains = sorted({
            spec.section for spec in MODULE_SPECS if spec.section != "PLATFORM"
        })
        navigation = ["HOME", *domains]
        current = (
            st.session_state.active_domain
            if st.session_state.active_domain in navigation
            else "HOME"
        )

        chosen = st.selectbox(
            "Discipline",
            navigation,
            index=navigation.index(current),
        )

        if chosen != current:
            st.session_state.active_domain = chosen
            st.session_state.active_route = "Overview"
            st.rerun()

        if chosen == "HOME":
            labels = [spec.label for spec in specs("PLATFORM")]
        else:
            labels = [
                "Discipline Overview",
                *[spec.label for spec in specs(chosen)],
            ]

        active = spec_for(st.session_state.active_route)
        active_label = active.label if active else "Overview"

        if active_label not in labels:
            active_label = (
                "Discipline Overview"
                if chosen != "HOME"
                else (labels[0] if labels else "Overview")
            )

        selected = st.selectbox(
            "Workspace",
            labels or ["Overview"],
            index=labels.index(active_label) if active_label in labels else 0,
        )

        if chosen != "HOME" and selected == "Discipline Overview":
            st.session_state.active_route = "Overview"
            st.session_state.active_domain = chosen
        elif selected and selected != "Overview":
            set_active(selected)

        st.markdown(
            '<div class="sidebar-heading">Search all workspaces</div>',
            unsafe_allow_html=True,
        )
        query = st.text_input(
            "Search",
            key="module_search",
            placeholder="Search projects, BIM, IFC, EN 1992...",
            label_visibility="collapsed",
        )

        if query:
            matches = search_specs(query)
            st.markdown(
                f'<div class="sidebar-heading">Search results · {len(matches)}</div>',
                unsafe_allow_html=True,
            )
            for index, spec in enumerate(matches[:12]):
                st.markdown(
                    f'<div class="sidebar-result">'
                    f'<div class="sidebar-result-title">{spec.label}</div>'
                    f'<div class="sidebar-result-meta">{spec.section}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Open",
                    key=f"search_open_{index}_{spec.route}",
                    use_container_width=True,
                ):
                    set_active(spec.route)
                    st.rerun()

        recent_routes = st.session_state.get("recent_routes", [])
        if recent_routes:
            st.markdown(
                '<div class="sidebar-heading">Recent</div>',
                unsafe_allow_html=True,
            )
            recent = st.selectbox(
                "Recent",
                recent_routes,
                index=0,
                label_visibility="collapsed",
            )
            if recent != st.session_state.active_route:
                set_active(recent)
                st.rerun()


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------


def render_header() -> None:
    spec = spec_for(st.session_state.active_route)
    label = spec.label if spec else "Overview"
    domain = spec.section if spec else "PLATFORM"
    st.markdown(
        f'<div class="imagine-header">'
        f'<div class="imagine-header-title">{label}</div>'
        f'<div class="imagine-header-subtitle">{domain} workspace · '
        f'Connected IMAGINE AEC data environment</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    summary = registry_summary()

    st.markdown(
        '<div class="imagine-hero">'
        '<div class="imagine-hero-title">AEC Command Centre</div>'
        '<div class="imagine-hero-copy">One workspace connecting project '
        'governance, architecture, structural engineering, BIM, MEP, costing, '
        'construction and digital delivery.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    cards = [
        ("Workspaces", summary["workspaces"]),
        ("Implemented", summary["implemented"]),
        ("Fallback", summary["fallback"]),
        ("Domains", summary["domains"]),
        ("Runtime", "Ready" if not REGISTRY_IMPORT_ERROR else "Degraded"),
    ]
    for col, (title, value) in zip(cols, cards):
        col.markdown(
            f'<div class="imagine-card">'
            f'<div class="imagine-card-title">{title}</div>'
            f'<div class="imagine-card-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if REGISTRY_IMPORT_ERROR:
        st.warning(
            "The registry could not be validated. Navigation is limited until "
            "the registry error is corrected."
        )
        st.code(REGISTRY_IMPORT_ERROR, language="text")
        return

    if MODULE_SPECS:
        import pandas as pd
        import plotly.express as px

        counts = pd.Series(
            [spec.section for spec in MODULE_SPECS]
        ).value_counts()
        dataframe = counts.rename_axis("Domain").reset_index(name="Workspaces")
        st.subheader("Platform coverage")
        st.plotly_chart(
            px.bar(dataframe, x="Domain", y="Workspaces"),
            use_container_width=True,
        )

    left, right = st.columns(2)
    with left:
        st.markdown(
            '<div class="imagine-panel"><b>Projects → BIM</b><br>'
            '<small>Project → Building → Storey → Space → Element → Assembly</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="imagine-panel"><b>BIM → Delivery</b><br>'
            '<small>IFC / COBie → Coordination → Quantities → Costing → Digital Twin</small>'
            '</div>',
            unsafe_allow_html=True,
        )


def render_system_health() -> None:
    st.title("System Health")

    if REGISTRY_IMPORT_ERROR:
        st.error("Registry import failed")
        st.code(REGISTRY_IMPORT_ERROR, language="text")
        return

    import pandas as pd

    rows: list[dict[str, str]] = []
    for spec in MODULE_SPECS:
        if not spec.implemented or spec.module_path in (None, "__builtin__"):
            continue

        _, error = import_renderer(spec)
        if error is None:
            status = "Ready"
            detail = "Callable renderer found"
        else:
            status = "Error"
            detail = error

        rows.append(
            {
                "Workspace": spec.label,
                "Domain": spec.section,
                "Status": status,
                "Detail": detail,
                "Module": spec.module_path or "",
            }
        )

    frame = pd.DataFrame(rows)
    ready = int((frame["Status"] == "Ready").sum()) if not frame.empty else 0
    errors = int((frame["Status"] == "Error").sum()) if not frame.empty else 0

    a, b, c = st.columns(3)
    a.metric("Registered renderers", len(frame))
    b.metric("Ready", ready)
    c.metric("Import errors", errors)

    if errors:
        st.warning(
            "One or more registered workspaces could not be imported. "
            "Open the affected workspace for its exact traceback."
        )

    st.dataframe(frame, hide_index=True, use_container_width=True)


def render_current() -> None:
    route = st.session_state.active_route

    if route == "Overview":
        render_overview()
        return

    if route == "System Health":
        render_system_health()
        return

    spec = spec_for(route)
    if spec is None:
        st.session_state.active_route = "Overview"
        render_overview()
        return

    renderer, error = import_renderer(spec)
    if renderer is None:
        st.error(f"Unable to load {spec.label}")
        st.code(error or "Unknown renderer failure", language="text")
        st.info(
            "The application shell is still running. Use the sidebar to open "
            "another workspace or System Health to inspect the registry."
        )
        return

    try:
        renderer()
    except Exception as exc:
        st.error(f"Unable to render {spec.label}")
        st.exception(exc)
        st.info(
            "This specialist workspace failed during rendering. The rest of "
            "the IMAGINE application remains available."
        )


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_header()
    render_current()
    st.markdown(
        '<div class="imagine-footer">IMAGINE AEC Engine · Preliminary '
        'engineering/software platform · Validate project outputs against '
        'applicable standards and professional requirements.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
