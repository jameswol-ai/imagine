"""
IMAGINE Projects Module Service
Path: Modules/projects/projects.py
App: imagine
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
import pandas as pd


class ProjectService:
    """Service class handling project calculations, creation, lookups, and analytics."""

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
        total_budget = sum(
            float(p.get("budget", p.get("budget_eur", 0.0))) for p in projects
        )
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
            "budget_eur": float(budget) * 1_000_000,
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

    @staticmethod
    def get_project_calculations(
        project_id: str,
        calcs_list: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Filters global structural calculation history by project ID."""
        return [
            calc for calc in calcs_list
            if str(calc.get("project_id")) == str(project_id)
        ]

    @staticmethod
    def get_project_milestones(project_id: str) -> pd.DataFrame:
        """Generates schedule milestone data for timeline visualization."""
        milestones = [
            {
                "Task": "Feasibility & Site Concept",
                "Start": "2026-01-15",
                "Finish": "2026-03-01",
                "Phase": "Architecture",
                "Completion": 100,
            },
            {
                "Task": "Eurocode Structural Analysis",
                "Start": "2026-02-15",
                "Finish": "2026-05-30",
                "Phase": "Engineering",
                "Completion": 75,
            },
            {
                "Task": "BIM Model & IFC Coordination",
                "Start": "2026-04-01",
                "Finish": "2026-07-15",
                "Phase": "BIM",
                "Completion": 50,
            },
            {
                "Task": "BOQ & Procurement Risk Review",
                "Start": "2026-06-01",
                "Finish": "2026-08-30",
                "Phase": "Costing",
                "Completion": 30,
            },
            {
                "Task": "Site Construction & Verification",
                "Start": "2026-08-15",
                "Finish": "2027-06-30",
                "Phase": "Construction",
                "Completion": 10,
            },
        ]
        df = pd.DataFrame(milestones)
        df["Start"] = pd.to_datetime(df["Start"])
        df["Finish"] = pd.to_datetime(df["Finish"])
        return df
