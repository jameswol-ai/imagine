"""
IMAGINE Projects Module

Project Management Engine

Version 24.1
"""

from datetime import datetime
import uuid


class ProjectService:

    @staticmethod
    def generate_project_code():

        today = datetime.now()

        return (
            f"PRJ-"
            f"{today.year}-"
            f"{str(uuid.uuid4())[:8].upper()}"
        )

    @staticmethod
    def create_project(
        name,
        status="planning",
        budget=0.0,
        progress=0.0,
        client="",
        category="General"
    ):

        return {
            "id": str(uuid.uuid4()),
            "project_code":
                ProjectService.generate_project_code(),
            "name": name,
            "status": status,
            "budget": budget,
            "progress": progress,
            "client": client,
            "category": category,
            "created_at":
                datetime.utcnow().isoformat()
        }

    @staticmethod
    def update_project(
        project,
        updates
    ):

        for key, value in updates.items():
            project[key] = value

        project["updated_at"] = (
            datetime.utcnow().isoformat()
        )

        return project

    @staticmethod
    def delete_project(
        project_id,
        projects
    ):

        return [
            p
            for p in projects
            if str(p["id"]) != str(project_id)
        ]

    @staticmethod
    def find_project(
        project_id,
        projects
    ):

        for project in projects:

            if str(project["id"]) == str(project_id):
                return project

        return None

    @staticmethod
    def total_budget(
        projects
    ):

        return round(
            sum(
                p.get("budget", 0)
                for p in projects
            ),
            2
        )

    @staticmethod
    def average_progress(
        projects
    ):

        if not projects:
            return 0

        return round(
            sum(
                p.get("progress", 0)
                for p in projects
            ) / len(projects),
            2
        )

    @staticmethod
    def status_summary(
        projects
    ):

        summary = {}

        for project in projects:

            status = project.get(
                "status",
                "unknown"
            )

            summary[status] = (
                summary.get(
                    status,
                    0
                ) + 1
            )

        return summary

    @staticmethod
    def portfolio_metrics(
        projects
    ):

        return {
            "total_projects":
                len(projects),

            "total_budget":
                ProjectService.total_budget(
                    projects
                ),

            "average_progress":
                ProjectService.average_progress(
                    projects
                ),

            "status_summary":
                ProjectService.status_summary(
                    projects
                )
        }
