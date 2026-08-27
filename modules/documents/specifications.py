"""
IMAGINE Documents Module

Technical Specifications

Version 24.1
"""

import uuid


class SpecificationService:

    @staticmethod
    def create_specification(
        title,
        section,
        discipline
    ):

        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "section": section,
            "discipline": discipline,
            "status": "Draft"
        }

    @staticmethod
    def approve_specification(
        specification
    ):

        specification["status"] = "Approved"

        return specification
