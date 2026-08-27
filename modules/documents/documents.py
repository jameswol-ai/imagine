"""
IMAGINE Documents Module

Document Management

Version 24.1
"""

import uuid
from datetime import datetime


class DocumentService:

    @staticmethod
    def create_document(
        title,
        document_type,
        uploaded_by
    ):

        return {
            "id": str(uuid.uuid4()),
            "document_no": f"DOC-{str(uuid.uuid4())[:8].upper()}",
            "title": title,
            "document_type": document_type,
            "uploaded_by": uploaded_by,
            "status": "Draft",
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def issue_document(
        document,
        revision
    ):

        document["revision"] = revision
        document["status"] = "Issued"

        return document

    @staticmethod
    def archive_document(
        document
    ):

        document["status"] = "Archived"

        return document
