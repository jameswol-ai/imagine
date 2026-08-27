"""
IMAGINE Construction Module

Site Diary

Version 24.1
"""

from datetime import datetime


class SiteDiaryService:

    @staticmethod
    def create_entry(
        project_code,
        author,
        notes
    ):

        return {
            "project_code": project_code,
            "author": author,
            "notes": notes,
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def weather_record(
        condition,
        temperature
    ):

        return {
            "weather": condition,
            "temperature": temperature
        }
