"""
IMAGINE MEP Module

Electrical Design Engine

Version 24.1
"""

import math


class ElectricalService:

    LOAD_DENSITIES = {
        "Residential": 35,
        "Commercial": 65,
        "Industrial": 85
    }

    @classmethod
    def connected_load(
        cls,
        area_m2,
        occupancy_type="Commercial",
        power_factor=0.85
    ):

        density = cls.LOAD_DENSITIES.get(
            occupancy_type,
            50
        )

        connected_kw = (
            area_m2 * density
        ) / 1000

        connected_kva = (
            connected_kw / power_factor
        )

        return {
            "connected_kw":
                round(connected_kw, 2),

            "connected_kva":
                round(connected_kva, 2)
        }

    @staticmethod
    def transformer_sizing(
        demand_kva
    ):

        transformer = (
            math.ceil(
                demand_kva / 50
            ) * 50
        )

        return {
            "transformer_kva":
                transformer
        }

    @staticmethod
    def demand_load(
        connected_kva,
        diversity_factor=0.80
    ):

        demand = (
            connected_kva
            * diversity_factor
        )

        return {
            "demand_kva":
                round(demand, 2)
        }
