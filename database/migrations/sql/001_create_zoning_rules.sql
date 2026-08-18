-- IMAGINE Architecture / Zoning
-- Apply after the projects table exists.
-- This migration is intentionally plain SQL because the repository currently
-- contains only an alembic.ini placeholder and no migration environment.

CREATE TYPE zoning_use AS ENUM (
    'residential',
    'commercial',
    'mixed_use',
    'industrial',
    'institutional',
    'agricultural',
    'special'
);

CREATE TYPE zoning_status AS ENUM (
    'active',
    'draft',
    'archived'
);

CREATE TABLE zoning_rules (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    created_by VARCHAR NULL,
    updated_by VARCHAR NULL,

    project_id UUID NULL REFERENCES projects(id) ON DELETE CASCADE,

    code VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,

    allowed_use zoning_use NOT NULL,
    status zoning_status NOT NULL DEFAULT 'active',

    max_height_m DOUBLE PRECISION NOT NULL DEFAULT 0,
    site_coverage_pct DOUBLE PRECISION NOT NULL DEFAULT 0,
    setback_m DOUBLE PRECISION NOT NULL DEFAULT 0,
    far DOUBLE PRECISION NOT NULL DEFAULT 0,

    CONSTRAINT uq_zoning_rules_project_code
        UNIQUE (project_id, code),

    CONSTRAINT ck_zoning_max_height_nonnegative
        CHECK (max_height_m >= 0),

    CONSTRAINT ck_zoning_coverage_range
        CHECK (site_coverage_pct >= 0 AND site_coverage_pct <= 100),

    CONSTRAINT ck_zoning_setback_nonnegative
        CHECK (setback_m >= 0),

    CONSTRAINT ck_zoning_far_nonnegative
        CHECK (far >= 0)
);

CREATE INDEX ix_zoning_rules_project_id
    ON zoning_rules(project_id);

CREATE INDEX ix_zoning_rules_code
    ON zoning_rules(code);

CREATE INDEX ix_zoning_rules_status
    ON zoning_rules(status);
