"""
IMAGINE Documents Module

Document Transmittals

Version 24.1
"""

import uuid
from datetime import datetime


class TransmittalService:

    @staticmethod
    def create_transmittal(
        recipient,
        subject,
        documents
    ):

        return {
            "id": str(uuid.uuid4()),
            "transmittal_no":
                f"TRM-{str(uuid.uuid4())[:8].upper()}",
            "recipient": recipient,
            "subject": subject,
            "documents": documents,
            "status": "Issued",
            "issued_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def acknowledge(
        transmittal,
        recipient
    ):

        transmittal["acknowledged_by"] = recipient
        transmittal["status"] = "Received"

        return transmittal
