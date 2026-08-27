"""
IMAGINE Costing Module

Procurement Engine

Version 24.1
"""

from datetime import datetime
import uuid


class ProcurementService:

    @staticmethod
    def create_package(
        name,
        value,
        package_type
    ):

        return {
            "id":
                str(uuid.uuid4()),

            "name":
                name,

            "value":
                value,

            "package_type":
                package_type,

            "status":
                "Planned",

            "created_at":
                datetime.utcnow().isoformat()
        }

    @staticmethod
    def award_package(
        package,
        contractor
    ):

        package["contractor"] = contractor
        package["status"] = "Awarded"

        return package
