"""
IMAGINE Costing Module

Cost Escalation Engine

Version 24.1
"""


class EscalationService:

    @staticmethod
    def escalate_cost(
        base_cost,
        inflation_rate,
        years
    ):

        future_cost = (
            base_cost
            *
            ((1 + inflation_rate) ** years)
        )

        return {

            "base_cost": base_cost,

            "inflation_rate":
                inflation_rate,

            "years":
                years,

            "future_cost":
                round(
                    future_cost,
                    2
                )
        }
