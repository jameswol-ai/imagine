"""IMAGINE AEC Engine Streamlit application shell."""
from __future__ import annotations
import importlib, sys
from pathlib import Path
from typing import Callable
import pandas as pd
import plotly.express as px
import streamlit as st
from modules.enterprise_registry import MODULE_SPECS, ModuleSpec, validate_registry

ROOT_DIR=Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path: sys.path.insert(0,str(ROOT_DIR))
st.set_page_config(page_title="IMAGINE | AEC Engine",page_icon=None,layout="wide",initial_sidebar_state="expanded")

SEARCH_ALIASES={"projects":("projects","approvals","revisions","workflows","governance"),"bim":("bim dashboard","buildings","storeys","spaces","elements","assemblies & types","ifc","cobie","bim coordination","bim quantities","bim → costing / boq","bim → digital twin"),"ifc":("ifc","bim coordination","bim dashboard"),"cobie":("cobie","bim → digital twin"),"boq":("bim quantities","bim → costing / boq","boq","quantity takeoff"),"digital twin":("bim → digital twin","assets","sensors","telemetry"),"structural":("structural engineering dashboard","eurocode suite","beam design","column design","slab design"),"architecture":("architecture assistant","site planning","zoning","floor planning","room programming","compliance"),"mep":("integrated mep analysis","hvac","ventilation","electrical load analysis","water supply","drainage"),"cost":("boq","quantity takeoff","procurement","forex","risk analysis"),"construction":("planning","scheduling","rfis","submittals","snagging","site diaries"),"documents":("drawing management","drawings","document register","specifications","contracts","transmittals")}

def init_session_state():
 for k,v in {"active_route":"Overview","module_search":"","active_domain":"PLATFORM","recent_routes":[],"selected_project_id":None,"selected_project_name":None,"sidebar_nav_domain":"HOME","sidebar_nav_workspace":"Overview"}.items(): st.session_state.setdefault(k,v)

def inject_styles():
 st.markdown("""<style>.stApp{background:linear-gradient(135deg,#f7f9fc,#eef3f8 52%,#fbfcfe)}.block-container{max-width:1720px;padding-top:1rem}.imagine-brand-title{font-size:2rem;font-weight:950;letter-spacing:-.075em}.imagine-brand-subtitle{color:#718096;font-size:.7rem;margin-bottom:1rem}.imagine-header,.imagine-hero,.imagine-panel,.imagine-card{border:1px solid rgba(110,125,145,.16);border-radius:22px;background:rgba(255,255,255,.88);box-shadow:0 16px 42px rgba(30,50,75,.055)}.imagine-header{padding:1.2rem 1.35rem;margin-bottom:1rem}.imagine-header-title{font-size:2.25rem;font-weight:930;letter-spacing:-.06em}.imagine-header-subtitle{color:#687588;margin-top:.3rem}.imagine-hero{padding:1.5rem;margin-bottom:1rem}.imagine-hero-title{font-size:1.7rem;font-weight:900}.imagine-hero-copy{color:#647184;line-height:1.6}.imagine-panel{padding:1rem;margin-bottom:.75rem}.imagine-card{min-height:100px;padding:1rem}.imagine-card-title{color:#687588;font-size:.6rem;font-weight:850;text-transform:uppercase;letter-spacing:.1em}.imagine-card-value{font-size:1.7rem;font-weight:930;margin-top:.35rem}.sidebar-heading{font-size:.59rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#718096;margin:.7rem 0 .35rem}.sidebar-result{padding:.55rem .65rem;border:1px solid rgba(110,125,145,.14);border-radius:11px;margin:.35rem 0}.sidebar-result-title{font-size:.76rem;font-weight:750}.sidebar-result-meta{font-size:.62rem;color:#7a8697}@media(prefers-color-scheme:dark){.stApp{background:#0a1017}.imagine-header,.imagine-hero,.imagine-panel,.imagine-card{background:#121b26;border-color:#293746}.imagine-header-title,.imagine-hero-title,.imagine-card-value,.sidebar-result-title{color:#f1f5f9}.imagine-header-subtitle,.imagine-hero-copy,.imagine-card-title,.sidebar-result-meta{color:#aab5c3}.sidebar-result{background:#111b25}}</style>""",unsafe_allow_html=True)

def specs(domain=None): return [s for s in MODULE_SPECS if domain is None or s.section==domain]
def spec_for(route): return next((s for s in MODULE_SPECS if s.route==route),None)
def set_active(route):
 s=spec_for(route)
 if not s:return
 st.session_state.active_route=route; st.session_state.active_domain=s.section
 st.session_state.recent_routes=[route]+[r for r in st.session_state.recent_routes if r!=route][:7]

def search_specs(query):
 q=" ".join(query.lower().split()); terms=q.split(); expanded=set(terms)
 for t in terms: expanded.update(SEARCH_ALIASES.get(t,()))
 found=[]
 for s in MODULE_SPECS:
  hay=f"{s.route} {s.label} {s.section} {s.module_path or ''}".lower(); score=sum(t in hay for t in terms)+.2*sum(t in hay for t in expanded)
  if q in hay: score+=8
  if score: found.append((score,s))
 return [s for _,s in sorted(found,key=lambda x:(-x[0],x[1].section,x[1].label))]

def load_renderer(s:ModuleSpec)->Callable:
 if not s.module_path or s.module_path=="__builtin__": raise AttributeError("Built-in route")
 m=importlib.import_module(s.module_path); fn=getattr(m,s.renderer_name,None) or getattr(m,"render",None)
 if not callable(fn): raise AttributeError(f"No callable renderer: {s.module_path}")
 return fn

def render_sidebar():
 with st.sidebar:
  st.markdown('<div class="imagine-brand-title">IMAGINE</div><div class="imagine-brand-subtitle">Integrated Architecture, Engineering & Construction Engine</div>',unsafe_allow_html=True)
  domains=sorted({s.section for s in MODULE_SPECS if s.section!="PLATFORM"}); nav=["HOME"]+domains
  current=st.session_state.active_domain if st.session_state.active_domain in nav else "HOME"
  chosen=st.selectbox("Discipline",nav,index=nav.index(current),key="discipline_select")
  if chosen!=current: set_active("Overview"); st.session_state.active_domain=chosen; st.rerun()
  if chosen=="HOME": pages=[s for s in MODULE_SPECS if s.section=="PLATFORM"]; labels=[s.label for s in pages]
  else: pages=specs(chosen); labels=["Discipline Overview"]+[s.label for s in pages]
  active=st.session_state.active_route
  active_label=spec_for(active).label if spec_for(active) else "Overview"
  if chosen!="HOME" and active_label not in labels: active_label="Discipline Overview"
  if chosen=="HOME" and active_label not in labels: active_label=labels[0]
  selected=st.selectbox("Workspace",labels,index=labels.index(active_label),key="workspace_select")
  if chosen!="HOME" and selected=="Discipline Overview": set_active("Overview")
  elif selected: set_active(selected)
  st.markdown('<div class="sidebar-heading">Search all workspaces</div>',unsafe_allow_html=True)
  q=st.text_input("Search",key="module_search",placeholder="Search projects, BIM, IFC, EN 1992...",label_visibility="collapsed")
  if q:
   matches=search_specs(q); st.markdown(f'<div class="sidebar-heading">Search results · {len(matches)}</div>',unsafe_allow_html=True)
   for i,s in enumerate(matches[:12]):
    st.markdown(f'<div class="sidebar-result"><div class="sidebar-result-title">{s.label}</div><div class="sidebar-result-meta">{s.section}</div></div>',unsafe_allow_html=True)
    if st.button("Open",key=f"search_open_{i}_{s.route}",use_container_width=True): set_active(s.route); st.rerun()
  if st.session_state.recent_routes:
   st.markdown('<div class="sidebar-heading">Recent</div>',unsafe_allow_html=True)
   recent=st.selectbox("Recent",st.session_state.recent_routes,key="recent_select",label_visibility="collapsed")
   if recent!=st.session_state.active_route: set_active(recent); st.rerun()

def render_header():
 s=spec_for(st.session_state.active_route); label=s.label if s else "Overview"; domain=s.section if s else "PLATFORM"
 st.markdown(f'<div class="imagine-header"><div class="imagine-header-title">{label}</div><div class="imagine-header-subtitle">{domain} workspace · Connected IMAGINE AEC data environment</div></div>',unsafe_allow_html=True)

def render_overview():
 all_specs=list(MODULE_SPECS); counts=pd.Series([s.section for s in all_specs]).value_counts(); projects=len(specs("PROJECTS")); bim=len(specs("BIM")); structural=len(specs("STRUCTURAL"))
 st.markdown('<div class="imagine-hero"><div class="imagine-hero-title">AEC Command Centre</div><div class="imagine-hero-copy">One workspace connecting project governance, architecture, structural engineering, BIM, MEP, costing, construction and digital delivery.</div></div>',unsafe_allow_html=True)
 cols=st.columns(5)
 for c,title,val in zip(cols,["Workspaces","Projects","BIM","Structural","Domains"],[len(all_specs),projects,bim,structural,len(counts)]): c.markdown(f'<div class="imagine-card"><div class="imagine-card-title">{title}</div><div class="imagine-card-value">{val}</div></div>',unsafe_allow_html=True)
 st.subheader("Platform coverage"); df=counts.rename_axis("Domain").reset_index(name="Workspaces"); st.plotly_chart(px.bar(df,x="Domain",y="Workspaces"),use_container_width=True)
 a,b=st.columns(2)
 with a:
  st.markdown('<div class="imagine-panel"><b>Projects → BIM</b><br><small>Project → Building → Storey → Space → Element → Assembly</small></div>',unsafe_allow_html=True)
 with b:
  st.markdown('<div class="imagine-panel"><b>BIM → Delivery</b><br><small>IFC / COBie → Coordination → Quantities → Costing → Digital Twin</small></div>',unsafe_allow_html=True)

def render_system_health():
 rows=[]
 for s in MODULE_SPECS:
  if not s.implemented or s.module_path in (None,"__builtin__"): continue
  try: load_renderer(s); status="Ready"; detail="Callable renderer found"
  except Exception as e: status="Error"; detail=f"{type(e).__name__}: {e}"
  rows.append({"Workspace":s.label,"Domain":s.section,"Status":status,"Detail":detail})
 df=pd.DataFrame(rows); st.title("System Health"); st.dataframe(df,hide_index=True,use_container_width=True)

def render_current():
 route=st.session_state.active_route
 if route=="Overview": render_overview(); return
 if route=="System Health": render_system_health(); return
 s=spec_for(route)
 if not s: render_overview(); return
 try: load_renderer(s)()
 except Exception as e:
  st.error(f"Unable to render {s.label}"); st.exception(e); st.info("The navigation shell remains available. Fix the module renderer without taking down the application.")

def main():
 init_session_state(); inject_styles(); render_sidebar(); render_header(); render_current(); st.markdown('<div class="imagine-footer">IMAGINE AEC Engine · Preliminary engineering/software platform · Validate project outputs against applicable standards and professional requirements.</div>',unsafe_allow_html=True)
if __name__=="__main__": main()
