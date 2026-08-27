"""
AI MEP Engineer
"""

from modules.mep.analysis import (
    MEPAnalysis
)


class AIMEP:

    @staticmethod
    def design_services(
        area,
        occupancy,
        occupants,
        bathrooms
    ):

        return (
            MEPAnalysis
            .full_building_analysis(
                area,
                occupancy,
                occupants,
                bathrooms
            )
        )
