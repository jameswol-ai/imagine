"""Central metadata registry for IMAGINE Streamlit navigation."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ModuleSpec:
    route: str
    label: str
    section: str
    module_path: str | None = None
    renderer_name: str = "render"
    implemented: bool = False

MODULE_SPECS: tuple[ModuleSpec, ...] = (
    ModuleSpec("Overview", "Overview", "PLATFORM", "__builtin__", "render_overview", True),
    ModuleSpec("System Health", "System Health", "PLATFORM", "__builtin__", "render_system_health", True),
    ModuleSpec("Project Files", "Project Files", "PLATFORM", "modules.platform.file_center", "render", True),
    ModuleSpec("Projects", "Projects", "PROJECTS", "projects.projects.ui", "render_projects", True),
    ModuleSpec("Approvals", "Approvals", "PROJECTS", "projects.approvals.ui", "render_approvals", True),
    ModuleSpec("Revisions", "Revisions", "PROJECTS", "projects.revisions.ui", "render_revisions", True),
    ModuleSpec("Workflows", "Workflows", "PROJECTS", "projects.workflows.ui", "render_workflows", True),
    ModuleSpec("Governance", "Governance", "PROJECTS", "projects.governance.ui", "render_governance", True),
    ModuleSpec("Architecture Assistant", "Architecture Assistant", "ARCHITECTURE", "architecture.assistant.ui", "render_architecture_assistant", True),
    ModuleSpec("Design Standards", "Design Standards", "ARCHITECTURE", "architecture.standards.ui", "render_design_standards", True),
    ModuleSpec("Zoning", "Zoning", "ARCHITECTURE", "architecture.zoning.ui", "render_zoning", True),
    ModuleSpec("Site Planning", "Site Planning", "ARCHITECTURE", "architecture.site_planning.ui", "render_site_planning", True),
    ModuleSpec("Floor Planning", "Floor Planning", "ARCHITECTURE", "architecture.floor_planning.ui", "render_floor_planning", True),
    ModuleSpec("Room Programming", "Room Programming", "ARCHITECTURE", "architecture.room_programming.ui", "render_room_programming", True),
    ModuleSpec("Compliance", "Compliance", "ARCHITECTURE", "architecture.compliance.ui", "render_compliance", True),
    ModuleSpec("Generative Design", "Generative Design", "ARCHITECTURE", "architecture.generative_design.ui", "render_generative_design", True),
    ModuleSpec("Eurocode Suite", "Eurocode Suite", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("EN 1990", "EN 1990", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("EN 1991", "EN 1991", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("EN 1992", "EN 1992", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("EN 1993", "EN 1993", "STRUCTURAL", "modules.structural.eurocode_1993", "render", True),
    ModuleSpec("EN 1994", "EN 1994", "STRUCTURAL", "modules.structural.eurocode_1994", "render", True),
    ModuleSpec("EN 1995", "EN 1995", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("EN 1996", "EN 1996", "STRUCTURAL", "modules.structural.eurocode_1996", "render", True),
    ModuleSpec("EN 1997", "EN 1997", "STRUCTURAL", "modules.structural.eurocode_1997", "render", True),
    ModuleSpec("EN 1998", "EN 1998", "STRUCTURAL", "modules.structural.eurocode_1998", "render", True),
    ModuleSpec("Beam Design", "Beam Design", "STRUCTURAL", "modules.structural.beam_design", "render", True),
    ModuleSpec("Column Design", "Column Design", "STRUCTURAL", "modules.structural.column_design", "render", True),
    ModuleSpec("Slab Design", "Slab Design", "STRUCTURAL", "modules.structural.slab_design", "render", True),
    ModuleSpec("Foundation Design", "Foundation Design", "STRUCTURAL", "modules.structural.foundation_design", "render", True),
    ModuleSpec("Retaining Walls", "Retaining Walls", "STRUCTURAL", "modules.structural.retaining_walls", "render", True),
    ModuleSpec("Punching Shear", "Punching Shear", "STRUCTURAL", "modules.structural.punching_shear", "render", True),
    ModuleSpec("Steel Members", "Steel Members", "STRUCTURAL", "modules.structural.steel_members", "render", True),
    ModuleSpec("Steel Connections", "Steel Connections", "STRUCTURAL", "modules.structural.steel_connections", "render", True),
    ModuleSpec("Section Shapes", "Section Shapes", "STRUCTURAL", "modules.structural.shape_design", "render", True),
    ModuleSpec("Roof Design", "Roof Design", "STRUCTURAL", "modules.structural.roof_design", "render", True),
    ModuleSpec("Structural Analysis", "Structural Analysis", "STRUCTURAL", "modules.structural.structural_analysis", "render", True),
    ModuleSpec("Finite Element Analysis", "Finite Element Analysis", "STRUCTURAL", None, "render", False),
    ModuleSpec("Buildings", "Buildings", "BIM", "modules.bim.buildings", "render", True),
    ModuleSpec("Storeys", "Storeys", "BIM", "modules.bim.storeys", "render", True),
    ModuleSpec("Spaces", "Spaces", "BIM", "modules.bim.spaces", "render", True),
    ModuleSpec("Elements", "Elements", "BIM", None, "render", False),
    ModuleSpec("IFC", "IFC", "BIM", "modules.bim.ifc_export", "render", True),
    ModuleSpec("COBie", "COBie", "BIM", None, "render", False),
    ModuleSpec("BIM Digital Twin", "BIM Digital Twin", "BIM", None, "render", False),
    ModuleSpec("Integrated MEP Analysis", "Integrated MEP Analysis", "MEP", "modules.mep.analysis", "render", True),
    ModuleSpec("HVAC", "HVAC", "MEP", "modules.mep.hvac", "render", True),
    ModuleSpec("Ventilation", "Ventilation", "MEP", "modules.mep.analysis", "render", True),
    ModuleSpec("Chilled Water", "Chilled Water", "MEP", "modules.mep.analysis", "render", True),
    ModuleSpec("Energy Simulation", "Energy Simulation", "MEP", "modules.mep.energy_simulation", "render", True),
    ModuleSpec("Electrical Load Analysis", "Electrical Load Analysis", "MEP", "modules.mep.electrical", "render", True),
    ModuleSpec("Water Supply", "Water Supply", "MEP", "modules.mep.plumbing", "render", True),
    ModuleSpec("Drainage", "Drainage", "MEP", "modules.mep.plumbing", "render", True),
    ModuleSpec("BOQ", "BOQ", "COSTING", "modules.costing.boq", "render", True),
    ModuleSpec("Quantity Takeoff", "Quantity Takeoff", "COSTING", "modules.costing.boq", "render", True),
    ModuleSpec("Procurement", "Procurement", "COSTING", "modules.costing.procurement", "render", True),
    ModuleSpec("Forex", "Forex", "COSTING", "modules.costing.forex", "render", True),
    ModuleSpec("Inflation / Escalation", "Inflation / Escalation", "COSTING", "modules.costing.escalation", "render", True),
    ModuleSpec("Risk Analysis", "Risk Analysis", "COSTING", "modules.costing.risk_analysis", "render", True),
    ModuleSpec("Planning", "Planning", "CONSTRUCTION", "modules.construction.progress_tracking", "render", True),
    ModuleSpec("Scheduling", "Scheduling", "CONSTRUCTION", "modules.construction.progress_tracking", "render", True),
    ModuleSpec("RFIs", "RFIs", "CONSTRUCTION", "modules.construction.rfis", "render", True),
    ModuleSpec("Submittals", "Submittals", "CONSTRUCTION", "modules.construction.submittals", "render", True),
    ModuleSpec("Snagging", "Snagging", "CONSTRUCTION", "modules.construction.snagging", "render", True),
    ModuleSpec("Site Diaries", "Site Diaries", "CONSTRUCTION", "modules.construction.site_diary", "render", True),
    ModuleSpec("Drawing Management", "Drawing Management", "DOCUMENTS", "modules.documents.drawing_register", "render", True),
    ModuleSpec("Document Register", "Document Register", "DOCUMENTS", "modules.documents.documents", "render", True),
    ModuleSpec("Specifications", "Specifications", "DOCUMENTS", "modules.documents.specifications", "render", True),
    ModuleSpec("Contracts", "Contracts", "DOCUMENTS", "modules.documents.documents", "render", True),
    ModuleSpec("Version Control", "Version Control", "DOCUMENTS", "modules.documents.revisions", "render", True),
    ModuleSpec("Transmittals", "Transmittals", "DOCUMENTS", "modules.documents.transmittals", "render", True),
    ModuleSpec("IMAGINE Architect", "IMAGINE Architect", "AI", "modules.ai.architect", "render", True),
    ModuleSpec("IMAGINE Engineer", "IMAGINE Engineer", "AI", "modules.ai.engineer", "render", True),
    ModuleSpec("IMAGINE MEP", "IMAGINE MEP", "AI", "modules.ai.mep", "render", True),
    ModuleSpec("IMAGINE QS", "IMAGINE QS", "AI", "modules.ai.qs", "render", True),
    ModuleSpec("IMAGINE PM", "IMAGINE PM", "AI", "modules.ai.project_manager", "render", True),
    ModuleSpec("Dashboards", "Dashboards", "ANALYTICS", "modules.dashboard.dashboard", "render", True),
    ModuleSpec("KPIs", "KPIs", "ANALYTICS", "modules.analytics.kpis", "render", True),
    ModuleSpec("Portfolio", "Portfolio", "ANALYTICS", "modules.analytics.portfolio", "render", True),
    ModuleSpec("Forecasting", "Forecasting", "ANALYTICS", "modules.analytics.forecasting", "render", True),
    ModuleSpec("Reporting", "Reporting", "ANALYTICS", "modules.analytics.reporting", "render", True),
    ModuleSpec("Uganda", "Uganda", "REGIONAL", None, "render", False),
    ModuleSpec("Kenya", "Kenya", "REGIONAL", None, "render", False),
    ModuleSpec("Tanzania", "Tanzania", "REGIONAL", None, "render", False),
    ModuleSpec("Rwanda", "Rwanda", "REGIONAL", None, "render", False),
    ModuleSpec("South Sudan", "South Sudan", "REGIONAL", None, "render", False),
    ModuleSpec("Codes", "Codes", "REGIONAL", None, "render", False),
    ModuleSpec("Zoning Laws", "Zoning Laws", "REGIONAL", None, "render", False),
    ModuleSpec("Microsoft", "Microsoft", "INTEGRATIONS", None, "render", False),
    ModuleSpec("AutoCAD", "AutoCAD", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Revit", "Revit", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Archicad", "Archicad", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Tekla", "Tekla", "INTEGRATIONS", None, "render", False),
    ModuleSpec("IfcOpenShell", "IfcOpenShell", "INTEGRATIONS", None, "render", False),
    ModuleSpec("ArcGIS", "ArcGIS", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Azure", "Azure", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Mapbox", "Mapbox", "INTEGRATIONS", None, "render", False),
    ModuleSpec("Assets", "Assets", "DIGITAL TWIN", "modules.digital_twin.assets", "render", True),
    ModuleSpec("Sensors", "Sensors", "DIGITAL TWIN", "modules.digital_twin.sensors", "render", True),
    ModuleSpec("Telemetry", "Telemetry", "DIGITAL TWIN", "modules.digital_twin.telemetry", "render", True),
    ModuleSpec("Energy", "Energy", "DIGITAL TWIN", None, "render", False),
    ModuleSpec("Maintenance", "Maintenance", "DIGITAL TWIN", "modules.digital_twin.maintenance", "render", True),
    ModuleSpec("Predictive AI", "Predictive AI", "DIGITAL TWIN", "modules.digital_twin.predictive_ai", "render", True),
)

MODULES_BY_ROUTE = {spec.route: spec for spec in MODULE_SPECS}

def validate_registry() -> None:
    routes = [s.route for s in MODULE_SPECS]
    duplicates = sorted({r for r in routes if routes.count(r) > 1})
    if duplicates:
        raise RuntimeError(f"Duplicate module routes detected: {duplicates}")
    for spec in MODULE_SPECS:
        if not spec.route.strip() or not spec.label.strip() or not spec.section.strip():
            raise RuntimeError(f"Invalid module specification: {spec!r}")
        if spec.implemented and not spec.module_path:
            raise RuntimeError(f"Implemented module has no module path: {spec.route}")

validate_registry()
__all__ = ["ModuleSpec", "MODULE_SPECS", "MODULES_BY_ROUTE", "validate_registry"]
