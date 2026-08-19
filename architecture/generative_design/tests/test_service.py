"""
IMAGINE
Generative Design Service Tests

Tests the transaction boundary and orchestration behavior of
GenerativeDesignService.generate().
"""

from __future__ import annotations

from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from architecture.generative_design.models import (
    DesignCandidateRecord,
    GenerativeDesignRun,
)
from architecture.generative_design.service import (
    GenerativeDesignGenerationError,
    GenerativeDesignService,
)


# ============================================================================
# Test Data
# ============================================================================


PROJECT_ID = UUID("11111111-1111-1111-1111-111111111111")
RUN_ID = UUID("22222222-2222-2222-2222-222222222222")


class FakeConstraintSet:
    """Minimal constraint object used by service tests."""

    def model_dump(self, mode: str = "json") -> dict:
        return {
            "site": {
                "area": 1000.0,
            },
            "zoning": {
                "max_site_coverage": 0.50,
            },
            "floor_planning": {
                "max_storeys": 3,
            },
        }


def make_candidate(
    name: str,
    score: float,
) -> dict:
    """
    Create a fake generated candidate.
    """

    return {
        "name": name,
        "geometry": {
            "footprint": {
                "width": 20.0,
                "depth": 25.0,
            }
        },
        "metrics": {
            "gross_floor_area": 1000.0,
            "site_coverage": 0.50,
        },
        "evaluation": {
            "compliance": 0.95,
        },
        "score": score,
    }


def make_session() -> MagicMock:
    """
    Create an AsyncSession-like mock.

    AsyncSession methods that are awaited are AsyncMock instances.
    """

    session = MagicMock()

    session.add = MagicMock()

    session.flush = AsyncMock()

    session.commit = AsyncMock()

    session.rollback = AsyncMock()

    session.refresh = AsyncMock()

    return session


def make_service() -> tuple[
    GenerativeDesignService,
    MagicMock,
]:
    """
    Create a service with a mocked async database session.
    """

    session = make_session()

    service = GenerativeDesignService(
        session
    )

    return service, session


# ============================================================================
# Successful Generation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_successfully_completes_run() -> None:
    """
    A successful generation should:

        create run
        generate candidates
        score candidates
        rank candidates
        persist candidates
        update candidate_count
        mark run completed
        commit exactly once
    """

    service, session = make_service()

    constraints = {
        "site": {
            "area": 1000.0,
        },
        "zoning": {
            "max_site_coverage": 0.50,
        },
    }

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.90,
        ),
        make_candidate(
            "Option B",
            0.80,
        ),
        make_candidate(
            "Option C",
            0.70,
        ),
    ]

    scored_candidates = [
        {
            **candidate,
            "evaluation": {
                "compliance": candidate["score"],
            },
        }
        for candidate in candidates
    ]

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=scored_candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=scored_candidates,
        ),
    ):
        run = await service.generate(
            project_id=PROJECT_ID,
            name="Residential Scheme",
            constraints=constraints,
            candidate_count=3,
            created_by="test-user",
        )

    assert isinstance(
        run,
        GenerativeDesignRun,
    )

    assert run.project_id == PROJECT_ID

    assert isinstance(
        run.project_id,
        UUID,
    )

    assert run.name == "Residential Scheme"

    assert run.status == "completed"

    assert run.candidate_count == 3

    assert run.completed_at is not None

    assert run.error_message is None

    assert session.commit.await_count == 1

    assert session.rollback.await_count == 0


# ============================================================================
# UUID Handling
# ============================================================================


@pytest.mark.asyncio
async def test_generate_preserves_uuid_project_identifier() -> None:
    """
    The service must pass UUID identifiers directly to the
    GenerativeDesignRun model.
    """

    service, session = make_service()

    project_id = uuid4()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.91,
        )
    ]

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            return_value=candidates[0],
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        run = await service.generate(
            project_id=project_id,
            name="UUID Test",
            constraints={},
            candidate_count=1,
        )

    assert run.project_id == project_id

    assert isinstance(
        run.project_id,
        UUID,
    )

    assert run.project_id.version == 4


@pytest.mark.asyncio
async def test_generate_creates_uuid_run_identifier() -> None:
    """
    BaseModel's UUID primary key should be available after flush.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        )
    ]

    def assign_run_id() -> None:
        """
        Simulate SQLAlchemy assigning the UUID during flush.
        """

        for call in session.add.call_args_list:
            entity = call.args[0]

            if isinstance(
                entity,
                GenerativeDesignRun,
            ):
                entity.id = RUN_ID

    session.flush.side_effect = assign_run_id

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            return_value=candidates[0],
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        run = await service.generate(
            project_id=PROJECT_ID,
            name="Run UUID Test",
            constraints={},
            candidate_count=1,
        )

    assert run.id == RUN_ID

    assert isinstance(
        run.id,
        UUID,
    )


# ============================================================================
# Candidate Count
# ============================================================================


@pytest.mark.asyncio
async def test_generate_updates_candidate_count() -> None:
    """
    candidate_count must equal the number of candidates actually
    persisted by the generation run.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate("Option A", 0.95),
        make_candidate("Option B", 0.90),
        make_candidate("Option C", 0.85),
        make_candidate("Option D", 0.80),
        make_candidate("Option E", 0.75),
    ]

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        run = await service.generate(
            project_id=PROJECT_ID,
            name="Candidate Count Test",
            constraints={},
            candidate_count=5,
        )

    assert run.candidate_count == 5


# ============================================================================
# Single Commit Boundary
# ============================================================================


@pytest.mark.asyncio
async def test_generate_commits_exactly_once() -> None:
    """
    generate() must have exactly one commit.

    This protects the service-owned transaction boundary.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate("Option A", 0.95),
        make_candidate("Option B", 0.90),
    ]

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        await service.generate(
            project_id=PROJECT_ID,
            name="Single Commit Test",
            constraints={},
            candidate_count=2,
        )

    assert session.commit.await_count == 1

    assert session.rollback.await_count == 0


@pytest.mark.asyncio
async def test_generate_does_not_commit_before_candidates_are_persisted() -> None:
    """
    The commit must happen only after the candidates and final run
    state have been flushed.

    This test records the order of transaction operations.
    """

    service, session = make_service()

    events: list[str] = []

    async def flush() -> None:
        events.append("flush")

    async def commit() -> None:
        events.append("commit")

    async def rollback() -> None:
        events.append("rollback")

    session.flush.side_effect = flush
    session.commit.side_effect = commit
    session.rollback.side_effect = rollback

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate("Option A", 0.95),
        make_candidate("Option B", 0.90),
    ]

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        await service.generate(
            project_id=PROJECT_ID,
            name="Transaction Order Test",
            constraints={},
            candidate_count=2,
        )

    assert events[-1] == "commit"

    assert events.count("commit") == 1

    assert events.count("rollback") == 0

    assert events.index("commit") > 0


# ============================================================================
# Generation Failure
# ============================================================================


@pytest.mark.asyncio
async def test_generate_rolls_back_when_generation_fails() -> None:
    """
    If candidate generation raises an exception, the complete
    transaction must be rolled back.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    generation_error = RuntimeError(
        "Generator failed."
    )

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            side_effect=generation_error,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError,
            match="generation failed",
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Generation Failure",
                constraints={},
                candidate_count=5,
            )

    assert session.rollback.await_count == 1

    assert session.commit.await_count == 0


@pytest.mark.asyncio
async def test_generate_rolls_back_when_generator_returns_no_candidates() -> None:
    """
    An empty candidate population is treated as a generation failure.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=[],
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Empty Generation",
                constraints={},
                candidate_count=10,
            )

    assert session.rollback.await_count == 1

    assert session.commit.await_count == 0


# ============================================================================
# Scoring Failure
# ============================================================================


@pytest.mark.asyncio
async def test_generate_rolls_back_when_scoring_fails() -> None:
    """
    If scoring fails after generation, nothing should be committed.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        ),
        make_candidate(
            "Option B",
            0.90,
        ),
    ]

    scoring_error = RuntimeError(
        "Scoring engine failed."
    )

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=scoring_error,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError,
            match="generation failed",
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Scoring Failure",
                constraints={},
                candidate_count=2,
            )

    assert session.rollback.await_count == 1

    assert session.commit.await_count == 0


# ============================================================================
# Persistence Failure
# ============================================================================


@pytest.mark.asyncio
async def test_generate_rolls_back_when_persistence_fails() -> None:
    """
    If the database flush fails while candidates are being persisted,
    the complete generation transaction must roll back.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        ),
        make_candidate(
            "Option B",
            0.90,
        ),
    ]

    flush_count = 0

    async def failing_flush() -> None:
        nonlocal flush_count

        flush_count += 1

        # First flush creates the run.
        if flush_count == 1:
            return

        # Second flush attempts to persist candidates.
        raise RuntimeError(
            "Database persistence failed."
        )

    session.flush.side_effect = failing_flush

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError,
            match="generation failed",
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Persistence Failure",
                constraints={},
                candidate_count=2,
            )

    assert flush_count == 2

    assert session.rollback.await_count == 1

    assert session.commit.await_count == 0


@pytest.mark.asyncio
async def test_generate_rolls_back_when_final_flush_fails() -> None:
    """
    If persistence fails while finalizing the completed run,
    the transaction must still roll back.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        )
    ]

    flush_count = 0

    async def failing_final_flush() -> None:
        nonlocal flush_count

        flush_count += 1

        # Run creation succeeds.
        # Candidate persistence succeeds.
        # Final run update fails.
        if flush_count >= 3:
            raise RuntimeError(
                "Final run update failed."
            )

    session.flush.side_effect = failing_final_flush

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError,
            match="generation failed",
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Final Flush Failure",
                constraints={},
                candidate_count=1,
            )

    assert session.rollback.await_count == 1

    assert session.commit.await_count == 0


# ============================================================================
# Commit Failure
# ============================================================================


@pytest.mark.asyncio
async def test_generate_rolls_back_when_commit_fails() -> None:
    """
    If the actual commit fails, rollback must be attempted.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        )
    ]

    session.commit.side_effect = RuntimeError(
        "Database commit failed."
    )

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError,
            match="generation failed",
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Commit Failure",
                constraints={},
                candidate_count=1,
            )

    assert session.commit.await_count == 1

    assert session.rollback.await_count == 1


# ============================================================================
# Validation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_rejects_zero_candidate_count() -> None:
    """
    candidate_count=0 must fail before opening a transaction.
    """

    service, session = make_service()

    with pytest.raises(
        ValueError,
        match="candidate_count must be greater than zero",
    ):
        await service.generate(
            project_id=PROJECT_ID,
            name="Invalid Count",
            constraints={},
            candidate_count=0,
        )

    session.add.assert_not_called()

    assert session.flush.await_count == 0

    assert session.commit.await_count == 0

    assert session.rollback.await_count == 0


@pytest.mark.asyncio
async def test_generate_rejects_negative_candidate_count() -> None:
    """
    Negative candidate counts must be rejected.
    """

    service, session = make_service()

    with pytest.raises(
        ValueError,
        match="candidate_count must be greater than zero",
    ):
        await service.generate(
            project_id=PROJECT_ID,
            name="Invalid Negative Count",
            constraints={},
            candidate_count=-1,
        )

    session.add.assert_not_called()

    assert session.commit.await_count == 0


# ============================================================================
# Candidate Persistence
# ============================================================================


@pytest.mark.asyncio
async def test_generate_persists_candidates_with_run_uuid() -> None:
    """
    Every generated candidate must reference the generated run's UUID.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        ),
        make_candidate(
            "Option B",
            0.90,
        ),
    ]

    def assign_run_uuid() -> None:
        """
        Simulate database/SQLAlchemy assignment of run UUID.
        """

        for call in session.add.call_args_list:
            entity = call.args[0]

            if isinstance(
                entity,
                GenerativeDesignRun,
            ):
                entity.id = RUN_ID

    session.flush.side_effect = assign_run_uuid

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        run = await service.generate(
            project_id=PROJECT_ID,
            name="Candidate UUID Test",
            constraints={},
            candidate_count=2,
        )

    assert run.id == RUN_ID

    added_entities = [
        call.args[0]
        for call in session.add.call_args_list
    ]

    persisted_candidates = [
        entity
        for entity in added_entities
        if isinstance(
            entity,
            DesignCandidateRecord,
        )
    ]

    assert len(persisted_candidates) == 2

    for candidate in persisted_candidates:
        assert candidate.run_id == RUN_ID

        assert isinstance(
            candidate.run_id,
            UUID,
        )


# ============================================================================
# Run State
# ============================================================================


@pytest.mark.asyncio
async def test_generate_marks_run_completed_only_after_candidates_are_added() -> None:
    """
    The run should remain in the running state until candidates
    have been added and the final flush occurs.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        )
    ]

    observed_statuses: list[str] = []

    original_add = session.add

    def capture_add(entity: object) -> None:
        if isinstance(
            entity,
            GenerativeDesignRun,
        ):
            observed_statuses.append(
                entity.status
            )

        original_add(entity)

    session.add.side_effect = capture_add

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=candidates,
        ),
        patch(
            "architecture.generative_design.service.rank_designs",
            return_value=candidates,
        ),
    ):
        run = await service.generate(
            project_id=PROJECT_ID,
            name="Completion State Test",
            constraints={},
            candidate_count=1,
        )

    assert observed_statuses == [
        "running"
    ]

    assert run.status == "completed"

    assert run.candidate_count == 1

    assert run.completed_at is not None


# ============================================================================
# No Partial Commit
# ============================================================================


@pytest.mark.asyncio
async def test_failed_generation_never_commits_partial_candidates() -> None:
    """
    A scoring failure after multiple candidates have been generated
    must never result in a commit.

    This is the key atomicity guarantee of the service.
    """

    service, session = make_service()

    fake_constraints = FakeConstraintSet()

    candidates = [
        make_candidate(
            "Option A",
            0.95,
        ),
        make_candidate(
            "Option B",
            0.90,
        ),
        make_candidate(
            "Option C",
            0.85,
        ),
    ]

    scoring_calls = 0

    def failing_score(
        *,
        candidate: object,
        constraints: object,
    ) -> dict[str, Any]:
        nonlocal scoring_calls

        scoring_calls += 1

        if scoring_calls == 2:
            raise RuntimeError(
                "Scoring failed on second candidate."
            )

        return candidate

    with (
        patch(
            "architecture.generative_design.service.build_constraints",
            return_value=fake_constraints,
        ),
        patch(
            "architecture.generative_design.service.generate_designs",
            return_value=candidates,
        ),
        patch(
            "architecture.generative_design.service.score_design",
            side_effect=failing_score,
        ),
    ):
        with pytest.raises(
            GenerativeDesignGenerationError
        ):
            await service.generate(
                project_id=PROJECT_ID,
                name="Atomicity Test",
                constraints={},
                candidate_count=3,
            )

    assert scoring_calls == 2

    assert session.commit.await_count == 0

    assert session.rollback.await_count == 1
