"""
IMAGINE MEP Module

HVAC Design Engine

Version 24.1
"""


class HVACService:

    LOAD_DENSITIES = {
        "Residential": 120,
        "Commercial": 160,
        "Industrial": 100
    }

    @classmethod
    def cooling_load(
        cls,
        area_m2,
        occupancy_type="Commercial"
    ):

        density = cls.LOAD_DENSITIES.get(
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
            "area_m2": area_m2,
            "occupancy_type": occupancy_type,
            "cooling_kw": round(cooling_kw, 2),
            "cooling_tr": round(cooling_tr, 2),
            "airflow_cfm": round(airflow_cfm, 0)
        }

    @staticmethod
    def equipment_selection(
        cooling_kw
    ):

        units = max(
            1,
            round(cooling_kw / 35)
        )

        return {
            "recommended_units": units,
            "unit_capacity_kw":
                round(cooling_kw / units, 2)
        }
