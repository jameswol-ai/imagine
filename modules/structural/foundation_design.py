"""
IMAGINE Structural Module

Foundation Design Engine

Version 24.1
"""


class FoundationDesignService:

    @staticmethod
    def bearing_check(
        foundation_type,
        column_load,
        footing_area,
        soil_capacity
    ):

        bearing_pressure = (
            column_load / footing_area
        )

        return {
            "foundation_type":
                foundation_type,

            "bearing_pressure":
                round(
                    bearing_pressure,
                    2
                ),

            "soil_capacity":
                soil_capacity,

            "status":
                (
                    "PASS"
                    if bearing_pressure
                    <= soil_capacity
                    else "FAIL"
                )
        }
