"""
Tests for the generative design repository.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from architecture.generative_design.models import Base
from architecture.generative_design.repository import (
    GenerativeDesignRepository,
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


def test_create_and_get_run():
    session = create_session()

    repository = GenerativeDesignRepository(
        session
    )

    run = repository.create_run(
        project_id=None,
        name="Test Run",
        constraints={
            "site": {
                "width": 20,
                "depth": 30,
            }
        },
    )

    session.commit()

    result = repository.get_run(
        run.id
    )

    assert result is not None
    assert result.name == "Test Run"

    session.close()


def test_add_candidate():
    session = create_session()

    repository = GenerativeDesignRepository(
        session
    )

    run = repository.create_run(
        project_id=None,
        name="Test Run",
        constraints={},
    )

    candidate = repository.add_candidate(
        run=run,
        name="Option 1",
        score=90,
        rank=1,
        geometry={
            "type": "rectangle"
        },
        metrics={
            "area": 500
        },
        evaluation={
            "compliance": 100
        },
    )

    session.commit()

    candidates = repository.list_candidates(
        run.id
    )

    assert len(candidates) == 1
    assert candidates[0].id == candidate.id

    session.close()


def test_delete_run():
    session = create_session()

    repository = GenerativeDesignRepository(
        session
    )

    run = repository.create_run(
        project_id=None,
        name="Delete Me",
        constraints={},
    )

    session.commit()

    repository.delete_run(
        run
    )

    session.commit()

    assert repository.get_run(
        run.id
    ) is None

    session.close()