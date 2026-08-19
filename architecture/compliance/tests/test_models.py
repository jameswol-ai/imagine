from architecture.compliance.models import (
    ComplianceAssessment,
    ComplianceResult,
)


def test_assessment_model_metadata():
    assert ComplianceAssessment.__tablename__ == "compliance_assessments"


def test_result_model_metadata():
    assert ComplianceResult.__tablename__ == "compliance_results"


def test_assessment_relationship_exists():
    assert hasattr(
        ComplianceAssessment,
        "rules",
    )


def test_result_relationship_exists():
    assert hasattr(
        ComplianceResult,
        "assessment",
    )