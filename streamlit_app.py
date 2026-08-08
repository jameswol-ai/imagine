import io
import bcrypt
import pandas as pd
import streamlit as st
from sqlalchemy import text
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# --- Page Setup ---
st.set_page_config(
    page_title="Creative Studios - Passport Portal",
    page_icon="🏗️",
    layout="wide"
)

# Initialize PostgreSQL connection via Streamlit Secrets / Environment
conn = st.connection("postgresql", type="sql")

# Allowed export roles for PDF export
EXPORT_ALLOWED_ROLES = {"Admin", "Project Manager", "Lead Engineer"}

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None


# ==========================================
# 1. PDF GENERATOR MODULE
# ==========================================
def make_cell(text_val, style):
    """Wraps cell content in a ReportLab Paragraph for auto-wrapping."""
    val_str = str(text_val) if text_val is not None and not pd.isna(text_val) else "N/A"
    return Paragraph(val_str, style)

def generate_passport_pdf(project_data: dict) -> bytes:
    """Generates an architectural passport PDF with full cell text wrapping."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'], fontSize=18, leading=22,
        textColor=colors.HexColor('#1E293B'), alignment=0, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontSize=11, leading=14,
        textColor=colors.HexColor('#475569')
    )
    heading_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'], fontSize=12, leading=15,
        textColor=colors.HexColor('#0F172A'), spaceAfter=6, spaceBefore=8
    )
    cell_header = ParagraphStyle(
        'CellHeader', parent=styles['Normal'], fontSize=9, leading=11,
        textColor=colors.white, fontName='Helvetica-Bold'
    )
    cell_body = ParagraphStyle(
        'CellBody', parent=styles['Normal'], fontSize=9, leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    cell_body_bold = ParagraphStyle(
        'CellBodyBold', parent=styles['Normal'], fontSize=9, leading=11,
        textColor=colors.HexColor('#1E293B'), fontName='Helvetica-Bold'
    )

    story = []
    
    # Document Header
    story.append(Paragraph("<b>MEP & Structural Passport Report</b>", title_style))
    story.append(Paragraph(f"Project Name: <b>{project_data.get('project_name', 'N/A')}</b>", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

    # Overview Table (Width: 540pt)
    gen_data = [
        [make_cell("Project ID", cell_body_bold), make_cell(project_data.get("project_id"), cell_body),
         make_cell("Date Generated", cell_body_bold), make_cell(project_data.get("date"), cell_body)],
        [make_cell("Location", cell_body_bold), make_cell(project_data.get("location"), cell_body),
         make_cell("Approval Status", cell_body_bold), make_cell(project_data.get("status"), cell_body)]
    ]
    t_gen = Table(gen_data, colWidths=[90, 180, 90, 180])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 10))

    # Structural Section
    story.append(Paragraph("1. Structural Specifications", heading_style))
    struct_data = [
        [make_cell("Parameter", cell_header), make_cell("Specification Details", cell_header)],
        [make_cell("Foundation Type", cell_body_bold), make_cell(project_data.get("foundation_type"), cell_body)],
        [make_cell("Load Capacity", cell_body_bold), make_cell(project_data.get("load_capacity"), cell_body)],
        [make_cell("Framing Material", cell_body_bold), make_cell(project_data.get("framing_material"), cell_body)],
        [make_cell("Seismic Compliance", cell_body_bold), make_cell(project_data.get("seismic_compliance"), cell_body)]
    ]
    t_struct = Table(struct_data, colWidths=[160, 380])
    t_struct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_struct)
    story.append(Spacer(1, 10))

    # MEP Section
    story.append(Paragraph("2. MEP Systems", heading_style))
    mep_data = [
        [make_cell("System Domain", cell_header), make_cell("System Specifications", cell_header)],
        [make_cell("Mechanical / HVAC", cell_body_bold), make_cell(project_data.get("hvac_spec"), cell_body)],
        [make_cell("Electrical System", cell_body_bold), make_cell(project_data.get("electrical_capacity"), cell_body)],
        [make_cell("Plumbing & Drainage", cell_body_bold), make_cell(project_data.get("plumbing_spec"), cell_body)],
        [make_cell("Fire Protection", cell_body_bold), make_cell(project_data.get("fire_protection"), cell_body)]
    ]
    t_mep = Table(mep_data, colWidths=[160, 380])
    t_mep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284C7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_mep)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 2. DATABASE & AUTHENTICATION HELPERS
# ==========================================
def authenticate_user(username: str, password: str) -> dict | None:
    """Safely checks credentials against bcrypt hashes in PostgreSQL."""
    try:
        query = "SELECT id, username, password_hash, role FROM users WHERE username = :username;"
        df = conn.query(query, params={"username": username}, ttl=0)
        
        if df.empty:
            return None
            
        record = df.iloc[0].to_dict()
        stored_hash = record["password_hash"]
        
        # Ensure correct bytes formatting for bcrypt
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return {
                "id": record["id"],
                "username": record["username"],
                "role": record["role"]
            }
    except Exception as e:
        st.error(f"Authentication Error: {e}")
    return None

def fetch_passport_data(project_id: str) -> dict | None:
    """Queries project, structural, and MEP details from PostgreSQL."""
    query = """
        SELECT p.id AS project_id, p.name AS project_name, p.location, p.status,
               TO_CHAR(p.created_at, 'YYYY-MM-DD') AS date,
               s.foundation_type, s.load_capacity, s.framing_material, s.seismic_compliance,
               m.hvac_spec, m.electrical_capacity, m.plumbing_spec, m.fire_protection
        FROM projects p
        LEFT JOIN structural_passports s ON p.id = s.project_id
        LEFT JOIN mep_passports m ON p.id = m.project_id
        WHERE p.id = :project_id;
    """
    try:
        df = conn.query(query, params={"project_id": project_id}, ttl="1m")
        return df.iloc[0].to_dict() if not df.empty else None
    except Exception as e:
        st.error(f"Error fetching passport record: {e}")
        return None

def update_own_password(username: str, current_pw: str, new_pw: str) -> tuple[bool, str]:
    """Updates the logged-in user's password with atomic transaction rollback."""
    try:
        df = conn.query("SELECT password_hash FROM users WHERE username = :u;", params={"u": username}, ttl=0)
        if df.empty:
            return False, "User record not found."
            
        stored_hash = df.iloc[0]["password_hash"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')

        if not bcrypt.checkpw(current_pw.encode('utf-8'), stored_hash):
            return False, "Current password is incorrect."
        
        new_hash = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        with conn.session as session:
            session.execute(
                text("UPDATE users SET password_hash = :h WHERE username = :u;"),
                {"h": new_hash, "u": username}
            )
            session.commit()
        return True, "Password updated successfully!"
    except Exception as e:
        return False, f"Database update failed: {e}"

def admin_reset_pw(target_username: str, temp_pw: str) -> tuple[bool, str]:
    """Administrative password override."""
    try:
        new_hash = bcrypt.hashpw(temp_pw.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        with conn.session as session:
            session.execute(
                text("UPDATE users SET password_hash = :h WHERE username = :u;"),
                {"h": new_hash, "u": target_username}
            )
            session.commit()
        return True, f"Password successfully reset for '{target_username}'."
    except Exception as e:
        return False, f"Reset failed: {e}"

def admin_update_role(target_username: str, new_role: str) -> tuple[bool, str]:
    """Administrative role modification."""
    try:
        with conn.session as session:
            session.execute(
                text("UPDATE users SET role = :r WHERE username = :u;"),
                {"r": new_role, "u": target_username}
            )
            session.commit()
        return True, f"Role for '{target_username}' updated to '{new_role}'."
    except Exception as e:
        return False, f"Role update failed: {e}"


# ==========================================
# 3. UI VIEWS
# ==========================================
def render_login_window():
    """Renders centered authentication view."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🏗️ Architectural Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Creative Studios Management System</p>", unsafe_allow_html=True)
        st.divider()

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

def render_passport_view():
    """Renders main project passport lookup and PDF export."""
    st.title("📄 MEP & Structural Passports")
    try:
        projects_df = conn.query("SELECT id, name FROM projects ORDER BY name ASC;", ttl="5m")
        if projects_df.empty:
            st.info("No active projects found in database.")
            return

        project_map = {f"{row['name']} ({row['id']})": row['id'] for _, row in projects_df.iterrows()}
        selected_label = st.selectbox("Select Project Record", list(project_map.keys()))
        selected_id = project_map[selected_label]

        current_role = st.session_state["user"]["role"]
        st.write("---")

        # RBAC Export Guard
        if current_role in EXPORT_ALLOWED_ROLES:
            passport_data = fetch_passport_data(selected_id)
            if passport_data:
                # Preview Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Status", passport_data.get("status", "N/A"))
                m2.metric("Location", passport_data.get("location", "N/A"))
                m3.metric("Date Created", str(passport_data.get("date", "N/A")))

                pdf_bytes = generate_passport_pdf(passport_data)
                
                st.download_button(
                    label="📥 Download Official Passport Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{passport_data['project_id']}_Passport.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("No structural/MEP record linked to this project.")
        else:
            st.error("⛔ Access Restricted: Your role does not have permission to export PDF reports.")
            st.info(f"Authorized Export Roles: {', '.join(EXPORT_ALLOWED_ROLES)}")

    except Exception as e:
        st.error(f"Database query error: {e}")

def render_settings_view():
    """Renders self-service user settings."""
    st.title("🔑 Account Settings")
    st.subheader("Update Password")
    
    with st.form("pw_change_form", clear_on_submit=True):
        cur_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        conf_pw = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password")

        if submit:
            if not cur_pw or not new_pw or not conf_pw:
                st.error("Please fill in all fields.")
            elif new_pw != conf_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters long.")
            else:
                success, msg = update_own_password(
                    st.session_state["user"]["username"], cur_pw, new_pw
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def render_admin_view():
    """Renders system administration panel."""
    st.title("🛠️ Admin User Management")
    
    # Enforce Admin Check
    if st.session_state["user"]["role"] != "Admin":
        st.error("⛔ Access Denied: System Administrator privileges required.")
        return

    try:
        users_df = conn.query("SELECT id, username, role, created_at FROM users ORDER BY username ASC;", ttl=0)
        st.dataframe(users_df, use_container_width=True, hide_index=True)

        if users_df.empty:
            st.info("No user accounts found.")
            return

        st.divider()
        usernames = users_df["username"].tolist()
        selected_user = st.selectbox("Select User Account to Modify", usernames)
        current_user_role = users_df[users_df["username"] == selected_user]["role"].values[0]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Reset User Password")
            with st.form("admin_pw_form", clear_on_submit=True):
                temp_pw = st.text_input("New Temporary Password", type="password")
                submit_pw = st.form_submit_button("Apply Password Reset", use_container_width=True)

                if submit_pw:
                    if len(temp_pw) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        ok, msg = admin_reset_pw(selected_user, temp_pw)
                        st.success(msg) if ok else st.error(msg)

        with col2:
            st.subheader("Update Assigned Role")
            with st.form("admin_role_form"):
                roles = ["Admin", "Project Manager", "Lead Engineer", "Junior Inspector", "Viewer"]
                default_idx = roles.index(current_user_role) if current_user_role in roles else 0
                new_role = st.selectbox("Assigned Role", roles, index=default_idx)
                submit_role = st.form_submit_button("Save Role Change", use_container_width=True)

                if submit_role:
                    if new_role == current_user_role:
                        st.warning("User is already assigned to this role.")
                    else:
                        ok, msg = admin_update_role(selected_user, new_role)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    except Exception as e:
        st.error(f"Admin lookup failed: {e}")


# ==========================================
# 4. MAIN ROUTER
# ==========================================
if not st.session_state["authenticated"]:
    render_login_window()
else:
    # Sidebar Navigation
    current_u = st.session_state["user"]
    st.sidebar.markdown(f"👤 **{current_u['username']}**")
    st.sidebar.caption(f"Role: `{current_u['role']}`")
    st.sidebar.divider()

    options = ["📄 Passports", "🔑 Account Settings"]
    if current_u["role"] == "Admin":
        options.append("🛠️ Admin Panel")

    selection = st.sidebar.radio("Navigation", options)
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

    # View Routing
    if selection == "📄 Passports":
        render_passport_view()
    elif selection == "🔑 Account Settings":
        render_settings_view()
    elif selection == "🛠️ Admin Panel":
        render_admin_view()
