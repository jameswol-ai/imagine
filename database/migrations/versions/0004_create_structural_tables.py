"""create structural tables

Revision ID: 0004_create_structural_tables
Revises: 0003_create_architecture_tables
Create Date: 2026-08-19 01:21:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_create_structural_tables'
down_revision = '0003_create_architecture_tables'
branch_labels = None
depends_on = None

def upgrade():
    # beam_designs
    op.create_table(
        'beam_designs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('material', sa.String(length=100), nullable=False),
        sa.Column('span_length', sa.Float(), nullable=False),
        sa.Column('load_capacity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # column_designs
    op.create_table(
        'column_designs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('material', sa.String(length=100), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('load_capacity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # slab_designs
    op.create_table(
        'slab_designs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('material', sa.String(length=100), nullable=False),
        sa.Column('thickness', sa.Float(), nullable=False),
        sa.Column('area', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # foundation_designs
    op.create_table(
        'foundation_designs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('depth', sa.Float(), nullable=True),
        sa.Column('capacity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # retaining_walls
    op.create_table(
        'retaining_walls',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('height', sa.Float(), nullable=False),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.Column('stability_factor', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # steel_connections
    op.create_table(
        'steel_connections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('connection_type', sa.String(length=100), nullable=False),
        sa.Column('bolt_count', sa.Integer(), nullable=True),
        sa.Column('weld_length', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # fea_models
    op.create_table(
        'fea_models',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('mesh_size', sa.Float(), nullable=True),
        sa.Column('solver', sa.String(length=100), nullable=False),
        sa.Column('results_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('fea_models')
    op.drop_table('steel_connections')
    op.drop_table('retaining_walls')
    op.drop_table('foundation_designs')
    op.drop_table('slab_designs')
    op.drop_table('column_designs')
    op.drop_table('beam_designs')