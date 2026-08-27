"""
IMAGINE Documents Module

Revision Control

Version 24.1
"""

from datetime import datetime


class RevisionService:

    REVISION_SEQUENCE = [
        "A1",
        "A2",
        "A3",
        "B1",
        "B2",
        "IFC",
        "AS-BUILT"
    ]

    @classmethod
    def next_revision(
        cls,
        current_revision
    ):

        if current_revision not in cls.REVISION_SEQUENCE:
            return cls.REVISION_SEQUENCE[0]

        index = cls.REVISION_SEQUENCE.index(
            current_revision
        )

        if index < len(cls.REVISION_SEQUENCE) - 1:
            return cls.REVISION_SEQUENCE[index + 1]

        return current_revision

    @staticmethod
    def create_revision_record(
        document_no,
        revision,
        issued_by
    ):

        return {
            "document_no": document_no,
            "revision": revision,
            "issued_by": issued_by,
            "issued_at": datetime.utcnow().isoformat()
        }
