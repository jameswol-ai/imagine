"""
IMAGINE Platform — Project Management Data Service
Path: modules/projects/projects.py
App: imagine
"""

from typing import Any, Dict, List, Optional
from modules.utils.crud import CRUDService

STATE_KEY = "projects"


class ProjectService:
    """Service layer for managing AEC projects in session state."""

    @staticmethod
    def get_all_projects() -> List[Dict[str, Any]]:
        """Fetch all registered projects."""
        return CRUDService.get_all(STATE_KEY)

    @staticmethod
    def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific project by unique ID."""
        return CRUDService.get_by_id(STATE_KEY, project_id, id_field="id")

    @staticmethod
    def create_project(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project record."""
        return CRUDService.create(STATE_KEY, data)

    @staticmethod
    def update_project(project_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Update an existing project record."""
        return CRUDService.update(STATE_KEY, project_id, updated_fields, id_field="id")

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete a project record."""
        return CRUDService.delete(STATE_KEY, project_id, id_field="id")
