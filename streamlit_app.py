"""IMAGINE AEC Engine Streamlit application shell."""
from __future__ import annotations
import importlib, sys, time
from pathlib import Path
from typing import Callable
import pandas as pd
import plotly.express as px
import streamlit as st
from modules.enterprise_registry import MODULE_SPECS, ModuleSpec, validate_registry
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path: sys.path.insert(0, str(ROOT_DIR))
st.set_page_config(page_title="IMAGINE | AEC Engine", page_icon=None, layout="wide", initial_sidebar_state="expanded")
SEARCH_ALIASES = {
    "structural": ("structural design handbook", "building materials", "eurocode suite", "beam design", "column design", "slab design", "stairs design", "openings design", "railings & balustrades", "structural analysis"),
    "concrete": ("beam", "column", "slab", "foundation", "punching", "en 1992", "building materials"), "rc": ("beam", "column", "slab", "foundation", "punching", "en 1992"),
    "steel": ("steel members", "steel connections", "section shapes", "en 1993"), "timber": ("en 1995", "roof design", "building materials"), "masonry": ("en 1996", "building materials"),
    "aluminium": ("en 1999", "building materials"), "aluminum": ("en 1999", "building materials"), "geotechnical": ("en 1997", "foundation design", "retaining walls"), "seismic": ("en 1998", "structural analysis"),
    "composite": ("en 1994", "steel members", "beam design", "slab design"), "materials": ("building materials", "concrete", "steel", "timber", "masonry", "aluminium"), "building material": ("building materials",),
    "handbook": ("structural design handbook", "architectural design handbook"), "eurocode": tuple(f"en 199{i}" for i in range(0, 10)) + ("eurocode suite",), "analysis": ("structural analysis", "finite element analysis"),
    "architecture": ("architecture assistant", "design standards", "architectural design handbook", "zoning", "site planning", "floor planning", "room programming", "compliance", "generative design"),
    "stairs": ("stairs design", "architecture", "compliance"), "stair": ("stairs design", "architecture", "compliance"), "opening": ("openings design", "beam design", "architecture"), "openings": ("openings design", "beam design", "architecture"),
    "railing": ("railings & balustrades", "architecture"), "railings": ("railings & balustrades", "architecture"), "bim": ("buildings", "storeys", "spaces", "elements", "ifc", "cobie", "digital twin"),
    "mep": ("integrated mep analysis", "hvac", "ventilation", "chilled water", "electrical load analysis", "water supply", "drainage"), "cost": ("boq", "quantity takeoff", "procurement", "forex", "inflation / escalation", "risk analysis"),
    "construction": ("planning", "scheduling", "rfis", "submittals", "snagging", "site diaries"), "documents": ("drawing management", "document register", "specifications", "contracts", "version control", "transmittals"), "files": ("project files", "file center", "documents", "drawings", "bim"),
}
def registry_snapshot() -> tuple[ModuleSpec, ...]: validate_registry(); return MODULE_SPECS
def init_session_state() -> None:
    defaults={"active_route":"Overview","module_search":"","module_search_domain":"All domains","active_domain":"PLATFORM","recent_routes":[],"selected_project_id":None,"selected_project_name":None,"last_route_load_ms":None}
    for k,v in defaults.items(): st.session_state.setdefault(k,v)
def inject_styles() -> None:
    st.markdown("""<style>.stApp{background:linear-gradient(135deg,#f7f9fc,#eef3f8 55%,#f8fafc)}.block-container{max-width:1600px;padding-top:.8rem;padding-bottom:3rem}.imagine-brand-title{font-size:1.8rem;font-weight:900;letter-spacing:-.06em}.imagine-brand-subtitle{color:#687588;font-size:.74rem;line-height:1.45}.imagine-header,.imagine-nav,.imagine-hero,.imagine-panel,.imagine-card{border:1px solid rgba(120,135,155,.18);border-radius:18px;background:rgba(255,255,255,.82);box-shadow:0 12px 35px rgba(35,55,80,.06)}.imagine-header{padding:1.15rem 1.3rem;margin-bottom:.9rem}.imagine-header-title{font-size:2.15rem;font-weight:900;letter-spacing:-.05em}.imagine-header-subtitle{color:#687588;margin-top:.35rem}.imagine-breadcrumb{display:inline-block;margin-top:.65rem;padding:.28rem .6rem;border-radius:999px;background:#f1f4f7;color:#566276;font-size:.68rem}.imagine-nav{padding:.85rem 1rem;margin-bottom:1rem}.imagine-nav-title,.imagine-label{font-size:.62rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#687588}.imagine-nav-subtitle{font-size:.75rem;color:#7a8697;margin:.3rem 0 .65rem}.imagine-hero{padding:1.35rem;margin-bottom:1rem}.imagine-hero-title{font-size:1.45rem;font-weight:850}.imagine-hero-copy{color:#647184;line-height:1.6;margin-top:.35rem}.imagine-panel{padding:1rem;margin-bottom:.7rem}.imagine-panel-title{font-weight:800}.imagine-panel-description{color:#687588;font-size:.76rem;margin-top:.25rem}.imagine-card{min-height:100px;padding:1rem}.imagine-card-title{color:#687588;font-size:.62rem;font-weight:850;letter-spacing:.09em;text-transform:uppercase}.imagine-card-value{font-size:1.4rem;font-weight:900;margin-top:.35rem}.imagine-card-description{color:#7a8697;font-size:.7rem}.imagine-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(120,135,155,.2);color:#8792a1;font-size:.67rem}@media(prefers-color-scheme:dark){.stApp{background:#0b1118}.imagine-header,.imagine-nav,.imagine-hero,.imagine-panel,.imagine-card{background:rgba(19,28,39,.88);border-color:#293746}.imagine-header-title,.imagine-hero-title,.imagine-card-value,.imagine-panel-title{color:#f1f5f9}.imagine-header-subtitle,.imagine-hero-copy,.imagine-panel-description,.imagine-card-description,.imagine-nav-subtitle,.imagine-brand-subtitle{color:#aab5c3}.imagine-breadcrumb{background:#17212c;border-color:#2b3948;color:#b9c4d1}}</style>""",unsafe_allow_html=True)
def spec_for_route(route:str)->ModuleSpec|None:return next((s for s in registry_snapshot() if s.route==route),None)
def domains()->list[str]:return sorted({s.section for s in registry_snapshot()})
def domain_specs(domain:str)->list[ModuleSpec]:return [s for s in registry_snapshot() if s.section==domain]
def search_specs(query:str,domain:str="All domains")->list[ModuleSpec]:
    normalized=" ".join(query.casefold().split())
    if not normalized:return []
    candidates=[s for s in registry_snapshot() if domain=="All domains" or s.section==domain]; terms=normalized.split(); expanded=set(terms)
    for t in terms: expanded.update(SEARCH_ALIASES.get(t,()))
    scored=[]
    for s in candidates:
        hay=" ".join((s.route,s.label,s.section,s.module_path or "")).casefold(); direct=sum(t in hay for t in terms); alias=sum(t in hay for t in expanded); phrase=normalized in hay
        if not(direct or alias or phrase):continue
        score=direct*80+alias*15+(100 if s.implemented else 0)+(120 if phrase else 0)
        if normalized in {s.route.casefold(),s.label.casefold()}:score+=180
        elif normalized in s.label.casefold():score+=80
        scored.append((score,s))
    return [s for _,s in sorted(scored,key=lambda x:(-x[0],x[1].section,x[1].label))]
def set_active_route(route:str)->None:
    s=spec_for_route(route)
    if not s:return
    st.session_state.active_route=route; st.session_state.active_domain=s.section
    recent=[r for r in st.session_state.recent_routes if r!=route]; st.session_state.recent_routes=[route,*recent][:6]
def load_renderer(spec:ModuleSpec)->Callable[[],object]:
    if not spec.module_path or spec.module_path=="__builtin__":raise AttributeError(f"No external renderer is configured for {spec.route}.")
    m=importlib.import_module(spec.module_path); r=getattr(m,spec.renderer_name,None) or getattr(m,"render",None)
    if not callable(r):raise AttributeError(f"Module '{spec.module_path}' does not expose a callable renderer.")
    return r
def probe_renderers()->list[dict[str,str]]:
    rows=[]
    for s in registry_snapshot():
        if not s.implemented or not s.module_path or s.module_path=="__builtin__":continue
        try:
            m=importlib.import_module(s.module_path); r=getattr(m,s.renderer_name,None) or getattr(m,"render",None); rows.append({"Module":s.label,"Domain":s.section,"Status":"Ready" if callable(r) else "Missing renderer","Detail":"Callable renderer found" if callable(r) else f"Expected {s.renderer_name}"})
        except Exception as exc:rows.append({"Module":s.label,"Domain":s.section,"Status":"Import error","Detail":f"{type(exc).__name__}: {exc}"})
    return rows
def render_sidebar()->None:
    with st.sidebar:
        st.markdown('<div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div>',unsafe_allow_html=True); st.divider(); st.markdown('<div class="imagine-label">Workspace search</div>',unsafe_allow_html=True)
        st.text_input("Search modules",key="module_search",placeholder="Search stairs, openings, railings, EN 1992, BIM...",label_visibility="collapsed")
        opts=["All domains",*domains()]
        if st.session_state.module_search_domain not in opts:st.session_state.module_search_domain="All domains"
        st.selectbox("Search domain",opts,key="module_search_domain"); st.caption("Browse disciplines with the dropdown menu bar. Search when you already know the workspace.")
def render_navigation()->None:
    st.markdown('<div class="imagine-nav"><div class="imagine-nav-title">IMAGINE Module Menu</div><div class="imagine-nav-subtitle">Select a discipline, then select a workspace from its dropdown.</div></div>',unsafe_allow_html=True)
    labels=["HOME" if d=="PLATFORM" else d for d in domains()]; current="HOME" if st.session_state.active_domain=="PLATFORM" else st.session_state.active_domain
    if current not in labels:current="HOME"
    c1,c2,c3=st.columns([1.2,2.4,1])
    with c1:selected=st.selectbox("Discipline",labels,index=labels.index(current),key="module_menu_domain",label_visibility="collapsed")
    domain="PLATFORM" if selected=="HOME" else selected; pages=domain_specs(domain); page_labels=[p.label+("" if p.implemented else " · Registered") for p in pages]; active=st.session_state.active_route; idx=next((i for i,p in enumerate(pages) if p.route==active),0)
    with c2:page=st.selectbox("Workspace",page_labels,index=idx,key=f"module_menu_page_{domain}",label_visibility="collapsed")
    chosen=pages[page_labels.index(page)] if pages else None
    with c3:st.caption(f"{domain}\n{'Ready' if chosen and chosen.implemented else 'Registered'}")
    if chosen and chosen.route!=active:set_active_route(chosen.route);st.rerun()
def render_header(title:str,subtitle:str,breadcrumb:str)->None:st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{title}</div><div class="imagine-header-subtitle">{subtitle}</div><div class="imagine-breadcrumb">{breadcrumb}</div></div>',unsafe_allow_html=True)
def render_workspace_controls()->None:
    active=st.session_state.active_route;a,b,c=st.columns([1.1,1.5,1.1])
    with a:
        if active!="Overview" and st.button("Back to Overview",use_container_width=True):set_active_route("Overview");st.rerun()
    with b:
        recent=[r for r in st.session_state.recent_routes if r!=active and spec_for_route(r)]
        if recent:
            choice=st.selectbox("Recent workspace",["Select recent workspace",*recent],key="recent_workspace")
            if choice!="Select recent workspace":set_active_route(choice);st.rerun()
    with c:st.caption(f"Active: {active}")
def render_search_results()->None:
    q=st.session_state.module_search.strip();matches=search_specs(q,st.session_state.module_search_domain);st.subheader("Workspace Search");st.caption(f"{len(matches)} result(s) for '{q}'")
    if not matches:st.info("No matching workspace. Try stairs, openings, railings, beam, EN 1992, handbook, materials, BIM or a discipline name.");return
    cols=st.columns(3)
    for i,s in enumerate(matches[:30]):
        with cols[i%3]:
            st.markdown(f'<div class="imagine-panel"><div class="imagine-panel-title">{s.label}</div><div class="imagine-panel-description">{s.section} · {"Ready" if s.implemented else "Registered"}</div></div>',unsafe_allow_html=True)
            if s.implemented and st.button("Open workspace",key=f"search_open_{s.route}",use_container_width=True):set_active_route(s.route);st.session_state.module_search="";st.rerun()
def render_overview()->None:
    specs=registry_snapshot();ready=sum(s.implemented for s in specs);coverage=round(100*ready/len(specs),1);render_header("IMAGINE","Integrated Architecture, Engineering & Construction Engine","Home / Enterprise Workspace");render_workspace_controls()
    st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">Design. Engineer. Build. Operate.</div><div class="imagine-hero-copy">A unified workspace for architecture, structural engineering, BIM, MEP, cost, construction, documents, AI and operational intelligence.</div></div>',unsafe_allow_html=True)
    cards=[("Workspaces",len(specs),"Central registry"),("Ready",ready,f"{coverage}% registry coverage"),("Structural tools",sum(s.section=="STRUCTURAL" and s.implemented for s in specs),"Design workspaces"),("Domains",len(domains()),"Enterprise disciplines")];cols=st.columns(4)
    for i,(t,v,d) in enumerate(cards):
        with cols[i]:st.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{t}</div><div class="imagine-card-value">{v}</div><div class="imagine-card-description">{d}</div></div>',unsafe_allow_html=True)
    rows=[]
    for d in domains():
        group=[s for s in specs if s.section==d];r=sum(s.implemented for s in group);rows.append({"Domain":d,"Ready":r,"Registered":len(group),"Coverage %":round(100*r/len(group),1)})
    df=pd.DataFrame(rows);left,right=st.columns([1.1,1])
    with left:st.dataframe(df,use_container_width=True,hide_index=True)
    with right:fig=px.bar(df,x="Domain",y="Coverage %",height=360);fig.update_layout(margin=dict(l=10,r=10,t=15,b=90),xaxis_tickangle=-35);st.plotly_chart(fig,use_container_width=True)
def render_system_health()->None:
    render_header("System Health","Registry, renderer and runtime diagnostics","Platform / System Health");validate_registry();rows=probe_renderers();a,b,c=st.columns(3);a.metric("Registered",len(registry_snapshot()));b.metric("Ready",sum(s.implemented for s in registry_snapshot()));c.metric("Registry","Healthy");st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True) if rows else st.info("No external renderers available to probe.")
def render_placeholder(spec:ModuleSpec)->None:render_header(spec.label,f"{spec.section} workspace",f"{spec.section} / {spec.label}");st.warning("This workspace is registered in the enterprise menu but its execution renderer is not connected yet.")
def render_selected_module(route:str)->None:
    spec=spec_for_route(route)
    if not spec:return render_overview()
    if route=="Overview":return render_overview()
    if route=="System Health":return render_system_health()
    if not spec.implemented or not spec.module_path:return render_placeholder(spec)
    render_header(spec.label,f"IMAGINE {spec.section.title()} Workspace",f"{spec.section} / {spec.label}");render_workspace_controls();started=time.perf_counter()
    try:load_renderer(spec)();st.session_state.last_route_load_ms=round((time.perf_counter()-started)*1000,1)
    except Exception as exc:
        st.error(f"{spec.label} could not be loaded safely. The module menu remains available.")
        with st.expander("Technical details",expanded=False):st.code(f"Module: {spec.module_path}\nRenderer: {spec.renderer_name}");st.exception(exc)
def main()->None:
    init_session_state();inject_styles();render_sidebar();render_navigation()
    if st.session_state.module_search.strip():render_header("Workspace Search","Find an engineering, project, delivery or file workspace","Search / Workspace");render_search_results()
    else:render_selected_module(st.session_state.active_route)
    load_ms=st.session_state.get("last_route_load_ms");timing=f" · last workspace load {load_ms} ms" if load_ms else "";st.markdown(f'<div class="imagine-footer">IMAGINE AEC Engine · Dropdown module navigation + workspace search{timing}</div>',unsafe_allow_html=True)
if __name__=="__main__":main()
