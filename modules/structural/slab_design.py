"""
IMAGINE Structural Module

Slab Design Engine

Version 24.1
"""


class SlabDesignService:

    @staticmethod
    def analyze(
        slab_id,
        span,
        load,
        thickness
    ):

        span_thickness = (
            span * 1000
        ) / thickness

        return {
            "slab_id": slab_id,
            "span_m": span,
            "load_kN_m2": load,
            "thickness_mm": thickness,
            "span_thickness_ratio":
                round(span_thickness, 2),
            "status":
                "OK"
                if span_thickness < 35
                else "REVIEW"
        }
