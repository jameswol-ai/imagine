"""
Predictive Maintenance
"""

class PredictiveAIService:

    @staticmethod
    def evaluate(
        readings
    ):

        if not readings:
            return "No Data"

        avg = (
            sum(readings)
            / len(readings)
        )

        if avg > 80:
            return "Inspection Recommended"

        return "Healthy"
