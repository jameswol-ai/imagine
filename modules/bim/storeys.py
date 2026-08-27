"""
IMAGINE BIM Module

Storey Service

Version 24.1
"""

import uuid


class StoreyService:

    @staticmethod
    def create_storey(
        level,
        height,
        area,
        building_id
    ):

        return {
            "id": str(uuid.uuid4()),
            "building_id": building_id,
            "level": level,
            "height": height,
            "area": area
        }

    @staticmethod
    def update_storey(
        storey,
        updates
    ):

        storey.update(updates)

        return storey

    @staticmethod
    def delete_storey(
        storey_id,
        storeys
    ):

        return [
            s for s in storeys
            if str(s["id"]) != str(storey_id)
        ]

    @staticmethod
    def total_floor_area(
        storeys
    ):

        return round(
            sum(
                s.get("area", 0)
                for s in storeys
            ),
            2
        )
