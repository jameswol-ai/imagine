"""
IMAGINE MEP Module

Plumbing Design Engine

Version 24.1
"""

import math


class PlumbingService:

    @staticmethod
    def water_demand(
        occupants,
        demand_per_person=150
    ):

        demand = (
            occupants
            * demand_per_person
        )

        return {
            "occupants": occupants,
            "daily_water_liters":
                round(demand, 2)
        }

    @staticmethod
    def wsfu(
        bathrooms,
        area_m2
    ):

        total_wsfu = (
            bathrooms * 8
        ) + (
            math.ceil(area_m2 / 100) * 4
        )

        peak_flow = (
            math.sqrt(total_wsfu)
            * 0.25
        )

        return {
            "wsfu": total_wsfu,
            "peak_flow_lps":
                round(peak_flow, 2)
        }
