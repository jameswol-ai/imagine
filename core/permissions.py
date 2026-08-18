"""
Role Based Access Control (RBAC)
"""

from core.settings import settings


def has_role(
        user_role,
        required_roles
):

    return user_role in required_roles


def can_approve(
        user_role
):

    return has_role(
        user_role,
        settings.APPROVAL_ROLES
    )


def is_admin(
        user_role
):

    return user_role == "Admin"
