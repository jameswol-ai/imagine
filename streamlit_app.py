"""
IMAGINE v24 Enterprise
Application Entry Point
"""

import streamlit as st

# Import page modules
from modules.dashboard.dashboard import DashboardPage
from modules.projects.project_page import ProjectPage

# Architecture
from modules.architecture.synthesis import render as ArchitecturePage

# BIM
from modules.bim.buildings import render as BuildingsPage
from modules.bim.storeys import render as StoreysPage
from modules.bim.spaces import render as SpacesPage
from modules.bim.ifc_export import render as IFCExportPage

# Structural
from modules.structural.eurocode import render as EurocodePage
from modules.structural.beam_design import render as BeamPage
from modules.structural.column_design import render as ColumnPage
from modules.structural.slab_design import render as SlabPage
from modules.structural.foundation_design import render as FoundationPage
from modules.structural.retaining_walls import render as RetainingWallsPage

# MEP
from modules.mep.analysis import render as MEPAnalysisPage
from modules.mep.hvac import render as HVACPage
from modules.mep.electrical import render as ElectricalPage
from modules.mep.plumbing import render as PlumbingPage
from modules.mep.energy_simulation import render as EnergySimPage

# Costing
from modules.costing.boq import render as BoQPage
from modules.costing.procurement import render as ProcurementPage
from modules.costing.forex import render as ForexPage
from modules.costing.escalation import render as EscalationPage
from modules.costing.risk_analysis import render as RiskPage

# Governance
from modules.governance.approvals import render as ApprovalsPage

# Construction
from modules.construction.rfis import render as RFIsPage
from modules.construction.submittals import render as SubmittalsPage
from modules.construction.site_diary import render as SiteDiaryPage
from modules.construction.progress_tracking import render as ProgressPage
from modules.construction.snagging import render as SnaggingPage

# Documents
from modules.documents.documents import render as DocumentsPage
from modules.documents.revisions import render as RevisionsPage
from modules.documents.drawing_register import render as DrawingRegisterPage
from modules.documents.specifications import render as SpecificationsPage
from modules.documents.transmittals import render as TransmittalsPage

# Analytics
from modules.analytics.portfolio import render as PortfolioPage
from modules.analytics.reporting import render as ReportingPage
from modules.analytics.forecasting import render as ForecastingPage
from modules.analytics.kpis import render as KPIsPage

# Digital Twin
from modules.digital_twin.assets import render as AssetsPage
from modules.digital_twin.sensors import render as SensorsPage
from modules.digital_twin.telemetry import render as TelemetryPage
from modules.digital_twin.maintenance import render as MaintenancePage
from modules.digital_twin.predictive_ai import render as PredictiveAIPage

# AI Assistant
from modules.ai.architect import render as ArchitectAIPage
from modules.ai.engineer import render as EngineerAIPage
from modules.ai.mep import render as MEPAIPage
from modules.ai.qs import render as QSAIPage
from modules.ai.project_manager import render as PMAIPage

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Authentication
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
    st.session_state.user = "Demo User"
    st.session_state.role = "Admin"

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🏗️ IMAGINE")
st.sidebar.write(f"User: {st.session_state.user}")
st.sidebar.write(f"Role: {st.session_state.role}")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Projects",
        "Architecture",
        "BIM",
        "Structural",
        "MEP",
        "Costing",
        "Governance",
        "Construction",
        "Documents",
        "Analytics",
        "Digital Twin",
        "AI Assistant"
    ]
)

# --------------------------------------------------
# Routing
# --------------------------------------------------

if page == "Dashboard":
    DashboardPage.render(st.session_state.projects_data)

elif page == "Projects":
    ProjectPage.render()

elif page == "Architecture":
    ArchitecturePage()

elif page == "BIM":
    st.title("🏛️ BIM")
    tab = st.tabs(["Buildings", "Storeys", "Spaces", "IFC Export"])
    with tab[0]: BuildingsPage()
    with tab[1]: StoreysPage()
    with tab[2]: SpacesPage()
    with tab[3]: IFCExportPage()

elif page == "Structural":
    st.title("🔩 Structural")
    tab = st.tabs(["Eurocode", "Beam", "Column", "Slab", "Foundation", "Retaining Walls"])
    with tab[0]: EurocodePage()
    with tab[1]: BeamPage()
    with tab[2]: ColumnPage()
    with tab[3]: SlabPage()
    with tab[4]: FoundationPage()
    with tab[5]: RetainingWallsPage()

elif page == "MEP":
    st.title("⚡ MEP")
    tab = st.tabs(["Analysis", "HVAC", "Electrical", "Plumbing", "Energy Simulation"])
    with tab[0]: MEPAnalysisPage()
    with tab[1]: HVACPage()
    with tab[2]: ElectricalPage()
    with tab[3]: PlumbingPage()
    with tab[4]: EnergySimPage()

elif page == "Costing":
    st.title("💰 Costing")
    tab = st.tabs(["BoQ", "Procurement", "Forex", "Escalation", "Risk Analysis"])
    with tab[0]: BoQPage()
    with tab[1]: ProcurementPage()
    with tab[2]: ForexPage()
    with tab[3]: EscalationPage()
    with tab[4]: RiskPage()

elif page == "Governance":
    ApprovalsPage()

elif page == "Construction":
    st.title("🚧 Construction")
    tab = st.tabs(["RFIs", "Submittals", "Site Diary", "Progress Tracking", "Snagging"])
    with tab[0]: RFIsPage()
    with tab[1]: SubmittalsPage()
    with tab[2]: SiteDiaryPage()
    with tab[3]: ProgressPage()
    with tab[4]: SnaggingPage()

elif page == "Documents":
    st.title("📄 Documents")
    tab = st.tabs(["Documents", "Revisions", "Drawing Register", "Specifications", "Transmittals"])
    with tab[0]: DocumentsPage()
    with tab[1]: RevisionsPage()
    with tab[2]: DrawingRegisterPage()
    with tab[3]: SpecificationsPage()
    with tab[4]: TransmittalsPage()

elif page == "Analytics":
    st.title("📈 Analytics")
    tab = st.tabs(["Portfolio", "Reporting", "Forecasting", "KPIs"])
    with tab[0]: PortfolioPage()
    with tab[1]: ReportingPage()
    with tab[2]: ForecastingPage()
    with tab[3]: KPIsPage()

elif page == "Digital Twin":
    st.title("🔄 Digital Twin")
    tab = st.tabs(["Assets", "Sensors", "Telemetry", "Maintenance", "Predictive AI"])
    with tab[0]: AssetsPage()
    with tab[1]: SensorsPage()
    with tab[2]: TelemetryPage()
    with tab[3]: MaintenancePage()
    with tab[4]: PredictiveAIPage()

elif page == "AI Assistant":
    st.title("🤖 AI Assistant")
    tab = st.tabs(["Architect", "Engineer", "MEP", "QS", "Project Manager"])
    with tab[0]: ArchitectAIPage()
    with tab[1]: EngineerAIPage()
    with tab[2]: MEPAIPage()
    with tab[3]: QSAIPage()
    with tab[4]: PMAIPage()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.caption("IMAGINE Enterprise v24.1")