"""
IMAGINE Session State Initialization & Mock Seed Data
Path: modules/utils/mock_data.py
App: imagine
"""

import streamlit as st


def init_mock_data():
    """Seeds default session state records across AEC domain modules."""
    if "projects" not in st.session_state:
        st.session_state.projects = [
            {
                "id": "PRJ-001",
                "name": "Skyline Tower",
                "client": "Apex Developments",
                "category": "Commercial",
                "budget": 45.0,
                "budget_eur": 45000000.0,
                "status": "active",
                "progress_pct": 65.0,
                "location": "Central District",
            },
            {
                "id": "PRJ-002",
                "name": "Harbor Bridge Expansion",
                "client": "Dept. of Transportation",
                "category": "Infrastructure",
                "budget": 120.0,
                "budget_eur": 120000000.0,
                "status": "active",
                "progress_pct": 35.0,
                "location": "East Port",
            },
        ]

    if "structural_calcs" not in st.session_state:
        st.session_state.structural_calcs = [
            {
                "id": "CALC-EN-101",
                "project_id": "PRJ-001",
                "code": "EN 1993-1-1",
                "element_name": "Main Transfer Girder G1",
                "unity_check": 0.84,
                "status": "Passed",
                "updated_at": "2026-08-25 14:30",
            },
            {
                "id": "CALC-EN-102",
                "project_id": "PRJ-001",
                "code": "EN 1992-1-1",
                "element_name": "Core Wall C3 Edge Column",
                "unity_check": 0.93,
                "status": "Warning",
                "updated_at": "2026-08-26 09:15",
            },
        ]
