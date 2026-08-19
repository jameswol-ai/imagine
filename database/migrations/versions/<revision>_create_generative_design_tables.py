"""
Create generative design tables.

Revision ID: 7f3a2c91b6d4
Revises: <PREVIOUS_REVISION_ID>
Create Date: 2026-08-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------

revision: str = "7f3a2c91b6d4"
down_revision: Union[str, Sequence[str], None] = "<PREVIOUS_REVISION_ID>"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    """
    Create generative design runs and generated candidate tables.
    """

    # -----------------------------------------------------------------------
    # generative_design_runs
    # -----------------------------------------------------------------------

    op.create_table(
        "generative_design_runs",

        # BaseModel fields
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "created_by",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),

        # Project relationship
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        # Generative design fields
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),

        sa.Column(
            "constraints",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        sa.Column(
            "candidate_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        # Primary key
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_generative_design_runs",
        ),

        # Project foreign key
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_generative_design_runs_project_id",
            ondelete="CASCADE",
        ),
    )

    # -----------------------------------------------------------------------
    # Indexes for generative_design_runs
    # -----------------------------------------------------------------------

    op.create_index(
        "ix_generative_design_runs_project_id",
        "generative_design_runs",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        "ix_generative_design_runs_status",
        "generative_design_runs",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_generative_design_runs_created_at",
        "generative_design_runs",
        ["created_at"],
        unique=False,
    )

    # -----------------------------------------------------------------------
    # generative_design_candidates
    # -----------------------------------------------------------------------

    op.create_table(
        "generative_design_candidates",

        # BaseModel fields
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "created_by",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),

        # Parent generative-design run
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        # Candidate fields
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'generated'"),
        ),

        sa.Column(
            "rank",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "score",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),

        sa.Column(
            "geometry",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        sa.Column(
            "metrics",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        sa.Column(
            "evaluation",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),

        # Primary key
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_generative_design_candidates",
        ),

        # Parent run foreign key
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["generative_design_runs.id"],
            name="fk_generative_design_candidates_run_id",
            ondelete="CASCADE",
        ),
    )

    # -----------------------------------------------------------------------
    # Indexes for generative_design_candidates
    # -----------------------------------------------------------------------

    op.create_index(
        "ix_generative_design_candidates_run_id",
        "generative_design_candidates",
        ["run_id"],
        unique=False,
    )

    op.create_index(
        "ix_generative_design_candidates_rank",
        "generative_design_candidates",
        ["rank"],
        unique=False,
    )

    op.create_index(
        "ix_generative_design_candidates_status",
        "generative_design_candidates",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_generative_design_candidates_score",
        "generative_design_candidates",
        ["score"],
        unique=False,
    )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    """
    Remove generative design tables and indexes.
    """

    # Drop child indexes first.
    op.drop_index(
        "ix_generative_design_candidates_score",
        table_name="generative_design_candidates",
    )

    op.drop_index(
        "ix_generative_design_candidates_status",
        table_name="generative_design_candidates",
    )

    op.drop_index(
        "ix_generative_design_candidates_rank",
        table_name="generative_design_candidates",
    )

    op.drop_index(
        "ix_generative_design_candidates_run_id",
        table_name="generative_design_candidates",
    )

    # Drop child table before parent because of FK dependency.
    op.drop_table(
        "generative_design_candidates"
    )

    # Drop parent indexes.
    op.drop_index(
        "ix_generative_design_runs_created_at",
        table_name="generative_design_runs",
    )

    op.drop_index(
        "ix_generative_design_runs_status",
        table_name="generative_design_runs",
    )

    op.drop_index(
        "ix_generative_design_runs_project_id",
        table_name="generative_design_runs",
    )

    # Drop parent table.
    op.drop_table(
        "generative_design_runs"
  )
