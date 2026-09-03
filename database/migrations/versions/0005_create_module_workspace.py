"""create shared enterprise module workspace table

Revision ID: 0005_create_module_workspace
Revises: 0004_create_structural_tables
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_create_module_workspace"
down_revision = "0004_create_structural_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "module_workspace_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("module_route", sa.String(length=150), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("module_workspace_records")
