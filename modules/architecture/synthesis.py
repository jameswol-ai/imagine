"""
IMAGINE Architecture Synthesis Engine

Generative Design
Space Programming
Zoning Analysis
Building Synthesis

Version 24.1
"""

import math
from datetime import datetime

from modules.structural.eurocode import EurocodeEngine
from modules.mep.analysis import MEPAnalysis
from modules.costing.boq import BoQEngine


class ArchitectureSynthesis:

    @staticmethod
    def calculate_footprint(
        plot_area: float,
        coverage_ratio: float = 0.40
    ) -> float:
        """
        Building footprint based on site coverage.
        """

        return round(
            plot_area * coverage_ratio,
            2
        )

    @staticmethod
    def calculate_gfa(
        footprint_area: float,
        floors: int
    ) -> float:
        """
        Gross Floor Area.
        """

        return round(
            footprint_area * floors,
            2
        )

    @staticmethod
    def estimate_occupancy(
        gross_floor_area: float,
        factor: float = 15
    ) -> int:
        """
        Preliminary occupant estimate.
        """

        return max(
            2,
            math.ceil(gross_floor_area / factor)
        )

    @staticmethod
    def generate_room_schedule(
        building_type: str,
        floors: int
    ):

        schedules = {

            "Residential": [
                "Living Room",
                "Bedroom",
                "Bedroom",
                "Kitchen",
                "Bathroom"
            ],

            "Commercial": [
                "Lobby",
                "Office",
                "Office",
                "Meeting Room",
                "Washroom"
            ],

            "Mixed Use": [
                "Retail Space",
                "Office",
                "Office",
                "Lobby",
                "Washroom"
            ]
        }

        base_rooms = schedules.get(
            building_type,
            schedules["Commercial"]
        )

        rooms = []

        for floor in range(1, floors + 1):

            for room in base_rooms:

                rooms.append({
                    "floor": floor,
                    "room_name": room
                })

        return rooms

    @staticmethod
    def zoning_check(
        footprint_area: float,
        plot_area: float,
        max_coverage: float = 0.50
    ):

        actual_coverage = (
            footprint_area / plot_area
        )

        return {
            "coverage": round(
                actual_coverage,
                2
            ),
            "limit": max_coverage,
            "status": (
                "PASS"
                if actual_coverage <= max_coverage
                else "VIOLATION"
            )
        }

    @classmethod
    def generate_building(
        cls,
        project_name: str,
        building_type: str,
        floors: int,
        plot_area: float,
        country: str = "Uganda"
    ):

        footprint = cls.calculate_footprint(
            plot_area
        )

        gfa = cls.calculate_gfa(
            footprint,
            floors
        )

        occupants = cls.estimate_occupancy(
            gfa
        )

        rooms = cls.generate_room_schedule(
            building_type,
            floors
        )

        zoning = cls.zoning_check(
            footprint,
            plot_area
        )

        structural = (
            EurocodeEngine
            .simply_supported_beam(
                span=6.0,
                gk=15.0,
                qk=10.0
            )
        )

        mep = (
            MEPAnalysis
            .full_building_analysis(
                area_m2=gfa,
                occupancy_type=(
                    "Commercial"
                    if building_type != "Residential"
                    else "Residential"
                ),
                occupants=occupants,
                bathrooms=max(2, floors)
            )
        )

        cost = (
            BoQEngine
            .project_estimate(
                gross_floor_area=gfa,
                country=country
            )
        )

        return {

            "project_name": project_name,

            "building_type": building_type,

            "country": country,

            "generated_at":
                datetime.utcnow().isoformat(),

            "building_parameters": {

                "plot_area_m2": plot_area,

                "footprint_area_m2":
                    footprint,

                "floors":
                    floors,

                "gross_floor_area_m2":
                    gfa,

                "estimated_occupants":
                    occupants
            },

            "rooms": rooms,

            "zoning": zoning,

            "structural": structural,

            "mep": mep,

            "costing": cost
        }
