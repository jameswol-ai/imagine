"""
IMAGINE BIM Module

IFC Export Engine
IFC4 Metadata Generator

Version 24.1
"""

import json
import uuid
from datetime import datetime


class IFCExportEngine:

    @staticmethod
    def generate_guid():
        """
        Generate unique IFC-like GUID.
        """

        return str(
            uuid.uuid4()
        )

    @classmethod
    def create_project(
        cls,
        project_name
    ):

        return {
            "GlobalId": cls.generate_guid(),
            "Type": "IfcProject",
            "Name": project_name
        }

    @classmethod
    def create_site(
        cls,
        site_name="Default Site"
    ):

        return {
            "GlobalId": cls.generate_guid(),
            "Type": "IfcSite",
            "Name": site_name
        }

    @classmethod
    def create_building(
        cls,
        building_name,
        floors,
        gross_floor_area
    ):

        return {
            "GlobalId": cls.generate_guid(),
            "Type": "IfcBuilding",
            "Name": building_name,
            "Storeys": floors,
            "GrossFloorArea": gross_floor_area
        }

    @classmethod
    def create_storeys(
        cls,
        floors
    ):

        storeys = []

        for level in range(
            1,
            floors + 1
        ):

            storeys.append({
                "GlobalId": cls.generate_guid(),
                "Type": "IfcBuildingStorey",
                "Name": f"Level {level}",
                "Elevation": (level - 1) * 3.5
            })

        return storeys

    @classmethod
    def create_spaces(
        cls,
        room_schedule
    ):

        spaces = []

        for room in room_schedule:

            spaces.append({
                "GlobalId": cls.generate_guid(),
                "Type": "IfcSpace",
                "Name": room["room_name"],
                "Storey": room["floor"]
            })

        return spaces

    @classmethod
    def export_building_metadata(
        cls,
        synthesis_result
    ):
        """
        Create IFC-compatible metadata
        from Architecture Synthesis.
        """

        project_name = synthesis_result[
            "project_name"
        ]

        building_data = synthesis_result[
            "building_parameters"
        ]

        floors = building_data[
            "floors"
        ]

        gross_floor_area = building_data[
            "gross_floor_area_m2"
        ]

        room_schedule = synthesis_result[
            "rooms"
        ]

        payload = {

            "generated_at":
                datetime.utcnow().isoformat(),

            "schema":
                "IFC4",

            "IfcProject":
                cls.create_project(
                    project_name
                ),

            "IfcSite":
                cls.create_site(),

            "IfcBuilding":
                cls.create_building(
                    project_name,
                    floors,
                    gross_floor_area
                ),

            "IfcBuildingStoreys":
                cls.create_storeys(
                    floors
                ),

            "IfcSpaces":
                cls.create_spaces(
                    room_schedule
                )
        }

        return payload

    @staticmethod
    def export_json(
        metadata
    ):

        return json.dumps(
            metadata,
            indent=4
        )

    @staticmethod
    def building_summary(
        metadata
    ):

        return {

            "project":
                metadata["IfcProject"]["Name"],

            "storeys":
                len(
                    metadata[
                        "IfcBuildingStoreys"
                    ]
                ),

            "spaces":
                len(
                    metadata[
                        "IfcSpaces"
                    ]
                ),

            "schema":
                metadata["schema"]
        }
