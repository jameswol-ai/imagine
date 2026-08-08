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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# Inject Custom CSS for Sleek Modern Styling
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .login-header {
        text-align: center;
        padding-bottom: 1rem;
    }
    .login-brand {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .login-subtitle {
        font-size: 0.95rem;
        color: #64748b;
    }
    .user-badge {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .error-card {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# RBAC Configuration
EXPORT_ALLOWED_ROLES = {"Admin", "Project Manager", "Lead Engineer"}


# ==========================================
# 0. SAFE DATABASE CONNECTION HANDLER
# ==========================================
def get_db_connection():
    """
    Safely retrieves the Streamlit SQL connection to prevent hard-crashing 
    the app when st.secrets is missing or database is offline.
    """
    try:
        # Check if secrets exist before attempting connection
        has_secrets = False
        if hasattr(st, "secrets"):
            if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
                has_secrets = True
            elif "connections.postgresql" in st.secrets:
                has_secrets = True
            elif "postgres" in st.secrets:
                has_secrets = True

        if not has_secrets:
            return None, "Missing `[connections.postgresql]` configuration in Streamlit secrets."

        conn = st.connection("postgresql", type="sql")
        return conn, None
    except Exception as err:
        return None, str(err)


def render_missing_secrets_ui(error_msg: str):
    """Renders diagnostic guidance when database configuration is missing."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error("🔌 PostgreSQL Connection Required")
        st.markdown(f"**Diagnostic Error:** `{error_msg}`")
        
        with st.expander("🛠️ How to fix this in Streamlit Community Cloud", expanded=True):
            st.markdown("""
            1. Go to your **Streamlit Cloud Dashboard**.
            2. Click **Manage App** (lower right) -> **⋮ Settings** -> **Secrets**.
            3. Paste your connection TOML configuration:
            ```toml
            [connections.postgresql]
            url = "postgresql://username:password@your-db-host.com:5432/dbname?sslmode=require"
            ```
            4. Click **Save** to restart the app.
            """)
            
        with st.expander("💻 How to fix this locally"):
            st.markdown("""
            Create or edit `.streamlit/secrets.toml` in your project root directory:
            ```toml
            [connections.postgresql]
            url = "postgresql://postgres:password@localhost:5432/creativestudios"
            ```
            """)


# ==========================================
# 1. REPORTLAB PDF GENERATOR
# ==========================================
def make_cell(text_val, style):
    val_str = str(text_val) if text_val is not None and not pd.isna(text_val) else "N/A"
    return Paragraph(val_str, style)

def generate_passport_pdf(project_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
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
    story.append(Paragraph("<b>MEP & Structural Passport Report</b>", title_style))
    story.append(Paragraph(f"Project Name: <b>{project_data.get('project_name', 'N/A')}</b>", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

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
def authenticate_user(conn, username: str, password: str) -> dict | None:
    try:
        query = "SELECT id, username, password_hash, role FROM users WHERE username = :username;"
        df = conn.query(query, params={"username": username}, ttl=0)
        
        if df.empty:
            return None
            
        record = df.iloc[0].to_dict()
        stored_hash = record["password_hash"]
        
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return {
                "id": record["id"],
                "username": record["username"],
                "role": record["role"]
            }
    except Exception as e:
        st.error(f"Database authentication error: {e}")
    return None

def fetch_passport_data(conn, project_id: str) -> dict | None:
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
        st.error(f"Error querying passport data: {e}")
        return None

def update_own_password(conn, username: str, current_pw: str, new_pw: str) -> tuple[bool, str]:
    try:
        df = conn.query("SELECT password_hash FROM users WHERE username = :u;", params={"u": username}, ttl=0)
        if df.empty:
            return False, "User account not found."
            
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
        return False, f"Password update failed: {e}"

def admin_reset_pw(conn, target_username: str, temp_pw: str) -> tuple[bool, str]:
    try:
        new_hash = bcrypt.hashpw(temp_pw.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        with conn.session as session:
            session.execute(
                text("UPDATE users SET password_hash = :h WHERE username = :u;"),
                {"h": new_hash, "u": target_username}
            )
            session.commit()
        return True, f"Password reset successfully for '{target_username}'."
    except Exception as e:
        return False, f"Password reset failed: {e}"

def admin_update_role(conn, target_username: str, new_role: str) -> tuple[bool, str]:
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
# 3. VIEWS & LOGIN WINDOW
# ==========================================
def render_login_window(conn):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        st.markdown("""
        <div class="login-header">
            <div class="login-brand">🏗️ Creative Studios</div>
            <div class="login-subtitle">Architectural Management & Passport System</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Sign In")
            username = st.text_input("Username", placeholder="e.g. admin_user")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("Authenticate", use_container_width=True, type="primary")

            if submit:
                if not username.strip() or not password.strip():
                    st.warning("Please provide both a username and password.")
                else:
                    with st.spinner("Verifying credentials..."):
                        user = authenticate_user(conn, username.strip(), password.strip())
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
        
        st.caption("🔒 Secured with bcrypt password hashing and PostgreSQL role-based access.")

def render_passport_view(conn):
    st.title("📄 MEP & Structural Passports")
    st.caption("Retrieve project structural parameters and download official compliance reports.")
    
    try:
        projects_df = conn.query("SELECT id, name FROM projects ORDER BY name ASC;", ttl="5m")
        if projects_df.empty:
            st.info("No projects registered in database.")
            return

        project_map = {f"{row['name']} ({row['id']})": row['id'] for _, row in projects_df.iterrows()}
        selected_label = st.selectbox("Select Active Project", list(project_map.keys()))
        selected_id = project_map[selected_label]

        current_role = st.session_state["user"]["role"]
        st.divider()

        passport_data = fetch_passport_data(conn, selected_id)
        
        if passport_data:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Project ID", passport_data.get("project_id", "N/A"))
            m2.metric("Approval Status", passport_data.get("status", "Pending"))
            m3.metric("Location", passport_data.get("location", "N/A"))
            m4.metric("Created On", str(passport_data.get("date", "N/A")))

            st.subheader("Specification Preview")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Structural Attributes**")
                st.json({
                    "Foundation": passport_data.get("foundation_type", "N/A"),
                    "Load Capacity": passport_data.get("load_capacity", "N/A"),
                    "Framing": passport_data.get("framing_material", "N/A"),
                    "Seismic": passport_data.get("seismic_compliance", "N/A")
                })
            with c2:
                st.markdown("**MEP Attributes**")
                st.json({
                    "HVAC": passport_data.get("hvac_spec", "N/A"),
                    "Electrical": passport_data.get("electrical_capacity", "N/A"),
                    "Plumbing": passport_data.get("plumbing_spec", "N/A"),
                    "Fire Protection": passport_data.get("fire_protection", "N/A")
                })

            st.divider()

            if current_role in EXPORT_ALLOWED_ROLES:
                pdf_bytes = generate_passport_pdf(passport_data)
                st.download_button(
                    label="📥 Export Passport Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"{passport_data['project_id']}_Passport.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.error("⛔ Permission Restricted: Your account role does not have authorization to download PDF reports.")
                st.info(f"Authorized Export Roles: {', '.join(EXPORT_ALLOWED_ROLES)}")
        else:
            st.warning("No structural or MEP passport records linked to this project.")

    except Exception as e:
        st.error(f"Error executing database lookup: {e}")

def render_settings_view(conn):
    st.title("🔑 Account Settings")
    st.subheader("Change Password")
    
    with st.form("pw_change_form", clear_on_submit=True):
        cur_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        conf_pw = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password", type="primary")

        if submit:
            if not cur_pw or not new_pw or not conf_pw:
                st.error("Please fill in all password fields.")
            elif new_pw != conf_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters long.")
            else:
                success, msg = update_own_password(
                    conn, st.session_state["user"]["username"], cur_pw, new_pw
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def render_admin_view(conn):
    st.title("🛠️ Admin Management")
    
    if st.session_state["user"]["role"] != "Admin":
        st.error("⛔ Access Denied: Administrator role required.")
        return

    try:
        users_df = conn.query("SELECT id, username, role, created_at FROM users ORDER BY username ASC;", ttl=0)
        st.subheader("System Accounts Roster")
        st.dataframe(users_df, use_container_width=True, hide_index=True)

        if users_df.empty:
            st.info("No user records found.")
            return

        st.divider()
        usernames = users_df["username"].tolist()
        selected_user = st.selectbox("Select Account to Modify", usernames)
        current_role = users_df[users_df["username"] == selected_user]["role"].values[0]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Reset User Password")
            with st.form("admin_pw_form", clear_on_submit=True):
                temp_pw = st.text_input("Temporary Password", type="password")
                submit_pw = st.form_submit_button("Override Password", use_container_width=True)

                if submit_pw:
                    if len(temp_pw) < 8:
                        st.error("Password must be at least 8 characters long.")
                    else:
                        ok, msg = admin_reset_pw(conn, selected_user, temp_pw)
                        st.success(msg) if ok else st.error(msg)

        with col2:
            st.subheader("Modify Assigned Role")
            with st.form("admin_role_form"):
                roles = ["Admin", "Project Manager", "Lead Engineer", "Junior Inspector", "Viewer"]
                default_idx = roles.index(current_role) if current_role in roles else 0
                new_role = st.selectbox("Assigned Role", roles, index=default_idx)
                submit_role = st.form_submit_button("Save Role Modification", use_container_width=True)

                if submit_role:
                    if new_role == current_role:
                        st.warning("User already holds this role assignment.")
                    else:
                        ok, msg = admin_update_role(conn, selected_user, new_role)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    except Exception as e:
        st.error(f"Error loading admin panel data: {e}")


# ==========================================
# 4. MAIN APPLICATION ENTRYPOINT
# ==========================================
conn, err = get_db_connection()

if conn is None:
    render_missing_secrets_ui(err)
else:
    if not st.session_state["authenticated"]:
        render_login_window(conn)
    else:
        current_u = st.session_state["user"]
        
        st.sidebar.markdown(f"### 👤 {current_u['username']}")
        st.sidebar.markdown(f"Role: <span class='user-badge'>{current_u['role']}</span>", unsafe_allow_html=True)
        st.sidebar.divider()

        options = ["📄 Passports", "🔑 Account Settings"]
        if current_u["role"] == "Admin":
            options.append("🛠️ Admin Panel")

        selection = st.sidebar.radio("Navigation Menu", options)
        
        st.sidebar.divider()
        if st.sidebar.button("Log Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()

        if selection == "📄 Passports":
            render_passport_view(conn)
        elif selection == "🔑 Account Settings":
            render_settings_view(conn)
        elif selection == "🛠️ Admin Panel":
            render_admin_view(conn)
