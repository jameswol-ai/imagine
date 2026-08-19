"""
Tests for generative design database models.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from architecture.generative_design.models import (
    Base,
    DesignCandidateRecord,
    GenerativeDesignRun,
)


def test_models_can_create_tables():
    engine = create_engine(
        "sqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    assert (
        "generative_design_runs"
        in Base.metadata.tables
    )

    assert (
        "generative_design_candidates"
        in Base.metadata.tables
    )


def test_run_and_candidate_relationship():
    engine = create_engine(
        "sqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine
    )

    session = Session()

    run = GenerativeDesignRun(
        name="Test Run",
        constraints={
            "site": {
                "width": 20,
                "depth": 30,
            }
        },
    )

    session.add(run)
    session.flush()

    candidate = DesignCandidateRecord(
        run_id=run.id,
        name="Option 1",
        score=85.0,
        geometry={
            "type": "rectangular_massing"
        },
        metrics={
            "storeys": 2
        },
        evaluation={
            "compliance": 100
        },
    )

    session.add(candidate)
    session.commit()

    session.refresh(run)

    assert len(run.candidates) == 1
    assert run.candidates[0].name == "Option 1"

    session.close()