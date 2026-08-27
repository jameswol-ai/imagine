"""
IMAGINE Structural Module

Retaining Wall Engine

Version 24.1
"""


class RetainingWallService:

    @staticmethod
    def preliminary_stability(
        wall_id,
        wall_height,
        wall_thickness
    ):

        ratio = (
            wall_height /
            wall_thickness
        )

        return {
            "wall_id": wall_id,
            "height_m": wall_height,
            "thickness_m": wall_thickness,
            "height_thickness_ratio":
                round(ratio, 2),
            "status":
                (
                    "OK"
                    if ratio < 15
                    else "REVIEW"
                )
        }
