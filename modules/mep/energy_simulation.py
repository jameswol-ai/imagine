"""
IMAGINE MEP Module

Energy Simulation Engine

Version 24.1
"""

from datetime import datetime


class EnergySimulationService:

    @staticmethod
    def annual_energy_use(
        area_m2,
        eui=180
    ):
        """
        EUI = kWh/m²/year
        """

        annual_energy = (
            area_m2 * eui
        )

        return {
            "area_m2": area_m2,
            "eui": eui,
            "annual_energy_kwh":
                round(annual_energy, 2)
        }

    @staticmethod
    def carbon_emissions(
        annual_energy_kwh,
        emission_factor=0.35
    ):

        emissions = (
            annual_energy_kwh
            * emission_factor
        )

        return {
            "co2_kg":
                round(emissions, 2),

            "co2_tonnes":
                round(
                    emissions / 1000,
                    2
                )
        }

    @staticmethod
    def building_performance(
        area_m2
    ):

        energy = (
            EnergySimulationService
            .annual_energy_use(area_m2)
        )

        carbon = (
            EnergySimulationService
            .carbon_emissions(
                energy["annual_energy_kwh"]
            )
        )

        return {
            "generated_at":
                datetime.utcnow().isoformat(),

            "energy": energy,

            "carbon": carbon
        }
