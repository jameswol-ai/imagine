"""
IMAGINE Construction Module

RFI Management

Version 24.1
"""

import uuid
from datetime import datetime


class RFIService:

    @staticmethod
    def create_rfi(
        subject,
        description,
        submitted_by
    ):

        return {
            "id": str(uuid.uuid4()),
            "rfi_number": f"RFI-{str(uuid.uuid4())[:8].upper()}",
            "subject": subject,
            "description": description,
            "submitted_by": submitted_by,
            "status": "Open",
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def answer_rfi(
        rfi,
        response,
        answered_by
    ):

        rfi["response"] = response
        rfi["answered_by"] = answered_by
        rfi["status"] = "Answered"

        return rfi

    @staticmethod
    def close_rfi(rfi):

        rfi["status"] = "Closed"

        return rfi
