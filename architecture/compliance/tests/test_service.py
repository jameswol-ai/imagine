from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.connection import Base

from architecture.compliance.schemas import (
    ComplianceAssessmentCreate,
    ComplianceCheckInput,
)
from architecture.compliance.service import (
    ComplianceService,
)


def make_service():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    db = Session(engine)

    return ComplianceService(db), db


def test_site_coverage():
    service, db = make_service()

    coverage = service.calculate_site_coverage(
        5000,
        2500,
    )

    assert coverage == 50

    db.close()


def test_far():
    service, db = make_service()

    far = service.calculate_far(
        5000,
        10000,
    )

    assert far == 2

    db.close()


def test_compliance_pass():
    service, db = make_service()

    result = service.evaluate(
        ComplianceCheckInput(
            site_area_m2=5000,
            building_footprint_m2=2500,
            gross_floor_area_m2=8000,
            building_height_m=25,
            front_setback_m=6,
            side_setback_m=4,
            rear_setback_m=4,
            max_height_m=30,
            max_coverage_percent=60,
            max_far=2,
            min_front_setback_m=5,
            min_side_setback_m=3,
            min_rear_setback_m=3,
        )
    )

    assert result.status == "PASS"
    assert result.failed == 0
    assert result.score == 100

    db.close()


def test_compliance_failure():
    service, db = make_service()

    result = service.evaluate(
        ComplianceCheckInput(
            site_area_m2=5000,
            building_footprint_m2=3500,
            gross_floor_area_m2=15000,
            building_height_m=40,
            front_setback_m=2,
            side_setback_m=1,
            rear_setback_m=1,
            max_height_m=30,
            max_coverage_percent=60,
            max_far=2,
            min_front_setback_m=5,
            min_side_setback_m=3,
            min_rear_setback_m=3,
        )
    )

    assert result.status == "FAIL"
    assert result.failed > 0

    db.close()


def test_create_assessment():
    service, db = make_service()

    assessment = service.create_assessment(
        ComplianceAssessmentCreate(
            name="Green Tower Compliance",
        )
    )

    assert assessment.id is not None
    assert assessment.name == "Green Tower Compliance"

    db.close()


def test_run_and_save():
    service, db = make_service()

    assessment = service.create_assessment(
        ComplianceAssessmentCreate(
            name="Saved Assessment",
        )
    )

    result = service.run_and_save(
        assessment.id,
        ComplianceCheckInput(
            site_area_m2=5000,
            building_footprint_m2=2500,
            gross_floor_area_m2=8000,
            building_height_m=25,
            front_setback_m=6,
            side_setback_m=4,
            rear_setback_m=4,
            max_height_m=30,
            max_coverage_percent=60,
            max_far=2,
            min_front_setback_m=5,
            min_side_setback_m=3,
            min_rear_setback_m=3,
        ),
    )

    assert result.status == "PASS"

    saved = service.get_assessment(
        assessment.id
    )

    assert saved is not None
    assert saved.status == "PASS"
    assert saved.score == 100
    assert len(saved.rules) == 6

    db.close()