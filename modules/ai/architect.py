"""
AI Architect
"""

from modules.architecture.synthesis import (
    ArchitectureSynthesis
)


class AIArchitect:

    @staticmethod
    def generate_concept(
        project_name,
        building_type,
        floors,
        plot_area,
        country
    ):

        return (
            ArchitectureSynthesis
            .generate_building(
                project_name,
                building_type,
                floors,
                plot_area,
                country
            )
        )
