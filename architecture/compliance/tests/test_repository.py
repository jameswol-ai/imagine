from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.connection import Base

from architecture.compliance.models import ComplianceAssessment
from architecture.compliance.repository import ComplianceRepository


def make_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return Session(engine)


def test_create_and_get_assessment():
    db = make_session()

    repository = ComplianceRepository(db)

    assessment = ComplianceAssessment(
        name="Test Assessment",
        status="PENDING",
        score=0,
    )

    created = repository.create_assessment(
        assessment
    )

    found = repository.get_assessment(
        created.id
    )

    assert found is not None
    assert found.name == "Test Assessment"

    db.close()


def test_list_assessments():
    db = make_session()

    repository = ComplianceRepository(db)

    repository.create_assessment(
        ComplianceAssessment(
            name="Assessment A",
            status="PENDING",
            score=0,
        )
    )

    repository.create_assessment(
        ComplianceAssessment(
            name="Assessment B",
            status="PENDING",
            score=0,
        )
    )

    assessments = repository.list_assessments()

    assert len(assessments) == 2

    db.close()


def test_delete_assessment():
    db = make_session()

    repository = ComplianceRepository(db)

    assessment = repository.create_assessment(
        ComplianceAssessment(
            name="Delete Me",
            status="PENDING",
            score=0,
        )
    )

    repository.delete_assessment(
        assessment
    )

    assert repository.get_assessment(
        assessment.id
    ) is None

    db.close()