"""
IMAGINE BIM Module

Building Service

Version 24.1
"""

import uuid
from datetime import datetime


class BuildingService:

    @staticmethod
    def create_building(
        name,
        storeys=1,
        area=0.0,
        ifc_version="IFC4",
        description=""
    ):

        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "storeys": storeys,
            "area": area,
            "ifc_version": ifc_version,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def update_building(
        building,
        updates
    ):

        building.update(updates)

        building["updated_at"] = (
            datetime.utcnow().isoformat()
        )

        return building

    @staticmethod
    def delete_building(
        building_id,
        buildings
    ):

        return [
            b for b in buildings
            if str(b["id"]) != str(building_id)
        ]

    @staticmethod
    def total_area(
        buildings
    ):

        return round(
            sum(
                b.get("area", 0)
                for b in buildings
            ),
            2
        )
