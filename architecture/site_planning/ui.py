from decimal import Decimal
import pandas as pd
import streamlit as st

def render_site_planning(service):
    st.subheader("Site Planning")
    plans = service.list_sync() if hasattr(service, "list_sync") else []
    if plans:
        st.dataframe(pd.DataFrame([{"ID": str(p.id), "Site": p.name, "Code": p.site_code, "Status": p.status, "Area (m²)": float(p.site_area_m2), "Footprint (m²)": float(p.building_footprint_m2), "Landscape (m²)": float(p.landscape_area_m2), "Slope (%)": float(p.slope_percent)} for p in plans]), use_container_width=True, hide_index=True)
    else: st.info("No site plans have been created yet.")
    with st.expander("➕ Add Site Plan"):
        with st.form("site_planning_create_form"):
            c1,c2=st.columns(2)
            with c1:
                name=st.text_input("Site Plan Name"); code=st.text_input("Site Code")
                status=st.selectbox("Status",["Draft","Proposed","Approved","Archived"])
                site_area=st.number_input("Site Area (m²)",min_value=.01,value=5000.0)
                footprint=st.number_input("Building Footprint (m²)",min_value=0.0,value=2000.0)
                road=st.number_input("Road Area (m²)",min_value=0.0,value=800.0)
            with c2:
                parking=st.number_input("Parking Area (m²)",min_value=0.0,value=700.0)
                landscape=st.number_input("Landscape Area (m²)",min_value=0.0,value=1500.0)
                orientation=st.number_input("North Orientation (°)",min_value=0.0,max_value=359.99,value=0.0)
                slope=st.number_input("Slope (%)",min_value=0.0,max_value=100.0,value=5.0)
                soil=st.selectbox("Soil Type",["Clay","Sand","Rock","Silt","Mixed"])
                drainage=st.text_input("Drainage Strategy"); access=st.text_input("Access Strategy")
            if st.form_submit_button("Create Site Plan"):
                if not name or not code: st.error("Name and Site Code are required.")
                else:
                    try:
                        service.create_sync(dict(name=name,site_code=code,status=status,site_area_m2=Decimal(str(site_area)),building_footprint_m2=Decimal(str(footprint)),road_area_m2=Decimal(str(road)),parking_area_m2=Decimal(str(parking)),landscape_area_m2=Decimal(str(landscape)),north_orientation_deg=Decimal(str(orientation)),slope_percent=Decimal(str(slope)),soil_type=soil,drainage_strategy=drainage or None,access_strategy=access or None,active=True))
                        st.success("Site plan created."); st.rerun()
                    except Exception as exc: st.error(str(exc))
