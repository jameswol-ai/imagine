import streamlit as st
import pandas as pd
from pdf_generator import generate_passport_pdf
from auth import check_permission, EXPORT_ALLOWED_ROLES

conn = st.connection("postgresql", type="sql")

# --- Mock Login / Session Setup (Replace with your login handler) ---
if "user" not in st.session_state:
    st.sidebar.title("🔐 Authentication")
    role_choice = st.sidebar.selectbox("Simulate Login Role", ["Admin", "Project Manager", "Junior Inspector", "Viewer"])
    st.session_state["user"] = {
        "username": "jdoe",
        "role": role_choice
    }

user = st.session_state["user"]
st.sidebar.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# --- Main App Interface ---
st.title("MEP & Structural Passport Generator")

# 1. Fetch available projects (visible to all logged-in users)
try:
    project_list_df = conn.query("SELECT id, name FROM projects ORDER BY name ASC;", ttl="10m")
    
    if not project_list_df.empty:
        project_map = {f"{row['name']} ({row['id']})": row['id'] for _, row in project_list_df.iterrows()}
        selected_project_label = st.selectbox("Select Project", list(project_map.keys()))
        selected_project_id = project_map[selected_project_label]

        # 2. Check RBAC permissions for PDF Download
        can_export = check_permission(EXPORT_ALLOWED_ROLES)

        if can_export:
            # Query full data & render download button ONLY if authorized
            passport_data = fetch_passport_data(selected_project_id) # defined in earlier step

            if passport_data:
                pdf_bytes = generate_passport_pdf(passport_data)

                st.download_button(
                    label="📄 Download Passport Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{passport_data['project_id']}_Passport.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("No structural/MEP record found for this project.")
        else:
            # Render a lock state for unauthorized roles
            st.error("⛔ Access Restricted: Your role does not have permission to export PDF Passports.")
            st.info(f"Required roles: {', '.join(EXPORT_ALLOWED_ROLES)}")

    else:
        st.info("No projects found in database.")

except Exception as e:
    st.error(f"Database connection error: {e}")
