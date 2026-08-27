"""
IMAGINE Platform — OpenBIM IFC Exporter Engine
Path: modules/bim/ifc_export.py
App: imagine
"""

import datetime
import pandas as pd
import streamlit as st
from modules.utils.crud import CRUDService

STATE_KEY = "ifc_exports"


def render() -> None:
    """Renders the OpenBIM IFC data translation and file export engine."""
    st.title("📦 OpenBIM & IFC Data Exporter")
    st.caption("Translate native building spatial hierarchy into ISO 10303-21 IFC (Industry Foundation Classes) schemas.")

    exports = CRUDService.get_all(STATE_KEY)

    tab_export, tab_history, tab_settings = st.tabs([
        "📤 Export Engine",
        "📜 Export Audit Log",
        "⚙️ Schema Configuration"
    ])

    # ==============================================================================
    # TAB 1: EXPORT ENGINE
    # ==============================================================================
    with tab_export:
        col_cfg, col_preview = st.columns([1, 1])

        with col_cfg:
            st.subheader("IFC Translation Settings")

            ifc_version = st.selectbox("IFC Schema Version", ["IFC4.3 (Latest Standard)", "IFC4 (ISO 16739-1)", "IFC2x3 (Legacy Coordination)"])
            discipline = st.multiselect(
                "Export Disciplines",
                ["Architectural Spatial (IfcSpace)", "Structural Geometry (IfcMember)", "MEP Services (IfcDistributionElement)"],
                default=["Architectural Spatial (IfcSpace)", "Structural Geometry (IfcMember)"]
            )
            project_name = st.text_input("BIM Project Name", value="IMAGINE Flagship Development")
            author = st.text_input("Lead Modeler / Author", value="AEC Lead Engineer")
            organization = st.text_input("Organization", value="IMAGINE Infrastructure Solutions")

            st.markdown("---")
            generate_btn = st.button("⚙️ Generate OpenBIM IFC File", type="primary", use_container_width=True)

        with col_preview:
            st.subheader("IFC Data Stream Preview")

            # Collect session state spatial entities
            buildings = CRUDService.get_all("bim_buildings")
            storeys = CRUDService.get_all("bim_storeys")
            spaces = CRUDService.get_all("bim_spaces")

            if generate_btn or "last_ifc_content" not in st.session_state:
                ifc_str = _generate_ifc_content(
                    project_name=project_name,
                    schema_ver=ifc_version.split()[0],
                    author=author,
                    org=organization,
                    buildings=buildings,
                    storeys=storeys,
                    spaces=spaces,
                )
                st.session_state["last_ifc_content"] = ifc_str

                # Record export event
                record = {
                    "id": f"EXP-{len(exports) + 1:03d}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "project": project_name,
                    "schema": ifc_version.split()[0],
                    "entities_count": len(buildings) + len(storeys) + len(spaces),
                    "file_size_kb": round(len(ifc_str) / 1024, 2),
                }
                CRUDService.create(STATE_KEY, record)
            else:
                ifc_str = st.session_state["last_ifc_content"]

            st.text_area("ISO 10303-21 STEP File Output", value=ifc_str, height=280)

            st.download_button(
                label="📥 Download .IFC File",
                data=ifc_str,
                file_name=f"{project_name.lower().replace(' ', '_')}.ifc",
                mime="text/plain",
                use_container_width=True,
            )

    # ==============================================================================
    # TAB 2: EXPORT AUDIT LOG
    # ==============================================================================
    with tab_history:
        st.subheader("Recent OpenBIM Exports")
        if exports:
            st.dataframe(
                pd.DataFrame(exports).sort_values(by="timestamp", ascending=False),
                column_config={
                    "id": "Export ID",
                    "timestamp": "Timestamp",
                    "project": "Project Name",
                    "schema": "IFC Schema",
                    "entities_count": "Mapped Entities",
                    "file_size_kb": st.column_config.NumberColumn("Size (KB)", format="%.2f KB"),
                },
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No export history logged.")

    # ==============================================================================
    # TAB 3: SCHEMA CONFIGURATION
    # ==============================================================================
    with tab_settings:
        st.subheader("OpenBIM Model View Definition (MVD)")
        st.checkbox("Reference View 1.2 (Coordination)", value=True)
        st.checkbox("Design Transfer View", value=False)
        st.checkbox("Include Quantities (BaseQuantities Property Sets)", value=True)
        st.checkbox("Export GUIDs as Persistent Identifiers", value=True)
        st.info("MVD configurations ensure structural, spatial, and mechanical property compliance for BIM tools (Revit, ArchiCAD, Tekla).")


def _generate_ifc_content(
    project_name: str,
    schema_ver: str,
    author: str,
    org: str,
    buildings: list,
    storeys: list,
    spaces: list,
) -> str:
    """Generates standard ISO-10303-21 IFC file text format."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    header = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [ReferenceView_V1.2]'),'2;1');
FILE_NAME('{project_name}.ifc','{now_str}',('{author}'),('{org}'),'IMAGINE AEC Engine','IMAGINE OpenBIM Generator','');
FILE_SCHEMA(('{schema_ver}'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'{author}',$,$,$,$,$);
#2=IFCORGANIZATION($,'{org}',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'1.0','IMAGINE AEC Platform','IMAGINE_BIM');
#5=IFCPROJECT('3a$B1m$89001',#3,'{project_name}',$,$,$,$,$,#6);
#6=IFCUNITASSIGNMENT((#7,#8));
#7=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#8=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
"""

    entity_idx = 10
    lines = []

    # Map Buildings
    for b in buildings:
        lines.append(f"#{entity_idx}=IFCBUILDING('{b.get('id', 'BLDG')}',#3,'{b.get('name', 'Building')}',$,$,$,$,$,.ELEMENT.,$,$,$);")
        entity_idx += 1

    # Map Storeys
    for s in storeys:
        lines.append(f"#{entity_idx}=IFCBUILDINGSTOREY('{s.get('id', 'STRY')}',#3,'{s.get('name', 'Storey')}',$,$,$,$,$,.ELEMENT.,{s.get('elevation_m', 0.0)});")
        entity_idx += 1

    # Map Spaces
    for sp in spaces:
        lines.append(f"#{entity_idx}=IFCSPACE('{sp.get('id', 'SPC')}',#3,'{sp.get('name', 'Space')}',$,$,$,$,$,.ELEMENT.,.INTERNAL.,{sp.get('net_area_m2', 0.0)});")
        entity_idx += 1

    footer = """ENDSEC;
END-ISO-10303-21;"""

    return header + "\n".join(lines) + "\n" + footer
