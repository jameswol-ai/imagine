"""
AI Project Manager
"""

class AIProjectManager:

    @staticmethod
    def project_health(
        progress,
        budget_variance
    ):

        if progress < 50 and budget_variance > 10:
            return "High Risk"

        if progress < 75:
            return "Monitor"

        return "Healthy"
