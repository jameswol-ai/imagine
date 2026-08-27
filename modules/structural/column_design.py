"""
IMAGINE Structural Module

Column Design Engine

Version 24.1
"""


class ColumnDesignService:

    @staticmethod
    def analyze(
        column_id,
        axial_load,
        width,
        depth
    ):

        area = width * depth

        stress = axial_load / area

        return {
            "column_id": column_id,
            "axial_load_kN": axial_load,
            "section_mm": f"{width}x{depth}",
            "area_mm2": area,
            "stress": round(stress, 2),
            "status":
                "OK"
                if stress < 15
                else "REVIEW"
        }
