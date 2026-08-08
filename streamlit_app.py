import io
import bcrypt
import pandas as pd
import streamlit as st
from sqlalchemy import text
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

# --- Page Configuration ---
st.set_page_config(
    page_title="Creative Studios - Passport Portal",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Database Connection
conn = st.connection("postgresql", type="sql")

# Allowed export roles
EXPORT_ALLOWED_ROLES = {"Admin", "Project Manager", "Lead Engineer"}


# ==========================================
# 1. PDF GENERATOR MODULE
# ==========================================
def generate_passport_pdf(project_data: dict) -> bytes:
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
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'], fontSize=20, leading=24,
        textColor=colors.HexColor('#1E293B'), alignment=0
    )
    heading_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'], fontSize=13, leading=16,
        textColor=colors.HexColor('#0F172A'), spaceAfter=6
    )

    story = []
    story.append(Paragraph("<b>MEP & Structural Passport Report</b>", title_style))
    story.append(Paragraph(f"Project Name: {project_data.get('project_name', 'N/A')}", styles['Subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

    gen_data = [
        ["Project ID", project_data.get("project_id", "N/A"), "Date Generated", str(project_data.get("date", "N/A"))],
        ["Location", project_data.get("location", "N/A"), "Approval Status", project_data.get("status", "Pending")]
    ]
    t_gen = Table(gen_data, colWidths=[100, 170, 100, 170])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Structural Specifications", heading_style))
    struct_data = [
        ["Parameter", "Specification Details"],
        ["Foundation Type", project_data.get("foundation_type", "N/A")],
        ["Load Capacity", project_data.get("load_capacity", "N/A")],
        ["Framing Material", project_data.get("framing_material", "N/A")],
        ["Seismic Compliance", project_data.get("seismic_compliance", "N/A")]
    ]
    t_struct = Table(struct_data, colWidths=[180, 360])
    t_struct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_struct)
    story.append(Spacer(1, 14))

    story.append(Paragraph("2. MEP Systems", heading_style))
    mep_data = [
        ["System Domain", "System Specifications"],
        ["Mechanical / HVAC", project_data.get("hvac_spec", "N/A")],
        ["Electrical System", project_data.get("electrical_capacity", "N/A")],
        ["Plumbing & Drainage", project_data.get("plumbing_spec", "N/A")],
        ["Fire Protection", project_data.get("fire_protection", "N/A")]
    ]
    t_mep = Table(mep_data, colWidths=[180, 360])
    t_mep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_mep)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 2. AUTHENTICATION & DATABASE HELPERS
# ==========================================
def authenticate_user(username: str, password: str) -> dict | None:
    query = "SELECT id, username, password_hash, role FROM users WHERE username = :username;"
    df = conn.query(query, params={"username": username}, ttl=0)
    if df.empty:
        return None
    record = df.iloc[0].to_dict()
    if bcrypt.checkpw(password.encode('utf-8'), record["password_hash"].encode('utf-8')):
        return {"id": record["id"], "username": record["username"], "role": record["role"]}
    return None

def fetch_passport_data(project_id: str) -> dict | None:
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
    df = conn.query(query, params={"project_id": project_id}, ttl="1m")
    return df.iloc[0].to_dict() if not df.empty else None

def update_own_password(username: str, current_pw: str, new_pw: str) -> tuple[bool, str]:
    df = conn.query("SELECT password_hash FROM users WHERE username = :u;", params={"u": username}, ttl=0)
    if df.empty or not bcrypt.checkpw(current_pw.encode('utf-8'), df.iloc[0]["password_hash"].encode('utf-8')):
        return False, "Current password is incorrect."
    
    new_hash = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
    try:
        with conn.session as session:
            session.execute(text("UPDATE users SET password_hash = :h WHERE username = :u;"), {"h": new_hash, "u": username})
            session.commit()
        return True, "Password successfully updated!"
    except Exception as e:
        return False, f"Database error: {e}"

def admin_reset_pw(username: str, temp_pw: str) -> tuple[bool, str]:
    new_hash = bcrypt.hashpw(temp_pw.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
    try:
        with conn.session as session:
            session.execute(text("UPDATE users SET password_hash = :h WHERE username = :u;"), {"h": new_hash, "u": username})
            session.commit()
        return True, f"Password reset for '{username}'."
    except Exception as e:
        return False, f"Failed: {e}"

def admin_update_role(username: str, new_role: str) -> tuple[bool, str]:
    try:
        with conn.session as session:
            session.execute(text("UPDATE users SET role = :r WHERE username = :u;"), {"r": new_role, "u": username})
            session.commit()
        return True, f"Role for '{username}' updated to '{new_role}'."
    except Exception as e:
        return False, f"Failed: {e}"


# ==========================================
# 3. UI VIEWS
# ==========================================
def render_login_window():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🏗️ Architectural Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Sign in to access MEP & Structural Passports</p>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

def render_passport_view():
    st.title("📄 MEP & Structural Passports")
    try:
        projects_df = conn.query("SELECT id, name FROM projects ORDER BY name ASC;", ttl="5m")
        if projects_df.empty:
            st.info("No projects registered in database.")
            return

        project_map = {f"{row['name']} ({row['id']})": row['id'] for _, row in projects_df.iterrows()}
        selected_label = st.selectbox("Select Project Record", list(project_map.keys()))
        selected_id = project_map[selected_label]

        current_role = st.session_state["user"]["role"]
        
        if current_role in EXPORT_ALLOWED_ROLES:
            passport_data = fetch_passport_data(selected_id)
            if passport_data:
                pdf_bytes = generate_passport_pdf(passport_data)
                st.download_button(
                    label="📥 Download Official Passport Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{passport_data['project_id']}_Passport.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("No passport metadata linked to this project.")
        else:
            st.error("⛔ Permission Denied: Your role does not have authorization to download PDF reports.")
            st.info(f"Export Authorized Roles: {', '.join(EXPORT_ALLOWED_ROLES)}")

    except Exception as e:
        st.error(f"Database error: {e}")

def render_settings_view():
    st.title("🔑 Account Settings")
    st.subheader("Change Password")
    with st.form("pw_change_form", clear_on_submit=True):
        cur_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        conf_pw = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password")

        if submit:
            if not cur_pw or not new_pw:
                st.error("Please complete all required fields.")
            elif new_pw != conf_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters.")
            else:
                success, msg = update_own_password(st.session_state["user"]["username"], cur_pw, new_pw)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def render_admin_view():
    st.title("🛠️ Admin Management")
    if st.session_state["user"]["role"] != "Admin":
        st.error("⛔ Access Restricted to System Administrators.")
        return

    users_df = conn.query("SELECT id, username, role, created_at FROM users ORDER BY username ASC;", ttl=0)
    st.dataframe(users_df, use_container_width=True, hide_index=True)

    selected_user = st.selectbox("Select User to Modify", users_df["username"].tolist())
    current_user_role = users_df[users_df["username"] == selected_user]["role"].values[0]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Reset Password")
        with st.form("admin_pw_form", clear_on_submit=True):
            temp_pw = st.text_input("New Temporary Password", type="password")
            if st.form_submit_button("Apply Password Reset"):
                if len(temp_pw) >= 8:
                    ok, msg = admin_reset_pw(selected_user, temp_pw)
                    st.success(msg) if ok else st.error(msg)
                else:
                    st.error("Minimum 8 characters required.")

    with c2:
        st.subheader("Modify User Role")
        with st.form("admin_role_form"):
            roles = ["Admin", "Project Manager", "Lead Engineer", "Junior Inspector", "Viewer"]
            new_role = st.selectbox("Assigned Role", roles, index=roles.index(current_user_role) if current_user_role in roles else 0)
            if st.form_submit_button("Update Role"):
                ok, msg = admin_update_role(selected_user, new_role)
                st.success(msg) if ok else st.error(msg)
                st.rerun()


# ==========================================
# 4. ROUTING & CONTROLLER
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if not st.session_state["authenticated"]:
    render_login_window()
else:
    # Navigation Sidebar
    u = st.session_state["user"]
    st.sidebar.markdown(f"👤 **{u['username']}**")
    st.sidebar.caption(f"Role: `{u['role']}`")
    
    nav_options = ["📄 Passports", "🔑 Account Settings"]
    if u["role"] == "Admin":
        nav_options.append("🛠️ Admin Panel")
        
    choice = st.sidebar.radio("Navigation", nav_options)
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

    if choice == "📄 Passports":
        render_passport_view()
    elif choice == "🔑 Account Settings":
        render_settings_view()
    elif choice == "🛠️ Admin Panel":
        render_admin_view()
