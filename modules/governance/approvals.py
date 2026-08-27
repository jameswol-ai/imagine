"""
IMAGINE Governance Module

Approval Workflow Engine
Version 24.1
"""

from datetime import datetime


class ApprovalEngine:

    VALID_STATUSES = [
        "Pending",
        "Approved",
        "Rejected",
        "Returned"
    ]

    @staticmethod
    def create_request(
        project_code,
        submitted_by,
        comments=""
    ):

        return {
            "project_code": project_code,
            "submitted_by": submitted_by,
            "status": "Pending",
            "comments": comments,
            "created_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def approve(
        request,
        approved_by,
        remarks=""
    ):

        request["status"] = "Approved"
        request["approved_by"] = approved_by
        request["remarks"] = remarks
        request["approved_at"] = datetime.utcnow().isoformat()

        return request

    @staticmethod
    def reject(
        request,
        approved_by,
        remarks=""
    ):

        request["status"] = "Rejected"
        request["approved_by"] = approved_by
        request["remarks"] = remarks
        request["approved_at"] = datetime.utcnow().isoformat()

        return request

    @staticmethod
    def return_for_revision(
        request,
        approved_by,
        remarks=""
    ):

        request["status"] = "Returned"
        request["approved_by"] = approved_by
        request["remarks"] = remarks
        request["approved_at"] = datetime.utcnow().isoformat()

        return request
