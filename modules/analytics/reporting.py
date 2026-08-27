"""
Reporting Engine
"""

from datetime import datetime


class ReportingService:

    @staticmethod
    def generate_report(
        title,
        content
    ):

        return {
            "title": title,
            "content": content,
            "generated_at":
                datetime.utcnow().isoformat()
        }
