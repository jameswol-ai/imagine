"""
Maintenance Engine
"""

from datetime import datetime


class MaintenanceService:

    @staticmethod
    def create_ticket(
        asset,
        issue
    ):

        return {
            "asset": asset,
            "issue": issue,
            "status": "Open",
            "created_at":
                datetime.utcnow().isoformat()
        }
