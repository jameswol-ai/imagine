"""
Asset Registry
"""

import uuid


class AssetService:

    @staticmethod
    def create_asset(
        name,
        category,
        location
    ):

        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "category": category,
            "location": location,
            "status": "Operational"
        }
