"""Shared project context and cross-module data contract for IMAGINE.

The context is intentionally UI-agnostic. It gives every AEC discipline one
small contract for identifying the active project and exchanging module
outputs without making each module know about the others.

This is a coordination layer, not a replacement for the database. The
session-state adapter keeps the Streamlit experience usable when a database
is unavailable; production persistence should be provided by the project
service/database layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


MODULE_ORDER = (
    "Architecture",
    "Structural Engineering",
    "BIM",
    "MEP",
    "Costing",
    "Construction",
    "Documents",
    "Digital Twin",
)


@dataclass
class ModuleStatus:
    """Status and handoff metadata for one discipline."""

    name: str
    status: str = "not_started"
    progress: float = 0.0
    output_count: int = 0
    last_updated: Optional[str] = None
    notes: str = ""


@dataclass
class ProjectContext:
    """Canonical project-level context shared by all IMAGINE modules."""

    project_id: str
    project_name: str
    status: str = "planning"
    description: str = ""
    client: str = ""
    location: str = ""
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)
    module_status: Dict[str, ModuleStatus] = field(default_factory=dict)
    outputs: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for module in MODULE_ORDER:
            self.module_status.setdefault(module, ModuleStatus(name=module))
            self.outputs.setdefault(module, [])

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["module_status"] = {
            name: asdict(value) for name, value in self.module_status.items()
        }
        return payload

    def set_status(self, module: str, status: str, progress: float | None = None, notes: str = "") -> None:
        entry = self.module_status.setdefault(module, ModuleStatus(name=module))
        entry.status = status
        if progress is not None:
            entry.progress = max(0.0, min(100.0, float(progress)))
        if notes:
            entry.notes = notes
        entry.last_updated = datetime.now(timezone.utc).isoformat()

    def add_output(self, module: str, output_type: str, data: Dict[str, Any], output_id: str | None = None) -> str:
        output_id = output_id or str(uuid4())
        record = {
            "id": output_id,
            "project_id": self.project_id,
            "module": module,
            "output_type": output_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self.outputs.setdefault(module, []).append(record)
        entry = self.module_status.setdefault(module, ModuleStatus(name=module))
        entry.output_count = len(self.outputs[module])
        entry.last_updated = record["created_at"]
        if entry.status == "not_started":
            entry.status = "in_progress"
        return output_id

    def outputs_for(self, module: str, output_type: str | None = None) -> List[Dict[str, Any]]:
        records = list(self.outputs.get(module, []))
        if output_type is None:
            return records
        return [record for record in records if record.get("output_type") == output_type]

    def handoff(self, source_module: str, target_module: str, output_type: str | None = None) -> Dict[str, Any]:
        """Create a lightweight, traceable handoff package between modules."""
        records = self.outputs_for(source_module, output_type)
        return {
            "id": str(uuid4()),
            "project_id": self.project_id,
            "source_module": source_module,
            "target_module": target_module,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "outputs": records,
        }


def context_from_project(project: Dict[str, Any]) -> ProjectContext:
    """Normalize a project-service record into the shared contract."""
    project_id = str(project.get("id") or project.get("project_id") or uuid4())
    name = str(project.get("name") or project.get("project_name") or "Untitled Project")
    return ProjectContext(
        project_id=project_id,
        project_name=name,
        status=str(project.get("status", "planning")),
        description=str(project.get("description") or ""),
        client=str(project.get("client") or project.get("client_name") or ""),
        location=str(project.get("location") or ""),
        currency=str(project.get("currency") or "USD"),
        metadata={key: value for key, value in project.items() if key not in {
            "id", "project_id", "name", "project_name", "status", "description",
            "client", "client_name", "location", "currency"
        }},
    )


def project_from_context(context: ProjectContext) -> Dict[str, Any]:
    """Return a project-service-compatible record from a context."""
    return {
        "id": context.project_id,
        "name": context.project_name,
        "status": context.status,
        "description": context.description,
        "client": context.client,
        "location": context.location,
        "currency": context.currency,
        **context.metadata,
    }


def context_from_projects(projects: Iterable[Dict[str, Any]], project_id: str | None) -> ProjectContext | None:
    """Select one project record without coupling the shell to storage."""
    if not project_id:
        return None
    target = str(project_id)
    for project in projects:
        candidate = str(project.get("id") or project.get("project_id") or "")
        if candidate == target:
            return context_from_project(project)
    return None


__all__ = [
    "MODULE_ORDER",
    "ModuleStatus",
    "ProjectContext",
    "context_from_project",
    "context_from_projects",
    "project_from_context",
]
