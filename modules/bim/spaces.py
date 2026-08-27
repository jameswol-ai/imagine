"""
IMAGINE BIM Module

Space Service

Version 24.1
"""

import uuid


class SpaceService:

    @staticmethod
    def create_space(
        name,
        space_type,
        area,
        height,
        storey_id
    ):

        return {
            "id": str(uuid.uuid4()),
            "storey_id": storey_id,
            "name": name,
            "space_type": space_type,
            "area": area,
            "height": height
        }

    @staticmethod
    def update_space(
        space,
        updates
    ):

        space.update(updates)

        return space

    @staticmethod
    def delete_space(
        space_id,
        spaces
    ):

        return [
            s for s in spaces
            if str(s["id"]) != str(space_id)
        ]

    @staticmethod
    def total_space_area(
        spaces
    ):

        return round(
            sum(
                s.get("area", 0)
                for s in spaces
            ),
            2
        )

    @staticmethod
    def occupancy_estimate(
        spaces,
        factor=10
    ):

        total_area = (
            SpaceService.total_space_area(
                spaces
            )
        )

        return int(
            total_area / factor
        )
