"""
IMAGINE Structural Module

Beam Design Engine
EN 1992 Preliminary Design

Version 24.1
"""

from modules.structural.eurocode import EurocodeEngine


class BeamDesignService:

    @staticmethod
    def analyze(
        beam_id,
        span,
        gk,
        qk,
        material="Concrete C30/37"
    ):

        result = (
            EurocodeEngine
            .simply_supported_beam(
                span=span,
                gk=gk,
                qk=qk
            )
        )

        return {
            "beam_id": beam_id,
            "material": material,
            **result,
            "status":
                EurocodeEngine.beam_status_check(
                    result["moment_kNm"]
                )
        }
