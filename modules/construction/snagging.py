"""
IMAGINE Construction Module

Snagging & Defects

Version 24.1
"""

import uuid
from datetime import datetime


class SnaggingService:

    @staticmethod
    def create_snag(
        location,
        description,
        priority="Medium"
    ):

        return {
            "id": str(uuid.uuid4()),
            "snag_no": f"SNG-{str(uuid.uuid4())[:8].upper()}",
            "location": location,
            "description": description,
            "priority": priority,
            "status": "Open",
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def close_snag(
        snag,
        closed_by
    ):

        snag["status"] = "Closed"
        snag["closed_by"] = closed_by

        return snag
