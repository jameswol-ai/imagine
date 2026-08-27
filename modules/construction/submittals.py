"""
IMAGINE Construction Module

Submittals Management

Version 24.1
"""

import uuid
from datetime import datetime


class SubmittalService:

    @staticmethod
    def create_submittal(
        title,
        discipline
    ):

        return {
            "id": str(uuid.uuid4()),
            "submittal_no": f"SUB-{str(uuid.uuid4())[:8].upper()}",
            "title": title,
            "discipline": discipline,
            "status": "Submitted",
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def approve(submittal):

        submittal["status"] = "Approved"

        return submittal

    @staticmethod
    def reject(
        submittal,
        comments
    ):

        submittal["status"] = "Rejected"
        submittal["comments"] = comments

        return submittal
