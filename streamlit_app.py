"""IMAGINE AEC Engine Streamlit application shell.

The shell owns navigation, registry loading, diagnostics and error isolation.
Specialist workspaces are imported only when opened so one broken domain
cannot prevent IMAGINE from starting on Streamlit Cloud.
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

try:
    from modules.ui_sanitizer import install_emoji_free_ui
    install_emoji_free_ui()
except Exception:
    pass

MODULE_SPECS: tuple[Any, ...] = ()
ModuleSpec: Any = Any
REGISTRY_IMPORT_ERROR: str | None = None


def _load_registry() -> None:
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
        REGISTRY_IMPORT_ERROR = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        MODULE_SPECS = ()


_load_registry()

SEARCH_ALIASES = {
    "projects": ("projects", "sample project", "sample design pipeline", "approvals", "revisions", "workflows", "governance"),
    "bim": ("bim dashboard", "buildings", "storeys", "spaces", "elements", "assemblies & types", "ifc", "cobie", "bim coordination", "bim quantities", "bim costing", "bim digital twin"),
    "ifc": ("ifc", "bim coordination", "bim dashboard"),
    "cobie": ("cobie", "bim digital twin"),
    "boq": ("bim quantities", "bim costing", "boq", "quantity takeoff"),
    "digital twin": ("bim digital twin", "assets", "sensors", "telemetry"),
    "structural": ("structural engineering dashboard", "structural design basis", "eurocode suite", "eurocode worked samples", "en 1990", "en 1991", "en 1992", "en 1993", "en 1994", "en 1995", "en 1996", "en 1997", "en 1998", "en 1999", "beam design", "column design", "slab design"),
    "eurocode": ("eurocode suite", "eurocode worked samples", "en 1990", "en 1991", "en 1992", "en 1993", "en 1994", "en 1995", "en 1996", "en 1997", "en 1998", "en 1999"),
    "architecture": ("architecture assistant", "site planning", "zoning", "floor planning", "room programming", "compliance"),
    "mep": ("integrated mep analysis", "hvac", "ventilation", "electrical load analysis", "water supply", "drainage"),
    "cost": ("boq", "quantity takeoff", "procurement", "forex", "risk analysis", "escalation"),
    "construction": ("planning", "scheduling", "progress tracking", "rfis", "submittals", "snagging", "site diaries"),
    "documents": ("drawing management", "drawings", "document register", "specifications", "contracts", "transmittals"),
}


def init_session_state() -> None:
    defaults = {
        "active_route": "Overview",
        "active_domain": "PLATFORM",
        "module_search": "",
        "recent_routes": [],
        "discipline_nav": "HOME",
        "workspace_nav": "Overview",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def specs(domain: str | None = None) -> list[Any]:
    return [spec for spec in MODULE_SPECS if domain is None or spec.section == domain]


def spec_for(route: str) -> Any | None:
    return next((spec for spec in MODULE_SPECS if spec.route == route), None)


def set_active(route: str, rerun: bool = False) -> None:
    spec = spec_for(route)
    if spec is None:
        return
    st.session_state.active_route = route
    st.session_state.active_domain = spec.section
    st.session_state.discipline_nav = "HOME" if spec.section == "PLATFORM" else spec.section
    st.session_state.workspace_nav = spec.label
    recent = st.session_state.get("recent_routes", [])
    st.session_state.recent_routes = [route, *[item for item in recent if item != route][:7]]
    if rerun:
        st.rerun()


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
        haystack = f"{spec.route} {spec.label} {spec.section} {spec.module_path or ''}".lower()
        score = sum(term in haystack for term in terms)
        score += 0.2 * sum(term in haystack for term in expanded)
        if normalized in haystack:
            score += 8
        if score:
            found.append((score, spec))
    return [item for _, item in sorted(found, key=lambda item: (-item[0], item[1].section, item[1].label))]


def import_renderer(spec: Any) -> tuple[Callable | None, str | None]:
    if not spec.module_path or spec.module_path == "__builtin__":
        return None, "Built-in workspace"
    try:
        module = importlib.import_module(spec.module_path)
        renderer = getattr(module, spec.renderer_name, None)
        if not callable(renderer):
            renderer = getattr(module, "render", None)
        if not callable(renderer):
            return None, f"RendererError: no callable '{spec.renderer_name}' or 'render' in {spec.module_path}"
        return renderer, None
    except Exception as exc:
        return None, "".join(traceback.format_exception_only(type(exc), exc)).strip()


def registry_summary() -> dict[str, int]:
    all_specs = list(MODULE_SPECS)
    implemented = [spec for spec in all_specs if spec.implemented]
    fallback = [spec for spec in implemented if spec.module_path in ("modules.enterprise_missing", "modules.enterprise_workspace")]
    return {"workspaces": len(all_specs), "implemented": len(implemented), "fallback": len(fallback), "domains": len({spec.section for spec in all_specs})}


def inject_styles() -> None:
    st.markdown("""<style>
    :root { --imagine-teal:#0f766e; --imagine-deep:#102a43; --imagine-line:#d7e1e8; --imagine-surface:rgba(255,255,255,.94); }
    .stApp { background: radial-gradient(circle at 12% 0%, #e8f6f4 0, transparent 30%), linear-gradient(135deg,#f6f9fb 0%,#edf3f7 55%,#f9fbfc 100%); }
    .block-container { max-width:1720px; padding-top:1.1rem; padding-bottom:2rem; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#102a43 0%,#163b52 52%,#0e283c 100%); }
    [data-testid="stSidebar"] * { color:#edf7f7; }
    [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] [data-baseweb="select"] > div { background:rgba(255,255,255,.09); border-color:rgba(255,255,255,.18); }
    [data-testid="stSidebar"] button { border-radius:10px; }
    .imagine-brand-title { font-size:2.15rem; font-weight:950; letter-spacing:-.08em; color:#fff; }
    .imagine-brand-subtitle { color:#b8d5d8; font-size:.68rem; line-height:1.45; margin-bottom:1rem; }
    .imagine-header,.imagine-hero,.imagine-panel,.imagine-card { border:1px solid var(--imagine-line); border-radius:18px; background:var(--imagine-surface); box-shadow:0 12px 34px rgba(16,42,67,.07); }
    .imagine-header { padding:1.15rem 1.3rem; margin-bottom:1rem; border-top:3px solid var(--imagine-teal); }
    .imagine-header-title { font-size:2.1rem; font-weight:900; letter-spacing:-.055em; color:var(--imagine-deep); }
    .imagine-header-subtitle { color:#607487; margin-top:.25rem; font-size:.82rem; }
    .imagine-hero { padding:1.45rem; margin-bottom:1rem; }
    .imagine-hero-title { font-size:1.65rem; font-weight:900; color:var(--imagine-deep); }
    .imagine-hero-copy { color:#5e7182; line-height:1.6; }
    .imagine-panel { padding:1rem; margin-bottom:.75rem; }
    .imagine-card { min-height:94px; padding:1rem; }
    .imagine-card-title { color:#688091; font-size:.58rem; font-weight:850; text-transform:uppercase; letter-spacing:.1em; }
    .imagine-card-value { font-size:1.65rem; font-weight:930; margin-top:.35rem; color:var(--imagine-deep); }
    .sidebar-heading { font-size:.58rem; font-weight:850; letter-spacing:.12em; text-transform:uppercase; color:#9fc5c8; margin:.85rem 0 .35rem; }
    .sidebar-result { padding:.5rem .62rem; border:1px solid rgba(255,255,255,.13); border-radius:10px; margin:.3rem 0; background:rgba(255,255,255,.045); }
    .sidebar-result-title { font-size:.75rem; font-weight:750; }
    .sidebar-result-meta { font-size:.6rem; color:#a9c2c9; }
    .imagine-footer { margin-top:2rem; padding:1rem 0; color:#718392; font-size:.66rem; text-align:center; border-top:1px solid var(--imagine-line); }
    @media (prefers-color-scheme:dark) {
      .stApp { background:#09141f; }
      .imagine-header,.imagine-hero,.imagine-panel,.imagine-card { background:#111e2a; border-color:#293b4b; }
      .imagine-header-title,.imagine-hero-title,.imagine-card-value { color:#edf5f7; }
      .imagine-header-subtitle,.imagine-hero-copy,.imagine-card-title,.imagine-footer { color:#a8b9c5; }
    }
    </style>""", unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div>', unsafe_allow_html=True)
        if not MODULE_SPECS:
            st.error("Module registry unavailable")
            if REGISTRY_IMPORT_ERROR:
                st.code(REGISTRY_IMPORT_ERROR, language="text")
            return

        domain_order = ["PROJECTS", "ARCHITECTURE", "STRUCTURAL", "BIM", "MEP", "COSTING", "CONSTRUCTION", "DOCUMENTS", "AI", "ANALYTICS", "REGIONAL", "INTEGRATIONS", "DIGITAL TWIN"]
        domains = [domain for domain in domain_order if any(spec.section == domain for spec in MODULE_SPECS)]
        navigation = ["HOME", *domains]
        current_domain = st.session_state.get("discipline_nav", "HOME")
        if current_domain not in navigation:
            current_domain = "HOME"
        chosen = st.selectbox("Discipline", navigation, index=navigation.index(current_domain), key="discipline_nav")

        if chosen != current_domain:
            if chosen == "HOME":
                set_active("Overview")
            else:
                domain_specs = specs(chosen)
                first = domain_specs[0].route if domain_specs else "Overview"
                set_active(first)
            st.rerun()

        if chosen == "HOME":
            labels = [spec.label for spec in specs("PLATFORM")]
        else:
            labels = [spec.label for spec in specs(chosen)]

        active = spec_for(st.session_state.active_route)
        active_label = active.label if active and active.section == chosen else (labels[0] if labels else "Overview")
        if active_label not in labels and labels:
            active_label = labels[0]

        selected = st.selectbox("Workspace", labels or ["Overview"], index=labels.index(active_label) if active_label in labels else 0, key="workspace_nav")
        if selected and selected != st.session_state.active_route:
            set_active(selected)
            st.rerun()

        st.markdown('<div class="sidebar-heading">Search all workspaces</div>', unsafe_allow_html=True)
        query = st.text_input("Search", key="module_search", placeholder="Search projects, BIM, EN 1993, foundations...", label_visibility="collapsed")
        if query:
            matches = search_specs(query)
            st.markdown(f'<div class="sidebar-heading">Search results · {len(matches)}</div>', unsafe_allow_html=True)
            for index, spec in enumerate(matches[:12]):
                st.markdown(f'<div class="sidebar-result"><div class="sidebar-result-title">{spec.label}</div><div class="sidebar-result-meta">{spec.section}</div></div>', unsafe_allow_html=True)
                if st.button("Open", key=f"search_open_{index}_{spec.route}", use_container_width=True):
                    set_active(spec.route, rerun=True)

        recent_routes = st.session_state.get("recent_routes", [])
        if recent_routes:
            st.markdown('<div class="sidebar-heading">Recent workspaces</div>', unsafe_allow_html=True)
            recent = st.selectbox("Recent", recent_routes, index=0, label_visibility="collapsed", key="recent_workspace_nav")
            if recent != st.session_state.active_route:
                set_active(recent, rerun=True)


def render_header() -> None:
    spec = spec_for(st.session_state.active_route)
    label = spec.label if spec else "Overview"
    domain = spec.section if spec else "PLATFORM"
    st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{label}</div><div class="imagine-header-subtitle">{domain} workspace · Connected IMAGINE AEC data environment</div></div>', unsafe_allow_html=True)


def render_overview() -> None:
    summary = registry_summary()
    st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">AEC Command Centre</div><div class="imagine-hero-copy">One workspace connecting project governance, architecture, structural engineering, BIM, MEP, costing, construction and digital delivery.</div></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    cards = [("Workspaces",summary["workspaces"]),("Implemented",summary["implemented"]),("Fallback",summary["fallback"]),("Domains",summary["domains"]),("Runtime","Ready" if not REGISTRY_IMPORT_ERROR else "Degraded")]
    for col,(title,value) in zip(cols,cards):
        col.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{value}</div></div>', unsafe_allow_html=True)
    if REGISTRY_IMPORT_ERROR:
        st.warning("The registry could not be validated. Navigation is limited until the registry error is corrected.")
        st.code(REGISTRY_IMPORT_ERROR, language="text")
        return
    if MODULE_SPECS:
        import pandas as pd
        import plotly.express as px
        counts = pd.Series([spec.section for spec in MODULE_SPECS]).value_counts()
        dataframe = counts.rename_axis("Domain").reset_index(name="Workspaces")
        st.subheader("Platform coverage")
        st.plotly_chart(px.bar(dataframe, x="Domain", y="Workspaces"), use_container_width=True)
    left,right = st.columns(2)
    with left: st.markdown('<div class="imagine-panel"><b>Projects → BIM</b><br><small>Project → Building → Storey → Space → Element → Assembly</small></div>', unsafe_allow_html=True)
    with right: st.markdown('<div class="imagine-panel"><b>BIM → Delivery</b><br><small>IFC / COBie → Coordination → Quantities → Costing → Digital Twin</small></div>', unsafe_allow_html=True)


def render_system_health() -> None:
    st.title("System Health")
    if REGISTRY_IMPORT_ERROR:
        st.error("Registry import failed"); st.code(REGISTRY_IMPORT_ERROR, language="text"); return
    import pandas as pd
    rows=[]
    for spec in MODULE_SPECS:
        if not spec.implemented or spec.module_path in (None,"__builtin__"): continue
        _,error=import_renderer(spec)
        rows.append({"Workspace":spec.label,"Domain":spec.section,"Status":"Ready" if error is None else "Error","Detail":"Callable renderer found" if error is None else error,"Module":spec.module_path or ""})
    frame=pd.DataFrame(rows)
    ready=int((frame["Status"]=="Ready").sum()) if not frame.empty else 0
    errors=int((frame["Status"]=="Error").sum()) if not frame.empty else 0
    a,b,c=st.columns(3); a.metric("Registered renderers",len(frame)); b.metric("Ready",ready); c.metric("Import errors",errors)
    if errors: st.warning("One or more registered workspaces could not be imported. Open the affected workspace for its exact traceback.")
    st.dataframe(frame,hide_index=True,use_container_width=True)


def render_current() -> None:
    route=st.session_state.active_route
    if route=="Overview": render_overview(); return
    if route=="System Health": render_system_health(); return
    spec=spec_for(route)
    if spec is None:
        set_active("Overview"); return
    renderer,error=import_renderer(spec)
    if renderer is None:
        st.error(f"Unable to load {spec.label}"); st.code(error or "Unknown renderer failure", language="text"); st.info("The application shell is still running. Use the sidebar to open another workspace or System Health to inspect the registry."); return
    try:
        renderer()
    except Exception as exc:
        st.error(f"Unable to render {spec.label}"); st.exception(exc); st.info("This specialist workspace failed during rendering. The rest of the IMAGINE application remains available.")


def main() -> None:
    init_session_state()
    inject_styles()
    render_sidebar()
    render_header()
    render_current()
    st.markdown('<div class="imagine-footer">IMAGINE AEC Engine · Preliminary engineering/software platform · Validate project outputs against applicable standards and professional requirements.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
