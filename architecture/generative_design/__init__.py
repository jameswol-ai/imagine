"""
IMAGINE
Generative Design Engine

Provides constraint-driven architectural design generation,
evaluation, scoring, ranking, persistence, and API integration.
"""

from .constraints import (
    ConstraintValidationResult,
    DesignConstraints,
    validate_constraints,
)
from .generator import (
    DesignCandidate,
    generate_candidates,
)
from .scoring import (
    DesignScore,
    score_candidate,
)
from .service import GenerativeDesignService

__all__ = [
    "ConstraintValidationResult",
    "DesignCandidate",
    "DesignConstraints",
    "DesignScore",
    "GenerativeDesignService",
    "generate_candidates",
    "score_candidate",
    "validate_constraints",
]

__version__ = "0.1.0"
