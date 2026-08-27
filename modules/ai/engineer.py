"""
AI Structural Engineer
"""

from modules.structural.beam_design import (
    BeamDesignService
)


class AIEngineer:

    @staticmethod
    def recommend_beam(
        span,
        load
    ):

        return (
            BeamDesignService.analyze(
                beam_id="AI-BEAM",
                span=span,
                gk=load,
                qk=load * 0.5
            )
        )
