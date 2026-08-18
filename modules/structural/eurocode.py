"""
IMAGINE Structural Engineering Module

Eurocode Design Engine
EN 1990 / EN 1991 / EN 1992 Concept Foundation

Version: 24.1
"""

import math


class EurocodeEngine:
    """
    Basic Eurocode structural calculations.
    """

    @staticmethod
    def ultimate_line_load(
        gk: float,
        qk: float
    ) -> float:
        """
        EN 1990 ULS Combination

        q_ed = 1.35Gk + 1.50Qk
        """

        return round(
            (1.35 * gk) + (1.50 * qk),
            2
        )

    @staticmethod
    def simply_supported_beam(
        span: float,
        gk: float,
        qk: float
    ) -> dict:
        """
        Simply supported beam.

        Returns:
        Design load
        Design bending moment
        Design shear
        """

        q_ed = EurocodeEngine.ultimate_line_load(
            gk,
            qk
        )

        m_ed = (
            q_ed * span ** 2
        ) / 8

        v_ed = (
            q_ed * span
        ) / 2

        return {
            "span_m": round(span, 2),
            "q_ed_kN_per_m": round(q_ed, 2),
            "moment_kNm": round(m_ed, 2),
            "shear_kN": round(v_ed, 2)
        }

    @staticmethod
    def slab_loading(
        area_load_gk: float,
        area_load_qk: float
    ) -> dict:
        """
        Slab ULS loading.
        """

        q_ed = (
            1.35 * area_load_gk
            +
            1.50 * area_load_qk
        )

        return {
            "uls_load_kN_m2": round(q_ed, 2)
        }

    @staticmethod
    def column_axial_force(
        tributary_area: float,
        gk: float,
        qk: float
    ) -> dict:
        """
        Simple column axial load estimate.
        """

        q_ed = (
            1.35 * gk
            +
            1.50 * qk
        )

        axial_force = q_ed * tributary_area

        return {
            "tributary_area_m2": round(
                tributary_area,
                2
            ),
            "axial_force_kN": round(
                axial_force,
                2
            )
        }

    @staticmethod
    def beam_status_check(
        moment_kNm: float,
        allowable_kNm: float = 250
    ) -> str:
        """
        Basic pass/fail screening.
        """

        if moment_kNm <= allowable_kNm:
            return "PASS"

        return "REVIEW"

    @staticmethod
    def deflection_ratio(
        span_m: float,
        deflection_mm: float
    ) -> dict:
        """
        Span/deflection ratio.
        """

        span_mm = span_m * 1000

        ratio = span_mm / deflection_mm

        return {
            "ratio": round(ratio, 2),
            "status": (
                "PASS"
                if ratio >= 250
                else "REVIEW"
            )
        }
