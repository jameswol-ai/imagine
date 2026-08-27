"""
IMAGINE Analytics Module

KPI Engine
"""

class KPIService:

    @staticmethod
    def budget_variance(
        planned,
        actual
    ):

        variance = actual - planned

        return {
            "planned": planned,
            "actual": actual,
            "variance": variance,
            "variance_percent":
                round(
                    (variance / planned) * 100,
                    2
                ) if planned else 0
        }

    @staticmethod
    def schedule_variance(
        planned_days,
        actual_days
    ):

        return actual_days - planned_days
