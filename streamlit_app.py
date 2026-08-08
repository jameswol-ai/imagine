import os
import hashlib
import datetime
import pandas as pd
import streamlit as st

# Optional database driver imports with fallback
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

import sqlite3

# ==============================================================================
# PAGE CONFIGURATION & GLASSMORPHISM STYLING
# ==============================================================================
st.set_page_config(
    page_title="Imagine | Architectural & Engineering Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* Glassmorphism Theme Container */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        .login-box {
            max-width: 420px;
            margin: 60px auto;
            padding: 35px;
            background: rgba(20, 25, 40, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }
        
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .badge-role {
            background-color: #2b5c8f;
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# DATABASE CONNECTION & ADAPTER FUNCTIONS
# ==============================================================================
def get_db_connection():
    """
    Connects to PostgreSQL if configuration exists, otherwise falls back to SQLite.
    Returns: (conn, db_type) where db_type is 'postgres' or 'sqlite'
    """
    # Check st.secrets or environment variable for Postgres
    pg_url = None
    if "postgres" in st.secrets:
        pg_url = st.secrets["postgres"].get("url") or st.secrets["postgres"].get("DATABASE_URL")
    elif "DATABASE_URL" in os.environ:
        pg_url = os.environ["DATABASE_URL"]

    if HAS_POSTGRES and pg_url:
        try:
            # SQLAlchemy / Render URLs often start with postgres:// - fix for psycopg2
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(pg_url)
            return conn, "postgres"
        except Exception as e:
            st.warning(f"PostgreSQL connection failed. Falling back to local database. Error: {e}")

    # Fallback SQLite
    conn = sqlite3.connect("app.db", check_same_thread=False)
    return conn, "sqlite"

def format_query(query: str, db_type: str) -> str:
    """Adapts '?' placeholders to '%s' when using PostgreSQL."""
    if db_type == "postgres":
        return query.replace("?", "%s")
    return query

def execute_query(query: str, params: tuple = (), fetch: str = None):
    """
    Safely executes database queries with error handling and transaction rollback.
    fetch options: None, 'one', 'all'
    """
    conn, db_type = get_db_connection()
    formatted_q = format_query(query, db_type)
    result = None
    
    try:
        cur = conn.cursor()
        cur.execute(formatted_q, params)
        
        if fetch == "one":
            result = cur.fetchone()
        elif fetch == "all":
            result = cur.fetchall()
            
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        st.error(f"Database Query Execution Error: {e}")
    finally:
        conn.close()
        
    return result

# ==============================================================================
# SECURITY & DATABASE INITIALIZATION
# ==============================================================================
def hash_password(password: str) -> str:
    """Hashes passwords using SHA-256 with a salt."""
    salt = "imagine_architectural_platform_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    """Initializes required database schema and default admin account."""
    # Create Users table
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(30) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if HAS_POSTGRES else """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Projects table
    execute_query("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            budget NUMERIC(12, 2) NOT NULL,
            status VARCHAR(30) NOT NULL,
            created_by VARCHAR(50) NOT NULL
        )
    """ if HAS_POSTGRES else """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            budget REAL NOT NULL,
            status TEXT NOT NULL,
            created_by TEXT NOT NULL
        )
    """)

    # Check if default admin exists
    admin_user = execute_query("SELECT id FROM users WHERE username = ?", ("admin",), fetch="one")
    if not admin_user:
        default_pw = hash_password("admin123")
        execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", default_pw, "Admin")
        )

init_db()

# ==============================================================================
# AUTHENTICATION
# ==============================================================================
def authenticate_user(username: str, password: str):
    """Verifies credentials against the database."""
    if not username or not password:
        return False, None
    
    pwd_hash = hash_password(password)
    row = execute_query(
        "SELECT password_hash, role FROM users WHERE username = ?",
        (username,),
        fetch="one"
    )
    
    if row and row[0] == pwd_hash:
        return True, row[1]
    return False, None

def render_improved_login():
    """Renders glassmorphic authentication UI."""
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🏛️ Imagine Platform")
    st.caption("Architectural & Engineering Management System")
    st.markdown("---")
    
    with st.form("login_form"):
        u = st.text_input("Username", placeholder="e.g. admin")
        p = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            ok, role = authenticate_user(u.strip(), p.strip())
            if ok:
                st.session_state["authenticated"] = True
                st.session_state["username"] = u.strip()
                st.session_state["role"] = role
                st.success("Authentication successful! Loading system...")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# APPLICATION MODULES
# ==============================================================================
def render_projects_module():
    st.header("📋 Project & Architecture Management")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("New Project Registration")
        with st.form("new_project_form"):
            title = st.text_input("Project Title")
            category = st.selectbox("Category", ["New Construction", "Renovation", "MEP Upgrade", "Structural"])
            budget = st.number_input("Budget ($)", min_value=1000.0, step=5000.0)
            status = st.selectbox("Initial Status", ["Planning", "Design Phase", "In Review", "Approved"])
            
            if st.form_submit_button("Create Project", use_container_width=True):
                if title:
                    execute_query(
                        "INSERT INTO projects (title, category, budget, status, created_by) VALUES (?, ?, ?, ?, ?)",
                        (title, category, budget, status, st.session_state.get("username", "system"))
                    )
                    st.success(f"Project '{title}' registered.")
                    st.rerun()
                else:
                    st.warning("Please provide a project title.")

    with col2:
        st.subheader("Active Projects Overview")
        rows = execute_query("SELECT id, title, category, budget, status, created_by FROM projects", fetch="all")
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Title", "Category", "Budget ($)", "Status", "Created By"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No projects recorded yet. Create one to get started.")

def render_mep_module():
    st.header("⚡ Mechanical, Electrical & Plumbing (MEP)")
    
    tab1, tab2, tab3 = st.tabs(["Electrical Load", "HVAC / Airflow", "Plumbing Pipe Sizing"])
    
    with tab1:
        st.subheader("Electrical Panel Load Estimation")
        area = st.number_input("Floor Area (sq meters)", min_value=10.0, value=150.0)
        density = st.slider("Power Density (W/sqm)", 10, 100, 30)
        safety_factor = st.slider("Safety Factor", 1.0, 1.5, 1.25)
        
        total_kw = (area * density * safety_factor) / 1000.0
        amps_3phase = (total_kw * 1000) / (400 * 1.732 * 0.9)
        
        c1, c2 = st.columns(2)
        c1.metric("Estimated Demand", f"{total_kw:.2f} kW")
        c2.metric("3-Phase Current (400V)", f"{amps_3phase:.2f} A")
        
    with tab2:
        st.subheader("HVAC Airflow Requirement")
        room_vol = st.number_input("Room Volume (m³)", min_value=20.0, value=300.0)
        ach = st.number_input("Air Changes per Hour (ACH)", min_value=1, value=6)
        cfm = (room_vol * ach * 35.315) / 60.0
        st.metric("Required Airflow", f"{cfm:.1f} CFM", help="Cubic Feet per Minute")
        
    with tab3:
        st.subheader("Plumbing Flow Rate Calculator")
        fixture_units = st.number_input("Total Fixture Units (WSFU)", min_value=1, value=25)
        est_gpm = fixture_units * 0.75  # Simplified Hunter curve approximation
        st.metric("Peak Water Demand", f"{est_gpm:.2f} GPM")

def render_structural_module():
    st.header("🏗️ Structural Eurocode Checks")
    st.caption("Simplified Beam Bending & Deflection Capacity Check")
    
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Span Length (m)", min_value=1.0, value=6.0)
        udl = st.number_input("Uniformly Distributed Load (kN/m)", min_value=1.0, value=15.0)
        fy = st.selectbox("Steel Grade (fy in MPa)", [275, 355, 460], index=1)
    
    with c2:
        w_el = st.number_input("Elastic Section Modulus Wel (cm³)", min_value=50.0, value=400.0)
        
    max_moment = (udl * (length ** 2)) / 8.0  # M = wL^2 / 8
    capacity = (w_el * 1e-6 * (fy * 1e3))  # kNm
    utilization = (max_moment / capacity) * 100
    
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Design Bending Moment", f"{max_moment:.2f} kNm")
    m2.metric("Section Moment Resistance", f"{capacity:.2f} kNm")
    m3.metric("Bending Utilization", f"{utilization:.1f} %", 
              delta="SAFE" if utilization <= 100 else "OVERLOADED",
              delta_color="normal" if utilization <= 100 else "inverse")

def render_forex_module():
    st.header("💱 Forex & Financial Tracking")
    
    rates = {"USD": 1.0, "EUR": 0.92, "GBP": 0.78, "UGX": 3700.0, "KES": 130.0}
    
    c1, c2, c3 = st.columns(3)
    with c1:
        amount = st.number_input("Base Amount", min_value=1.0, value=10000.0)
    with c2:
        from_curr = st.selectbox("From Currency", list(rates.keys()), index=0)
    with c3:
        to_curr = st.selectbox("To Currency", list(rates.keys()), index=3)
        
    usd_val = amount / rates[from_curr]
    converted = usd_val * rates[to_curr]
    
    st.subheader(f"Converted Value: **{converted:,.2f} {to_curr}**")

def render_admin_module():
    st.header("⚙️ User & Access Control Management")
    if st.session_state.get("role") != "Admin":
        st.error("Access Restricted: Requires Administrator privileges.")
        return

    st.subheader("Create New User")
    with st.form("create_user_form"):
        new_u = st.text_input("Username")
        new_p = st.text_input("Password", type="password")
        new_r = st.selectbox("Role", ["Admin", "Project Manager", "Engineer", "Architect", "Viewer"])
        
        if st.form_submit_button("Register User", use_container_width=True):
            if new_u and new_p:
                try:
                    execute_query(
                        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (new_u.strip(), hash_password(new_p.strip()), new_r)
                    )
                    st.success(f"User '{new_u}' registered successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create user: {e}")
            else:
                st.warning("Please fill out all fields.")
                
    st.subheader("Existing System Users")
    users = execute_query("SELECT id, username, role, created_at FROM users", fetch="all")
    if users:
        st.dataframe(pd.DataFrame(users, columns=["ID", "Username", "Role", "Created At"]), use_container_width=True)

# ==============================================================================
# MAIN ROUTER
# ==============================================================================
def main():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        render_improved_login()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.title("Imagine Platform")
        st.markdown(f"User: **{st.session_state.get('username')}**")
        st.markdown(f"Role: <span class='badge-role'>{st.session_state.get('role')}</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        menu = ["Projects & Arch", "MEP Analysis", "Structural Checks", "Forex & Budgeting"]
        if st.session_state.get("role") == "Admin":
            menu.append("User Management")
            
        choice = st.radio("Navigation", menu)
        
        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Routing
    if choice == "Projects & Arch":
        render_projects_module()
    elif choice == "MEP Analysis":
        render_mep_module()
    elif choice == "Structural Checks":
        render_structural_module()
    elif choice == "Forex & Budgeting":
        render_forex_module()
    elif choice == "User Management":
        render_admin_module()

if __name__ == "__main__":
    main()
