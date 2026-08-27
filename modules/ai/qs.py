"""
AI Quantity Surveyor
"""

from modules.costing.boq import (
    BoQEngine
)


class AIQS:

    @staticmethod
    def generate_estimate(
        area,
        country
    ):

        return (
            BoQEngine.project_estimate(
                area,
                country
            )
        )
