"""
IMAGINE Costing Module

Cost Risk Analysis

Version 24.1
"""


class RiskAnalysisService:

    @staticmethod
    def contingency(
        project_cost,
        risk_percentage=0.10
    ):

        contingency = (
            project_cost
            * risk_percentage
        )

        return {

            "base_cost":
                project_cost,

            "risk_percentage":
                risk_percentage,

            "contingency":
                round(
                    contingency,
                    2
                ),

            "recommended_budget":
                round(
                    project_cost +
                    contingency,
                    2
                )
        }

    @staticmethod
    def risk_rating(
        risk_percentage
    ):

        if risk_percentage < 0.05:
            return "Low"

        if risk_percentage < 0.15:
            return "Medium"

        return "High"
