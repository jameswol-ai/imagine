# create_modules.py
import os

MODULES = {
    "dashboard": ["dashboard.py"],
    "projects": ["project_page.py"],
    "architecture": ["synthesis.py"],
    "bim": ["buildings.py", "storeys.py", "spaces.py", "ifc_export.py"],
    "structural": ["eurocode.py", "beam_design.py", "column_design.py", "slab_design.py", "foundation_design.py", "retaining_walls.py"],
    "mep": ["analysis.py", "hvac.py", "electrical.py", "plumbing.py", "energy_simulation.py"],
    "costing": ["boq.py", "procurement.py", "forex.py", "escalation.py", "risk_analysis.py"],
    "governance": ["approvals.py"],
    "construction": ["rfis.py", "submittals.py", "site_diary.py", "progress_tracking.py", "snagging.py"],
    "documents": ["documents.py", "revisions.py", "drawing_register.py", "specifications.py", "transmittals.py"],
    "analytics": ["portfolio.py", "reporting.py", "forecasting.py", "kpis.py"],
    "digital_twin": ["assets.py", "sensors.py", "telemetry.py", "maintenance.py", "predictive_ai.py"],
    "ai": ["architect.py", "engineer.py", "mep.py", "qs.py", "project_manager.py"],
}

TEMPLATE = '''import streamlit as st

def render():
    st.info("📦 This module is under development. Coming soon.")
'''

def create_modules():
    for folder, files in MODULES.items():
        os.makedirs(f"modules/{folder}", exist_ok=True)
        with open(f"modules/{folder}/__init__.py", "w") as f:
            f.write("")
        for file in files:
            with open(f"modules/{folder}/{file}", "w") as f:
                f.write(TEMPLATE)
    print("✅ All module files created.")

if __name__ == "__main__":
    create_modules()