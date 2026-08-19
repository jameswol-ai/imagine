CREATE TABLE IF NOT EXISTS site_plans (
id UUID PRIMARY KEY, project_id UUID NULL REFERENCES projects(id) ON DELETE SET NULL,
name VARCHAR(200) NOT NULL, site_code VARCHAR(100) NOT NULL UNIQUE, description TEXT,
status VARCHAR(30) NOT NULL DEFAULT 'Draft', site_area_m2 NUMERIC(14,2) NOT NULL CHECK(site_area_m2>0),
building_footprint_m2 NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK(building_footprint_m2>=0),
road_area_m2 NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK(road_area_m2>=0),
parking_area_m2 NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK(parking_area_m2>=0),
landscape_area_m2 NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK(landscape_area_m2>=0),
north_orientation_deg NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK(north_orientation_deg>=0 AND north_orientation_deg<360),
slope_percent NUMERIC(6,2) NOT NULL DEFAULT 0 CHECK(slope_percent>=0 AND slope_percent<=100),
soil_type VARCHAR(80), drainage_strategy VARCHAR(200), access_strategy VARCHAR(200),
active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS ix_site_plans_project_id ON site_plans(project_id);
CREATE INDEX IF NOT EXISTS ix_site_plans_status ON site_plans(status);
