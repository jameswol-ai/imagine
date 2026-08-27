"""
IMAGINE Construction Module

Progress Tracking

Version 24.1
"""

from datetime import datetime


class ProgressTrackingService:

    @staticmethod
    def create_progress_record(
        activity,
        planned,
        actual
    ):

        variance = actual - planned

        return {
            "activity": activity,
            "planned_percent": planned,
            "actual_percent": actual,
            "variance": variance,
            "date": datetime.utcnow().isoformat()
        }

    @staticmethod
    def schedule_status(
        variance
    ):

        if variance >= 0:
            return "On Track"

        if variance >= -10:
            return "Minor Delay"

        return "Critical Delay"
