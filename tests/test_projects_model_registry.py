"""Regression tests for the Projects ORM relationship graph."""

from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers


def test_projects_relationship_targets_are_registered():
    from projects.model_registry import Approval, Organization, Project, Revision, User

    configure_mappers()

    assert inspect(Project).relationships["approvals"].mapper.class_ is Approval
    assert inspect(Project).relationships["revisions"].mapper.class_ is Revision
    assert inspect(Project).relationships["client"].mapper.class_ is Organization
    assert inspect(Approval).relationships["approver"].mapper.class_ is User
    assert inspect(Revision).relationships["author"].mapper.class_ is User


def test_project_database_types_match_schema_contract():
    from projects.projects.models import Project

    assert Project.__table__.c.id.type.python_type is not None
    assert Project.__table__.c.client_id.type.python_type is int
