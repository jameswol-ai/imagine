"""
IMAGINE Documents Module

Drawing Register

Version 24.1
"""

import uuid


class DrawingRegisterService:

    @staticmethod
    def create_drawing(
        drawing_no,
        title,
        discipline
    ):

        return {
            "id": str(uuid.uuid4()),
            "drawing_no": drawing_no,
            "title": title,
            "discipline": discipline,
            "revision": "A1",
            "status": "Draft"
        }

    @staticmethod
    def update_revision(
        drawing,
        revision
    ):

        drawing["revision"] = revision

        return drawing
