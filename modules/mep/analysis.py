"""
IMAGINE MEP Engineering Module

Mechanical
Electrical
Plumbing

Version 24.1
"""

import math
from modules.mep.hvac import HVACService
from modules.mep.electrical import ElectricalService
from modules.mep.plumbing import PlumbingService


class MEPAnalysis:

    @classmethod
    def full_building_analysis(
        cls,
        area_m2,
        occupancy_type,
        occupants,
        bathrooms
    ):

        hvac = HVACService.cooling_load(
            area_m2,
            occupancy_type
        )

        electrical = ElectricalService.connected_load(
            area_m2,
            occupancy_type
        )

        plumbing = PlumbingService.water_demand(
            occupants
        )

        wsfu = PlumbingService.wsfu(
            bathrooms,
            area_m2
        )

        return {
            "hvac": hvac,
            "electrical": electrical,
            "plumbing": plumbing,
            "wsfu": wsfu
        }




class MEPAnalysis:

    # --------------------------------------------------
    # HVAC
    # --------------------------------------------------

    HVAC_DENSITIES = {
        "Residential": 120,
        "Commercial": 160,
        "Industrial": 100
    }

    @classmethod
    def cooling_load(
        cls,
        area_m2: float,
        occupancy_type: str = "Residential"
    ) -> dict:
        """
        Preliminary cooling load estimate.
        """

        density = cls.HVAC_DENSITIES.get(
            occupancy_type,
            120
        )

        cooling_kw = (
            area_m2 * density
        ) / 1000

        cooling_tr = (
            cooling_kw / 3.517
        )

        airflow_cfm = (
            cooling_tr * 400
        )

        return {
            "area_m2": round(area_m2, 2),
            "cooling_kw": round(cooling_kw, 2),
            "cooling_tr": round(cooling_tr, 2),
            "airflow_cfm": round(
                airflow_cfm,
                0
            )
        }

    # --------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------

    ELECTRICAL_DENSITIES = {
        "Residential": 35,
        "Commercial": 65,
        "Industrial": 85
    }

    @classmethod
    def electrical_load(
        cls,
        area_m2: float,
        occupancy_type: str = "Residential",
        power_factor: float = 0.85
    ) -> dict:

        density = cls.ELECTRICAL_DENSITIES.get(
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
            "connected_kw": round(
                connected_kw,
                2
            ),
            "connected_kva": round(
                connected_kva,
                2
            )
        }

    @staticmethod
    def maximum_demand(
        connected_kva: float,
        diversity_factor: float = 0.8
    ) -> dict:

        demand_kva = (
            connected_kva
            * diversity_factor
        )

        transformer = math.ceil(
            (
                demand_kva * 1.25
            ) / 50
        ) * 50

        return {
            "max_demand_kva": round(
                demand_kva,
                2
            ),
            "transformer_kva": transformer
        }

    # --------------------------------------------------
    # PLUMBING
    # --------------------------------------------------

    @staticmethod
    def plumbing_demand(
        occupants: int,
        litres_per_person: float = 150
    ) -> dict:

        daily_demand = (
            occupants
            * litres_per_person
        )

        return {
            "occupants": occupants,
            "daily_demand_liters": round(
                daily_demand,
                2
            )
        }

    @staticmethod
    def wsfu_calculation(
        bathrooms: int,
        area_m2: float
    ) -> dict:
        """
        Water Supply Fixture Units
        """

        wsfu = (
            bathrooms * 8
        ) + (
            math.ceil(area_m2 / 100) * 4
        )

        peak_flow = (
            math.sqrt(wsfu)
            * 0.25
        )

        return {
            "wsfu": wsfu,
            "peak_flow_lps": round(
                peak_flow,
                2
            )
        }

    # --------------------------------------------------
    # COMPLETE SYSTEM SUMMARY
    # --------------------------------------------------

    @classmethod
    def full_building_analysis(
        cls,
        area_m2: float,
        occupancy_type: str,
        occupants: int,
        bathrooms: int
    ) -> dict:

        hvac = cls.cooling_load(
            area_m2,
            occupancy_type
        )

        electrical = cls.electrical_load(
            area_m2,
            occupancy_type
        )

        demand = cls.maximum_demand(
            electrical["connected_kva"]
        )

        plumbing = cls.plumbing_demand(
            occupants
        )

        wsfu = cls.wsfu_calculation(
            bathrooms,
            area_m2
        )

        return {
            "hvac": hvac,
            "electrical": electrical,
            "demand": demand,
            "plumbing": plumbing,
            "wsfu": wsfu
        }
