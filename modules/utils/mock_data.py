"""
Centralized Mock Data Initializer for imagine
Path: Modules/utils/mock_data.py
App: imagine
"""

from datetime import datetime, timezone
import streamlit as st


def get_default_mock_data() -> dict:
    """Returns baseline AEC mock data records across all domains."""
    return {
        "projects": [
            {
                "id": "PRJ-001",
                "name": "Apex Commercial Tower",
                "location": "Frankfurt, Germany",
                "typology": "Commercial High-Rise",
                "budget_eur": 45000000.0,
                "status": "In Design",
                "progress_pct": 35.0,
                "created_at": "2026-01-15T08:30:00Z",
            },
            {
                "id": "PRJ-002",
                "name": "Riverside Eco-Residences",
                "location": "Lyon, France",
                "typology": "Residential Mixed-Use",
                "budget_eur": 18500000.0,
                "status": "Construction",
                "progress_pct": 62.0,
                "created_at": "2026-03-01T10:15:00Z",
            },
        ],
        "buildings": [
            {
                "id": "BLD-101",
                "project_id": "PRJ-001",
                "name": "Tower Block A",
                "storeys_above_ground": 24,
                "storeys_below_ground": 3,
                "gross_floor_area_m2": 32000.0,
                "structure_type": "Composite Steel-Concrete",
            },
            {
                "id": "BLD-102",
                "project_id": "PRJ-002",
                "name": "Residences West",
                "storeys_above_ground": 8,
                "storeys_below_ground": 1,
                "gross_floor_area_m2": 11500.0,
                "structure_type": "Glulam Timber Framing",
            },
        ],
        "structural_calcs": [
            {
                "id": "CALC-001",
                "project_id": "PRJ-001",
                "code": "EN 1992",
                "element_name": "Beam B-201 (Transfer Beam)",
                "status": "Passed",
                "unity_check": 0.84,
                "updated_at": "2026-08-20T14:22:00Z",
            },
            {
                "id": "CALC-002",
                "project_id": "PRJ-001",
                "code": "EN 1993",
                "element_name": "Column C-104 (HEB 300)",
                "status": "Warning",
                "unity_check": 0.96,
                "updated_at": "2026-08-24T11:05:00Z",
            },
        ],
        "boq_items": [
            {
                "id": "BOQ-501",
                "project_id": "PRJ-001",
                "code": "03-30-00",
                "description": "Cast-in-Place Concrete C30/37 (Columns)",
                "quantity": 2450.0,
                "unit": "m³",
                "unit_rate_eur": 195.0,
            },
            {
                "id": "BOQ-502",
                "project_id": "PRJ-001",
                "code": "05-12-00",
                "description": "Structural Steel S355 (Beams & Columns)",
                "quantity": 680.0,
                "unit": "tonnes",
                "unit_rate_eur": 2450.0,
            },
        ],
        "rfis": [
            {
                "id": "RFI-101",
                "project_id": "PRJ-001",
                "title": "Rebar clearance at transfer beam B-201",
                "assigned_to": "Structural Lead",
                "priority": "High",
                "status": "Open",
                "date_raised": "2026-08-22",
            }
        ],
        "digital_twin_sensors": [
            {
                "id": "SNS-901",
                "project_id": "PRJ-001",
                "type": "Strain Gauge",
                "location": "Beam B-201 Midspan",
                "value": 142.5,
                "unit": "µε",
                "status": "Nominal",
            }
        ],
    }


def init_mock_data(force_reset: bool = False) -> None:
    """Populates st.session_state with initial domain collections if uninitialized."""
    default_data = get_default_mock_data()

    for key, data_list in default_data.items():
        if force_reset or key not in st.session_state:
            st.session_state[key] = data_list

    if "session_initialized_at" not in st.session_state or force_reset:
        st.session_state.session_initialized_at = datetime.now(timezone.utc).isoformat()
