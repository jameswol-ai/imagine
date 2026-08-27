"""
IMAGINE Projects Module Service
Path: Modules/projects/projects.py
App: imagine
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional


class ProjectService:
    """Service class handling project calculations, creation, and lookups."""

    @staticmethod
    def portfolio_metrics(projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates aggregated metrics across the project portfolio."""
        if not projects:
            return {
                "total_projects": 0,
                "total_budget": 0.0,
                "average_progress": 0.0,
            }

        total_projects = len(projects)

        # Compute total budget (handling key variances: budget or budget_eur)
        total_budget = sum(
            float(p.get("budget", p.get("budget_eur", 0.0))) for p in projects
        )

        # Compute average progress percentage
        total_progress = sum(float(p.get("progress_pct", 0.0)) for p in projects)
        average_progress = round(total_progress / total_projects, 1)

        return {
            "total_projects": total_projects,
            "total_budget": total_budget,
            "average_progress": average_progress,
        }

    @staticmethod
    def create_project(
        name: str,
        client: str,
        category: str,
        budget: float,
        status: str,
    ) -> Dict[str, Any]:
        """Constructs a new validated project record with default metadata."""
        project_id = f"PRJ-{str(uuid.uuid4())[:6].upper()}"

        return {
            "id": project_id,
            "name": name if name.strip() else f"Project {project_id}",
            "client": client if client.strip() else "Unassigned Client",
            "category": category,
            "budget": float(budget),
            "budget_eur": float(budget) * 1_000_000,  # Standardize for costing suite
            "status": status,
            "progress_pct": 0.0,
            "location": "TBD",
            "typology": category,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def find_project(
        project_id: str,
        projects: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Finds and returns a single project record by unique ID."""
        for project in projects:
            if str(project.get("id")) == str(project_id):
                return project
        return None
