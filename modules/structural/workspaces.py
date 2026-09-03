"""Unified UI adapters for structural workspaces whose calculation engines are still evolving.

Each workspace remains executable and transparent while deeper code-specific solvers
are integrated. Outputs are preliminary screening values, never certification.
"""
from __future__ import annotations
import math
import streamlit as st


def _title() -> str:
    return str(st.session_state.get("active_route", "Structural Workspace"))


def _notice(code: str) -> None:
    st.warning(f"{code}: preliminary engineering workspace. Verify the adopted Eurocode edition, National Annex, project specification, load model, material properties and professional design review before use on a real project.")


def _eurocode(code: str) -> None:
    st.title(code)
    st.caption(f"{code} knowledge, inputs and preliminary calculation workspace")
    topics = {
        "EN 1993": ["Steel material properties", "Cross-section resistance", "Buckling", "Members", "Connections"],
        "EN 1994": ["Composite beams", "Shear connection", "Effective width", "Composite slabs", "Construction stage"],
        "EN 1995": ["Timber grades", "Bending", "Compression", "Buckling", "Connections"],
        "EN 1996": ["Masonry units", "Mortar", "Wall resistance", "Slenderness", "Lateral loading"],
        "EN 1997": ["Ground model", "Bearing", "Sliding", "Settlement", "Retaining structures"],
        "EN 1998": ["Hazard", "Response spectrum", "Seismic forces", "Drift", "Ductility"],
        "EN 1999": ["Aluminium alloys", "Cross-sections", "Member resistance", "Buckling", "Connections"],
    }
    selected = st.multiselect("Design topics", topics.get(code, ["Basis", "Actions", "Resistance", "Serviceability"]), default=topics.get(code, [])[:2])
    st.dataframe({"Topic": selected, "Status": ["Available for preliminary review"] * len(selected)}, use_container_width=True, hide_index=True)
    if code == "EN 1997":
        c1,c2,c3=st.columns(3); c1.number_input("Ground unit weight (kN/m³)", value=18.0); c2.number_input("Cohesion c' (kPa)", value=10.0); c3.number_input("Friction angle phi' (deg)", value=30.0)
    elif code == "EN 1998":
        c1,c2,c3=st.columns(3); c1.number_input("Design ground acceleration ag (g)", value=0.12); c2.number_input("Behaviour factor q", min_value=1.0, value=3.0); c3.number_input("Importance factor", min_value=0.1, value=1.0)
    else:
        st.info("Select the relevant topic to continue into the detailed design workflow.")
    _notice(code)


def _foundation() -> None:
    st.title("Foundation Design")
    st.caption("Preliminary isolated pad footing screening")
    c1,c2=st.columns(2)
    with c1:
        n=st.number_input("Service axial load N (kN)", min_value=0.0, value=600.0)
        qallow=st.number_input("Allowable bearing pressure (kPa)", min_value=1.0, value=150.0)
        width=st.number_input("Footing width B (m)", min_value=0.3, value=2.2)
    with c2:
        length=st.number_input("Footing length L (m)", min_value=0.3, value=2.2)
        self_weight=st.number_input("Estimated footing/soil surcharge (kN)", min_value=0.0, value=80.0)
        m=st.number_input("Service moment M (kNm)", min_value=0.0, value=30.0)
    area=width*length; pressure=(n+self_weight)/area; e=m/max(n+self_weight,1e-9); qmax=pressure*(1+6*e/width); qmin=pressure*(1-6*e/width)
    a,b,c,d=st.columns(4); a.metric("Area",f"{area:.2f} m²"); b.metric("Average q",f"{pressure:.1f} kPa"); c.metric("qmax",f"{qmax:.1f} kPa"); d.metric("Eccentricity",f"{e*1000:.0f} mm")
    if qmax<=qallow and qmin>=0: st.success("Preliminary bearing-pressure screen passes.")
    else: st.warning("Bearing-pressure screen requires revision or detailed geotechnical design.")
    _notice("Foundation Design")


def _punching() -> None:
    st.title("Punching Shear")
    st.caption("Preliminary punching shear screening around an internal column")
    c1,c2=st.columns(2)
    with c1: ved=st.number_input("Column reaction VEd (kN)", min_value=0.0, value=500.0); d=st.number_input("Effective depth d (mm)", min_value=50.0, value=150.0)
    with c2: bx=st.number_input("Column width (mm)", min_value=100.0, value=300.0); by=st.number_input("Column depth (mm)", min_value=100.0, value=300.0)
    u=2*((bx+4*d)+(by+4*d)); area=u*d/1e6; v=ved/(area*1000) if area else math.inf
    a,b=st.columns(2); a.metric("Approx. control perimeter",f"{u:.0f} mm"); b.metric("vEd",f"{v:.3f} MPa")
    st.info("A complete EC2 punching check needs loaded area, control perimeters, reinforcement ratio, concrete strength, openings, moments and National Annex factors.")
    _notice("Punching Shear")


def _steel(kind: str) -> None:
    st.title(kind)
    st.caption("Preliminary EN 1993 steel member screening")
    c1,c2=st.columns(2)
    with c1: area=st.number_input("Gross area A (mm²)", min_value=100.0, value=5000.0); fy=st.number_input("Steel fy (MPa)", min_value=100.0, value=355.0)
    with c2: ned=st.number_input("Design axial force NEd (kN)", min_value=0.0, value=500.0); length=st.number_input("Member length (m)", min_value=0.1, value=5.0)
    resistance=area*fy/1000; utilisation=ned/max(resistance,1e-9)
    a,b=st.columns(2); a.metric("Gross yield resistance",f"{resistance:.0f} kN"); b.metric("Axial utilisation",f"{utilisation:.2f}")
    st.info(f"{kind}: section classification, buckling curves, imperfections, shear, interaction and connection design require the detailed EN 1993 workflow.")
    _notice(kind)


def _connections() -> None:
    st.title("Steel Connections")
    st.caption("Preliminary bolt and weld resistance screening")
    bolts=st.number_input("Number of bolts", min_value=1, value=4); dia=st.number_input("Bolt diameter (mm)", min_value=6.0, value=20.0); fub=st.number_input("Bolt ultimate strength fub (MPa)", min_value=200.0, value=800.0); ned=st.number_input("Design shear force (kN)", min_value=0.0, value=120.0)
    area=math.pi*dia**2/4; resistance=bolts*0.6*fub*area/1000; u=ned/max(resistance,1e-9)
    st.metric("Approx. bolt shear resistance",f"{resistance:.1f} kN"); st.metric("Utilisation",f"{u:.2f}")
    _notice("Steel Connections")


def _generic() -> None:
    title=_title(); st.title(title); st.caption("Interactive preliminary structural engineering workspace")
    c1,c2,c3=st.columns(3); c1.number_input("Design action", min_value=0.0, value=100.0); c2.number_input("Characteristic resistance", min_value=0.1, value=200.0); c3.number_input("Partial factor", min_value=0.1, value=1.5)
    action=st.session_state.get("Design action",100.0); resistance=st.session_state.get("Characteristic resistance",200.0); gamma=st.session_state.get("Partial factor",1.5); design=resistance/gamma; utilisation=action/max(design,1e-9)
    a,b=st.columns(2); a.metric("Design resistance",f"{design:.2f}"); b.metric("Utilisation",f"{utilisation:.2f}")
    _notice(title)


def render() -> None:
    title=_title()
    if title.startswith("EN 199"):
        _eurocode(title)
    elif title=="Foundation Design": _foundation()
    elif title=="Punching Shear": _punching()
    elif title in {"Steel Members","Section Shapes"}: _steel(title)
    elif title=="Steel Connections": _connections()
    else: _generic()

__all__=["render"]
