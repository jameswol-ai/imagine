import streamlit as st
import pandas as pd
from pdf_generator import generate_passport_pdf

# Initialize standard SQL connection
conn = st.connection("postgresql", type="sql")

def fetch_passport_data(project_id: str) -> dict:
    """Queries project, structural, and MEP details, returning a formatted dict."""
    query = """
        SELECT 
            p.id AS project_id,
            p.name AS project_name,
            p.location,
            p.status,
            TO_CHAR(p.created_at, 'YYYY-MM-DD') AS date,
            s.foundation_type,
            s.load_capacity,
            s.framing_material,
            s.seismic_compliance,
            m.hvac_spec,
            m.electrical_capacity,
            m.plumbing_spec,
            m.fire_protection
        FROM projects p
        LEFT JOIN structural_passports s ON p.id = s.project_id
        LEFT JOIN mep_passports m ON p.id = m.project_id
        WHERE p.id = :project_id;
    """
    
    # Query database and return pandas DataFrame
    df = conn.query(query, params={"project_id": project_id}, ttl="5m")
    
    if df.empty:
        return None
    
    # Convert first row to dictionary (matches required keys in generate_passport_pdf)
    return df.iloc[0].to_dict()

# --- Streamlit UI ---
st.title("MEP & Structural Passport Generator")

# 1. Fetch available projects for dropdown selector
try:
    project_list_df = conn.query("SELECT id, name FROM projects ORDER BY name ASC;", ttl="10m")
    
    if not project_list_df.empty:
        project_map = {f"{row['name']} ({row['id']})": row['id'] for _, row in project_list_df.iterrows()}
        selected_project_label = st.selectbox("Select Project", list(project_map.keys()))
        selected_project_id = project_map[selected_project_label]

        # 2. Fetch selected data and generate PDF buffer
        passport_data = fetch_passport_data(selected_project_id)

        if passport_data:
            pdf_bytes = generate_passport_pdf(passport_data)

            # 3. Download Button
            st.download_button(
                label="📄 Download Passport Report (PDF)",
                data=pdf_bytes,
                file_name=f"{passport_data['project_id']}_Passport.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("No structural/MEP record found for the selected project.")
    else:
        st.info("No projects found in database.")

except Exception as e:
    st.error(f"Database connection error: {e}")
