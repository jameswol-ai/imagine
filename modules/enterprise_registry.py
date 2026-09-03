"""Central metadata registry for the IMAGINE Streamlit navigation.

This registry is metadata-only: it does not import renderers. That keeps
startup lightweight and lets the application load individual modules lazily.
"""

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
    ModuleSpec("Projects", "Projects", "PROJECTS", "projects.projects.ui", "render_projects", True),
    ModuleSpec("Approvals", "Approvals", "PROJECTS", "projects.approvals.ui", "render_approvals", True),
    ModuleSpec("Revisions", "Revisions", "PROJECTS", "projects.revisions.ui", "render_revisions", True),
    ModuleSpec("Workflows", "Workflows", "PROJECTS", "projects.workflows.ui", "render_workflows", False),
    ModuleSpec("Governance", "Governance", "PROJECTS", "projects.governance.ui", "render_governance", False),
    ModuleSpec("Zoning", "Zoning", "ARCHITECTURE", "architecture.zoning.ui", "render_zoning", True),
    ModuleSpec("Site Planning", "Site Planning", "ARCHITECTURE", "architecture.site_planning.ui", "render_site_planning", True),
    ModuleSpec("Floor Planning", "Floor Planning", "ARCHITECTURE", "architecture.floor_planning.ui", "render_floor_planning", True),
    ModuleSpec("Room Programming", "Room Programming", "ARCHITECTURE", "architecture.room_programming.ui", "render_room_programming", True),
    ModuleSpec("Compliance", "Compliance", "ARCHITECTURE", "architecture.compliance.ui", "render_compliance", True),
    ModuleSpec("Generative Design", "Generative Design", "ARCHITECTURE", "architecture.generative_design.ui", "render_generative_design", True),
    ModuleSpec("Structural", "Structural", "STRUCTURAL", "modules.structural.eurocode", "render", True),
    ModuleSpec("Beam Design", "Beam Design", "STRUCTURAL", "modules.structural.beam_design", "render", True),
    ModuleSpec("Column Design", "Column Design", "STRUCTURAL", "modules.structural.column_design", "render", True),
    ModuleSpec("Slab Design", "Slab Design", "STRUCTURAL", "modules.structural.slab_design", "render", True),
    ModuleSpec("Foundation Design", "Foundation Design", "STRUCTURAL", "modules.structural.foundation_design", "render", True),
    ModuleSpec("Retaining Walls", "Retaining Walls", "STRUCTURAL", "modules.structural.retaining_walls", "render", True),
    ModuleSpec("Steel Connections", "Steel Connections", "STRUCTURAL", "modules.structural.steel_connections", "render", True),
    ModuleSpec("Buildings", "Buildings", "BIM", "modules.bim.buildings", "render", True),
    ModuleSpec("Storeys", "Storeys", "BIM", "modules.bim.storeys", "render", True),
    ModuleSpec("Spaces", "Spaces", "BIM", "modules.bim.spaces", "render", True),
    ModuleSpec("IFC", "IFC", "BIM", "modules.bim.ifc_export", "render", True),
    ModuleSpec("HVAC", "HVAC", "MEP", "modules.mep.hvac", "render", True),
    ModuleSpec("Energy Simulation", "Energy Simulation", "MEP", "modules.mep.energy_simulation", "render", True),
    ModuleSpec("Electrical Load Analysis", "Electrical Load Analysis", "MEP", "modules.mep.electrical", "render", True),
    ModuleSpec("Water Supply", "Water Supply", "MEP", "modules.mep.plumbing", "render", True),
    ModuleSpec("Drainage", "Drainage", "MEP", "modules.mep.plumbing", "render", True),
    ModuleSpec("BOQ", "BOQ", "COSTING", "modules.costing.boq", "render", True),
    ModuleSpec("Procurement", "Procurement", "COSTING", "modules.costing.procurement", "render", True),
    ModuleSpec("Forex", "Forex", "COSTING", "modules.costing.forex", "render", True),
    ModuleSpec("Escalation", "Escalation", "COSTING", "modules.costing.escalation", "render", True),
    ModuleSpec("Risk Analysis", "Risk Analysis", "COSTING", "modules.costing.risk_analysis", "render", True),
    ModuleSpec("RFIs", "RFIs", "CONSTRUCTION", "modules.construction.rfis", "render", True),
    ModuleSpec("Submittals", "Submittals", "CONSTRUCTION", "modules.construction.submittals", "render", True),
    ModuleSpec("Snagging", "Snagging", "CONSTRUCTION", "modules.construction.snagging", "render", True),
    ModuleSpec("Progress Tracking", "Progress Tracking", "CONSTRUCTION", "modules.construction.progress_tracking", "render", True),
    ModuleSpec("Site Diaries", "Site Diaries", "CONSTRUCTION", "modules.construction.site_diary", "render", True),
    ModuleSpec("Drawings", "Drawings", "DOCUMENTS", "modules.documents.drawing_register", "render", True),
    ModuleSpec("Specifications", "Specifications", "DOCUMENTS", "modules.documents.specifications", "render", True),
    ModuleSpec("Transmittals", "Transmittals", "DOCUMENTS", "modules.documents.transmittals", "render", True),
    ModuleSpec("Revisions Control", "Revisions Control", "DOCUMENTS", "modules.documents.revisions", "render", True),
    ModuleSpec("Dashboards", "Dashboards", "ANALYTICS", "modules.analytics.portfolio", "render", True),
    ModuleSpec("KPIs", "KPIs", "ANALYTICS", "modules.analytics.kpis", "render", True),
    ModuleSpec("Portfolio", "Portfolio", "ANALYTICS", "modules.analytics.portfolio", "render", True),
    ModuleSpec("Forecasting", "Forecasting", "ANALYTICS", "modules.analytics.forecasting", "render", True),
    ModuleSpec("Reporting", "Reporting", "ANALYTICS", "modules.analytics.reporting", "render", True),
    ModuleSpec("Digital Twin Assets", "Assets", "DIGITAL TWIN", "modules.digital_twin.assets", "render", True),
    ModuleSpec("Digital Twin Sensors", "Sensors", "DIGITAL TWIN", "modules.digital_twin.sensors", "render", True),
    ModuleSpec("Telemetry", "Telemetry", "DIGITAL TWIN", "modules.digital_twin.telemetry", "render", True),
    ModuleSpec("Maintenance", "Maintenance", "DIGITAL TWIN", "modules.digital_twin.maintenance", "render", True),
    ModuleSpec("Predictive AI", "Predictive AI", "DIGITAL TWIN", "modules.digital_twin.predictive_ai", "render", True),
)


MODULES_BY_ROUTE = {spec.route: spec for spec in MODULE_SPECS}


def validate_registry() -> None:
    """Fail fast on duplicate or malformed route metadata."""
    routes = [spec.route for spec in MODULE_SPECS]
    duplicates = sorted({route for route in routes if routes.count(route) > 1})
    if duplicates:
        raise RuntimeError(f"Duplicate module routes detected: {duplicates}")

    for spec in MODULE_SPECS:
        if not spec.route.strip() or not spec.label.strip() or not spec.section.strip():
            raise RuntimeError(f"Invalid module specification: {spec!r}")
        if spec.implemented and not spec.module_path:
            raise RuntimeError(f"Implemented module has no module path: {spec.route}")


validate_registry()

__all__ = ["ModuleSpec", "MODULE_SPECS", "MODULES_BY_ROUTE", "validate_registry"]
