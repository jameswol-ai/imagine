"""create architecture tables

Revision ID: 0003_create_architecture_tables
Revises: 0002_create_core_tables
Create Date: 2026-08-19 01:15:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_create_architecture_tables'
down_revision = '0002_create_core_tables'
branch_labels = None
depends_on = None

def upgrade():
    # generative_designs
    op.create_table(
        'generative_designs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('algorithm', sa.String(length=255), nullable=False),
        sa.Column('parameters', sa.Text(), nullable=True),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # zoning_rules
    op.create_table(
        'zoning_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('zone_type', sa.String(length=100), nullable=False),
        sa.Column('restrictions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # site_plans
    op.create_table(
        'site_plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('layout', sa.Text(), nullable=True),
        sa.Column('constraints', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # floor_plans
    op.create_table(
        'floor_plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('layout_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # room_programs
    op.create_table(
        'room_programs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('room_name', sa.String(length=100), nullable=False),
        sa.Column('area', sa.Integer(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # compliance_checks
    op.create_table(
        'compliance_checks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('rule', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), default='pending', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('compliance_checks')
    op.drop_table('room_programs')
    op.drop_table('floor_plans')
    op.drop_table('site_plans')
    op.drop_table('zoning_rules')
    op.drop_table('generative_designs')