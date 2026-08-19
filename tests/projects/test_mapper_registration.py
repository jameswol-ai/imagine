from sqlalchemy import inspect


def test_projects_mapper_registration():
    import projects.model_registry

    from database.models.organization import Organization
    from projects.approvals.models import Approval
    from projects.projects.models import Project
    from projects.revisions.models import Revision

    mapper = inspect(Project)

    assert (
        mapper.relationships["client"].mapper.class_
        is Organization
    )

    assert (
        mapper.relationships["approvals"].mapper.class_
        is Approval
    )

    assert (
        mapper.relationships["revisions"].mapper.class_
        is Revision
    )