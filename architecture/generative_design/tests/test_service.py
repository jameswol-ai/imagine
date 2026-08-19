"""
Tests for the generative design service.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from architecture.generative_design.models import Base
from architecture.generative_design.schemas import (
    GenerativeDesignRunCreate,
)
from architecture.generative_design.seed import (
    demo_constraints,
)
from architecture.generative_design.service import (
    GenerativeDesignService,
)


def create_session():
    engine = create_engine(
        "sqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine
    )

    return Session()


def test_create_design_run():
    session = create_session()

    service = GenerativeDesignService(
        session
    )

    request = GenerativeDesignRunCreate(
        name="Service Test",
        constraints=demo_constraints(),
        candidate_count=3,
    )

    run = service.create_run(
        request
    )

    assert run.id is not None
    assert run.status == "completed"
    assert run.candidate_count == 3

    candidates = service.get_candidates(
        run.id
    )

    assert len(candidates) == 3

    session.close()


def test_get_run():
    session = create_session()

    service = GenerativeDesignService(
        session
    )

    request = GenerativeDesignRunCreate(
        name="Get Test",
        constraints=demo_constraints(),
        candidate_count=2,
    )

    created = service.create_run(
        request
    )

    found = service.get_run(
        created.id
    )

    assert found is not None
    assert found.id == created.id

    session.close()


def test_delete_run():
    session = create_session()

    service = GenerativeDesignService(
        session
    )

    request = GenerativeDesignRunCreate(
        name="Delete Test",
        constraints=demo_constraints(),
        candidate_count=1,
    )

    run = service.create_run(
        request
    )

    deleted = service.delete_run(
        run.id
    )

    assert deleted is True
    assert service.get_run(
        run.id
    ) is None

    session.close()