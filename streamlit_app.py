# =========================================================
# IMAGINE – Architectural Intellect, MEP Engine & Enterprise System
# Integrated Unified Edition v23.0
# =========================================================

import json
import os
import sqlite3
import uuid
import math
import hashlib
import random
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# PostgreSQL Driver Import with Fallback
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# ------------------------------------------------------------
# PAGE CONFIGURATION & THEME
# ------------------------------------------------------------
st.set_page_config(
    page_title="Imagine - Architectural & Engineering Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #dddddd; }
        .stSidebar { background-color: #0c0c0c; border-right: 1px solid #222222; }
        h1, h2, h3, h4, h5, h6 { color: #eeeeee !important; font-weight: 600; }
        
        .glass-card {
            background: rgba(20, 20, 20, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }
        
        .stMetric {
            background: rgba(30, 30, 30, 0.4);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #333333;
            color: #eee;
        }
        
        .badge-role {
            background-color: #2563eb;
            color: #ffffff;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80" width="240" height="64">
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#9ea5b1"/>
      <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>
  </defs>
  <g transform="translate(130,25)">
    <circle cx="0" cy="0" r="16" stroke="url(#lg)" stroke-width="2" fill="none"/>
    <line x1="0" y1="-14" x2="0" y2="14" stroke="url(#lg)" stroke-width="2"/>
    <line x1="-14" y1="0" x2="14" y2="0" stroke="url(#lg)" stroke-width="2"/>
    <polygon points="0,-12 3,0 0,12 -3,0" fill="url(#lg)"/>
    <circle cx="0" cy="0" r="4" fill="#000"/>
  </g>
  <text x="150" y="65" text-anchor="middle"
        font-family="'Segoe UI', Arial, sans-serif" font-weight="400" font-size="28"
        fill="url(#lg)" letter-spacing="6">Imagine</text>
</svg>
"""

# ------------------------------------------------------------
# DATABASE PERSISTENCE LAYER (PostgreSQL / SQLite Hybrid)
# ------------------------------------------------------------
def get_db_connection():
    pg_url = None
    if "postgres" in st.secrets:
        pg_url = st.secrets["postgres"].get("url") or st.secrets["postgres"].get("DATABASE_URL")
    elif "DATABASE_URL" in os.environ:
        pg_url = os.environ["DATABASE_URL"]

    if HAS_POSTGRES and pg_url:
        try:
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(pg_url, sslmode="require")
            return conn, "postgres"
        except Exception:
            pass

    conn = sqlite3.connect("imagine_platform.db", check_same_thread=False)
    return conn, "sqlite"

def format_query(query: str, db_type: str) -> str:
    return query.replace("?", "%s") if db_type == "postgres" else query

def execute_query(query: str, params: tuple = (), fetch: str = None):
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
        st.error(f"Database Query Error: {e}")
    finally:
        conn.close()
    return result

# ------------------------------------------------------------
# AUTHENTICATION & DATABASE INIT
# ------------------------------------------------------------
def hash_password(password: str, salt: str = "imagine_architectural_platform_salt_2026") -> str:
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    conn, db_type = get_db_connection()
    is_pg = (db_type == "postgres")
    
    users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            salt VARCHAR(64) NOT NULL DEFAULT 'imagine_architectural_platform_salt_2026',
            role VARCHAR(30) NOT NULL DEFAULT 'Viewer',
            email VARCHAR(100) DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if is_pg else """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL DEFAULT 'imagine_architectural_platform_salt_2026',
            role TEXT NOT NULL DEFAULT 'Viewer',
            email TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute_query(users_sql)

    projects_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            client TEXT,
            category TEXT DEFAULT 'New Construction',
            status TEXT DEFAULT 'Draft',
            gross_area FLOAT DEFAULT 0.0,
            estimated_cost_usd FLOAT DEFAULT 0.0,
            created_by TEXT DEFAULT 'system',
            design_data TEXT DEFAULT '{}',
            approval_role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if is_pg else """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            client TEXT,
            category TEXT DEFAULT 'New Construction',
            status TEXT DEFAULT 'Draft',
            gross_area REAL DEFAULT 0.0,
            estimated_cost_usd REAL DEFAULT 0.0,
            created_by TEXT DEFAULT 'system',
            design_data TEXT DEFAULT '{}',
            approval_role TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute_query(projects_sql)

    logs_sql = """
        CREATE TABLE IF NOT EXISTS system_logs (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if is_pg else """
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute_query(logs_sql)

    # Seed Default User Accounts
    default_users = [
        ("admin", "admin123", "Admin", "admin@imagine.io"),
        ("lead_eng", "lead123", "Project Lead", "lead@imagine.io"),
        ("arch_user", "arch123", "Architect", "arch@imagine.io"),
        ("mep_eng", "mep123", "MEP Engineer", "mep@imagine.io"),
        ("viewer", "view123", "Viewer", "client@imagine.io")
    ]
    
    for u, p, r, e in default_users:
        if not execute_query("SELECT id FROM users WHERE username = ?", (u,), fetch="one"):
            salt = uuid.uuid4().hex
            pwd_hash = hash_password(p, salt)
            execute_query(
                "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?, ?, ?, ?, ?)",
                (u, pwd_hash, salt, r, e)
            )

init_db()

def authenticate_user(username: str, password: str):
    row = execute_query("SELECT password_hash, salt, role FROM users WHERE username = ?", (username,), fetch="one")
    if row:
        db_hash, salt, role = row
        if hash_password(password, salt) == db_hash or hash_password(password, "imagine_architectural_platform_salt_2026") == db_hash:
            return True, role
    return False, None

def register_user(username, password, email="", role="Viewer"):
    salt = uuid.uuid4().hex
    pwd_hash = hash_password(password, salt)
    try:
        execute_query(
            "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?, ?, ?, ?, ?)",
            (username, pwd_hash, salt, role, email)
        )
        return True, f"User '{username}' registered successfully."
    except Exception as e:
        return False, f"Registration failed: {e}"

def log_system_event(msg):
    username = st.session_state.get("user", {}).get("username", "system") if st.session_state.get("user") else "system"
    execute_query("INSERT INTO system_logs (username, message) VALUES (?, ?)", (username, msg))

# ------------------------------------------------------------
# DOMAIN DATA & REGIONAL CONSTANTS
# ------------------------------------------------------------
REGIONAL_FX_DEFAULTS = {
    "Kenya": {"currency": "KES", "rate_to_usd": 129.49, "symbol": "KSh", "cost_multiplier": 1.0, "risk_premium": 0.02},
    "Uganda": {"currency": "UGX", "rate_to_usd": 3700.00, "symbol": "USh", "cost_multiplier": 0.95, "risk_premium": 0.03},
    "Tanzania": {"currency": "TZS", "rate_to_usd": 2625.00, "symbol": "TSh", "cost_multiplier": 0.98, "risk_premium": 0.025},
    "South Sudan": {"currency": "SSP", "rate_to_usd": 4626.40, "symbol": "SSP", "cost_multiplier": 1.35, "risk_premium": 0.08}
}

if "regional_fx" not in st.session_state:
    st.session_state.regional_fx = REGIONAL_FX_DEFAULTS.copy()

ARCH_DOMAINS = {
    "Residential": {"types": ["Luxury Villa", "Modern Apartment", "Townhouse Studio"], "max_coverage": 0.5, "max_far": 2.5},
    "Commercial": {"types": ["Corporate Hub Block", "Boutique Retail Space", "Medical Clinic Center"], "max_coverage": 0.7, "max_far": 4.5},
    "Industrial": {"types": ["Distribution Depot", "Heavy Machinery Plant Warehouse"], "max_coverage": 0.6, "max_far": 1.8}
}

SOIL_PROFILES = {
    "Kampala Red Lateritic Clay": {"cohesion": 35, "friction_angle": 12, "unit_weight": 18.0},
    "Nairobi Black Cotton Soil": {"cohesion": 15, "friction_angle": 8, "unit_weight": 16.5},
    "Coastal Quartz Sand (Dar)": {"cohesion": 0, "friction_angle": 32, "unit_weight": 19.0},
    "Juba Alluvial Silt Deposit": {"cohesion": 20, "friction_angle": 15, "unit_weight": 17.5}
}

SEISMIC_ZONES = {
    "Low (PGA=0.05g)": {"PGA": 0.05, "S": 1.0, "importance": 1.0},
    "Moderate (PGA=0.15g)": {"PGA": 0.15, "S": 1.2, "importance": 1.0},
    "High (PGA=0.25g)": {"PGA": 0.25, "S": 1.4, "importance": 1.25}
}

WIND_ZONES = {"Low (22 m/s)": 22, "Moderate (28 m/s)": 28, "High (35 m/s)": 35}

ROOM_COLORS = {
    "Bedroom": "#a78bfa", "Living Room": "#34d399", "Kitchen": "#fbbf24",
    "Bathroom": "#60a5fa", "Office": "#f87171", "Dining": "#f472b6",
    "Corridor": "#94a3b8", "Garage": "#64748b"
}

if "active_design" not in st.session_state:
    st.session_state.active_design = None

# ------------------------------------------------------------
# COMPUTATION ENGINES
# ------------------------------------------------------------
def run_mep_analysis(design):
    gfa = design["total_gfa"]
    domain = design.get("domain", "Residential")
    baths = design.get("bathrooms", 2)
    
    hvac_densities = {"Residential": 120.0, "Commercial": 160.0, "Industrial": 100.0}
    w_per_m2 = hvac_densities.get(domain, 130.0)
    cooling_kw = (gfa * w_per_m2) / 1000.0
    cooling_tr = cooling_kw / 3.517
    airflow_cfm = cooling_tr * 400.0
    
    elec_densities = {"Residential": 35.0, "Commercial": 65.0, "Industrial": 85.0}
    w_elec_per_m2 = elec_densities.get(domain, 50.0)
    diversity = {"Residential": 0.70, "Commercial": 0.80, "Industrial": 0.85}.get(domain, 0.75)
    
    total_connected_kw = (gfa * w_elec_per_m2) / 1000.0
    connected_kva = total_connected_kw / 0.85
    max_demand_kva = connected_kva * diversity
    
    est_occupants = max(2, math.ceil(gfa / 15.0))
    daily_water_l = est_occupants * 150.0
    wsfu = (baths * 8) + (math.ceil(gfa / 100) * 4)
    
    return {
        "mechanical": {"cooling_load_kw": round(cooling_kw, 2), "cooling_load_tr": round(cooling_tr, 2), "supply_airflow_cfm": round(airflow_cfm, 0)},
        "electrical": {"connected_load_kw": round(total_connected_kw, 2), "max_demand_kva": round(max_demand_kva, 2), "transformer_rating_kva": math.ceil(max_demand_kva * 1.2 / 50.0) * 50},
        "plumbing": {"est_occupants": est_occupants, "daily_water_demand_liters": round(daily_water_l, 0), "total_wsfu": wsfu}
    }

def run_eurocode_analysis(design):
    span = design.get("layout", {}).get("span", 6.0)
    gk = design["loads"]["g_k"]
    qk = design["loads"]["q_k"]
    med_load = (1.35 * gk) + (1.50 * qk)
    m_ed = (med_load * (span ** 2)) / 8.0
    v_ed = (med_load * span) / 2.0
    return {
        "q_ed": round(med_load, 2),
        "max_moment_kNm": round(m_ed, 2),
        "shear_v_ed_kN": round(v_ed, 2),
        "status": "PASS" if m_ed < 250 else "REVIEW"
    }

def verify_zoning_laws(design):
    max_cov = ARCH_DOMAINS[design["domain"]]["max_coverage"]
    max_far = ARCH_DOMAINS[design["domain"]]["max_far"]
    cov = design["ground_footprint"] / design["plot_size"]
    far = design["total_gfa"] / design["plot_size"]
    return {
        "coverage": round(cov, 2),
        "coverage_ok": cov <= max_cov,
        "far": round(far, 2),
        "far_ok": far <= max_far,
        "status": "APPROVED" if (cov <= max_cov and far <= max_far) else "VIOLATION"
    }

def compute_detailed_forex_boq(design, rate_overrides=None):
    country = design["country"]
    fx = st.session_state.regional_fx.get(country, REGIONAL_FX_DEFAULTS["Uganda"])
    mult = fx["cost_multiplier"]
    risk = fx["risk_premium"]
    
    gfa = design["total_gfa"]
    substructure = 150.0 * gfa
    superstructure = 420.0 * gfa
    mep_cost = 210.0 * gfa
    finishes = 180.0 * gfa
    
    raw_total_usd = substructure + superstructure + mep_cost + finishes
    total_usd = raw_total_usd * mult * (1 + risk)
    
    return {
        "substructure": round(substructure, 2),
        "superstructure": round(superstructure, 2),
        "mep_services": round(mep_cost, 2),
        "finishes": round(finishes, 2),
        "total_usd": round(total_usd, 2),
        "total_local": round(total_usd * fx["rate_to_usd"], 2),
        "local_currency": fx["currency"],
        "symbol": fx["symbol"],
        "rate_used": fx["rate_to_usd"]
    }

def generate_building_model(domain, btype, floors, baths, country, material_frame, plot_size,
                           soil_type, g_k, q_k, steel_section, seismic_zone, wind_zone, username):
    rooms = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Dining"]
    span = 6.0
    ground_footprint = plot_size * 0.4
    nx, ny = 3, 2
    layout_grid = [rooms[:3], rooms[3:]]
    total_gfa = ground_footprint * floors
    
    design = {
        "id": f"PRJ-2026-{random.randint(100, 999)}",
        "username": username,
        "domain": domain,
        "type": btype,
        "floors": floors,
        "bathrooms": baths,
        "country": country,
        "material_frame": material_frame,
        "plot_size": plot_size,
        "soil_type": soil_type,
        "ground_footprint": ground_footprint,
        "rooms": rooms,
        "layout": {"grid": layout_grid, "nx": nx, "ny": ny, "span": span},
        "total_gfa": total_gfa,
        "loads": {"g_k": g_k, "q_k": q_k, "steel_section": steel_section, "seismic_zone": seismic_zone, "wind_zone": wind_zone},
        "created": datetime.now().isoformat()
    }
    design["analysis"] = run_eurocode_analysis(design)
    design["mep"] = run_mep_analysis(design)
    design["zoning"] = verify_zoning_laws(design)
    design["boq"] = compute_detailed_forex_boq(design)
    return design

# ------------------------------------------------------------
# SESSION & SIDEBAR AUTHENTICATION
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

st.sidebar.markdown(LOGO_SVG, unsafe_allow_html=True)

if st.session_state["user"] is None:
    st.sidebar.subheader("🔒 Access Control Portal")
    tab_log, tab_reg = st.sidebar.tabs(["Login", "Register"])
    
    with tab_log:
        username = st.text_input("Username", key="l_u")
        password = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In", use_container_width=True):
            ok, role = authenticate_user(username.strip(), password.strip())
            if ok:
                st.session_state["user"] = {"username": username.strip(), "role": role}
                log_system_event("User logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")
                
    with tab_reg:
        r_u = st.text_input("Username", key="r_u")
        r_p = st.text_input("Password", type="password", key="r_p")
        r_r = st.selectbox("Role", ["Architect", "MEP Engineer", "Project Lead", "Viewer"])
        if st.button("Create Account", use_container_width=True):
            ok, msg = register_user(r_u.strip(), r_p.strip(), role=r_r)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    st.stop()
else:
    u = st.session_state["user"]
    st.sidebar.write(f"**Logged in as:** {u['username']}")
    st.sidebar.caption(f"Role: `{u['role']}`")
    if st.sidebar.button("Logout", use_container_width=True):
        log_system_event("User logged out")
        st.session_state["user"] = None
        st.rerun()

current_role = st.session_state["user"]["role"]
can_approve = current_role in ["Admin", "Project Lead"]

# Navigation
nav_options = [
    "📌 Dashboard & Portfolio",
    "📐 Generative Synthesis Lab",
    "⚙️ Eurocode Structural Analysis",
    "⚡ MEP Calculation Engine",
    "📊 BoQ & Forex Budgeting",
    "📦 IFC / BIM Export",
    "🔒 Project Governance & Approvals"
]
if current_role == "Admin":
    nav_options.append("⚙️ User & System Control")

nav_option = st.sidebar.radio("Platform Navigation", nav_options)

# ------------------------------------------------------------
# MODULE 1: DASHBOARD & PORTFOLIO
# ------------------------------------------------------------
if nav_option == "📌 Dashboard & Portfolio":
    st.title("📌 Project Portfolio & System Dashboard")
    st.markdown("Centralized architectural lifecycle dashboard.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Projects", "12", "+2 this month")
    col2.metric("Total Gross Area", "48,500 m²", "+12%")
    col3.metric("Est. Portfolio Value", "$18.4 M", "+5.2%")
    col4.metric("Pending Approvals", "3", "Action Required")

    st.divider()
    st.subheader("Project Inventory")
    
    cols = ["id", "name", "code", "client", "status", "gross_area", "estimated_cost_usd"]
    rows = execute_query("SELECT id, name, code, client, status, gross_area, estimated_cost_usd FROM projects", fetch="all") or []
    df_projects = pd.DataFrame(rows, columns=cols)

    if df_projects.empty:
        execute_query(
            "INSERT INTO projects (name, code, client, status, gross_area, estimated_cost_usd) VALUES (?, ?, ?, ?, ?, ?)",
            ("Civic Commercial Tower", "PRJ-2026-001", "Metropolitan Dev", "Pending Review", 12500.0, 4500000.0)
        )
        st.info("Sample project seeded. Refresh page.")
    else:
        st.dataframe(df_projects, use_container_width=True)

# ------------------------------------------------------------
# MODULE 2: GENERATIVE SYNTHESIS LAB
# ------------------------------------------------------------
elif nav_option == "📐 Generative Synthesis Lab":
    st.title("📐 Generative Synthesis & Space Programming")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Synthesis Parameters")
        country = st.selectbox("Region", list(st.session_state.regional_fx.keys()))
        domain = st.selectbox("Category", list(ARCH_DOMAINS.keys()))
        btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
        plot = st.slider("Plot Size (m²)", 200, 5000, 800, 50)
        floors = st.slider("Storeys", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)
        soil = st.selectbox("Soil Profile", list(SOIL_PROFILES.keys()))
        material = st.selectbox("Structural Frame", ["Concrete EN1992", "Steel EN1993", "Timber EN1995"])
        
        if st.button("Generate Architectural Archetype", type="primary"):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                5.5, 2.5, "UB 254x146x31", "Moderate (PGA=0.15g)", "Moderate (28 m/s)", st.session_state["user"]["username"]
            )
            st.session_state.active_design = design
            execute_query(
                "INSERT INTO projects (name, code, client, status, gross_area, estimated_cost_usd, design_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"{design['type']} Archetype", design['id'], "Internal", "Draft", design['total_gfa'], design['boq']['total_usd'], json.dumps(design))
            )
            st.success("Model generated successfully!")

    with col_b:
        if st.session_state.active_design:
            d = st.session_state.active_design
            st.subheader(f"Archetype Footprint: {d['id']}")
            
            fig = go.Figure()
            fig.add_shape(type="rect", x0=0, y0=0, x1=35, y1=20, line=dict(color="RoyalBlue", width=3), fillcolor="LightSteelBlue", opacity=0.3)
            fig.add_shape(type="rect", x0=12, y0=6, x1=23, y1=14, line=dict(color="Red", width=2), fillcolor="IndianRed", opacity=0.7)
            fig.update_layout(title="Floor Boundary & MEP Core Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.json(d["zoning"])
        else:
            st.info("Configure variables and click generate.")

# ------------------------------------------------------------
# MODULE 3: EUROCODE STRUCTURAL ANALYSIS
# ------------------------------------------------------------
elif nav_option == "⚙️ Eurocode Structural Analysis":
    st.title("⚙️ Eurocode Structural Engineering Engine")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Simply Supported RC Beam Design (EN 1992)")
        span = st.number_input("Span Length L (m)", 2.0, 15.0, 6.0)
        gk = st.number_input("Permanent Load Gk (kN/m)", 1.0, 100.0, 15.0)
        qk = st.number_input("Variable Load Qk (kN/m)", 0.0, 100.0, 10.0)

        med_load = (1.35 * gk) + (1.50 * qk)
        m_ed = (med_load * (span ** 2)) / 8.0
        v_ed = (med_load * span) / 2.0

        st.metric("Design Load ULS (q_ed)", f"{med_load:.2f} kN/m")
        st.metric("Design Bending Moment (M_ed)", f"{m_ed:.2f} kNm")
        st.metric("Design Shear Force (V_ed)", f"{v_ed:.2f} kN")

    with col2:
        st.subheader("3D Isometric Structural Framework")
        fig3d = go.Figure()
        for x in [0, span]:
            for y in [0, 6]:
                fig3d.add_trace(go.Scatter3d(x=[x, x], y=[y, y], z=[0, 3.5], mode='lines', line=dict(color='white', width=6)))
        fig3d.add_trace(go.Scatter3d(x=[0, span], y=[0, 0], z=[3.5, 3.5], mode='lines', line=dict(color='blue', width=8)))
        fig3d.add_trace(go.Scatter3d(x=[0, span], y=[6, 6], z=[3.5, 3.5], mode='lines', line=dict(color='blue', width=8)))
        fig3d.update_layout(scene=dict(xaxis_title='Span X', yaxis_title='Bay Y', zaxis_title='Height Z'), height=400)
        st.plotly_chart(fig3d, use_container_width=True)

# ------------------------------------------------------------
# MODULE 4: MEP CALCULATION ENGINE
# ------------------------------------------------------------
elif nav_option == "⚡ MEP Calculation Engine":
    st.title("⚡ Mechanical, Electrical & Plumbing (MEP) Engine")
    
    mep_tab1, mep_tab2, mep_tab3 = st.tabs(["Mechanical (HVAC)", "Electrical Power", "Plumbing (WSFU)"])
    
    with mep_tab1:
        st.subheader("HVAC Cooling Load Estimator")
        floor_area_m2 = st.number_input("Served Area (m²)", 10.0, 5000.0, 350.0)
        occupants = st.number_input("Occupant Density", 1, 500, 35)
        heat_load = st.slider("Heat Gain Target (W/m²)", 80, 200, 120)
        total_kw = ((floor_area_m2 * heat_load) + (occupants * 100)) / 1000.0
        st.metric("Cooling Capacity Required", f"{total_kw:.2f} kW", f"{total_kw/3.517:.2f} TR")
        
    with mep_tab2:
        st.subheader("Electrical Power Demand")
        lighting = st.number_input("Lighting Load (kW)", 0.0, 500.0, 15.0)
        sockets = st.number_input("Small Power (kW)", 0.0, 500.0, 45.0)
        demand_kw = (lighting + sockets + 40.0) * 0.75
        st.metric("Suggested Transformer Rating", f"{demand_kw / (0.85 * 0.8):.0f} kVA")

    with mep_tab3:
        st.subheader("Plumbing Fixture Unit Sizing")
        wc = st.number_input("Water Closets", 1, 100, 12)
        basin = st.number_input("Wash Basins", 1, 100, 15)
        wsfu = (wc * 5) + (basin * 1.5)
        st.metric("Peak Domestic Flow Rate", f"{np.sqrt(wsfu) * 0.25:.2f} L/s")

# ------------------------------------------------------------
# MODULE 5: BOQ & FOREX BUDGETING
# ------------------------------------------------------------
elif nav_option == "📊 BoQ & Forex Budgeting":
    st.title("📊 Multi-Currency Forex & BoQ Budgeting")
    
    currency = st.selectbox("Select Currency", list(st.session_state.regional_fx.keys()))
    fx_data = st.session_state.regional_fx[currency]
    rate = fx_data["rate_to_usd"]

    boq_data = pd.DataFrame([
        {"Item": "1.0 Substructure", "Base Cost (USD)": 150000.0},
        {"Item": "2.0 Superstructure Concrete & Steel", "Base Cost (USD)": 420000.0},
        {"Item": "3.0 Architectural Facade & Finishes", "Base Cost (USD)": 280000.0},
        {"Item": "4.0 MEP Systems & Services", "Base Cost (USD)": 210000.0},
    ])

    boq_data[f"Total ({fx_data['currency']})"] = boq_data["Base Cost (USD)"] * rate
    st.table(boq_data.style.format({"Base Cost (USD)": "${:,.2f}", f"Total ({fx_data['currency']})": f"{fx_data['symbol']} {{:,.2f}}"}))

# ------------------------------------------------------------
# MODULE 6: IFC / BIM EXPORT
# ------------------------------------------------------------
elif nav_option == "📦 IFC / BIM Export":
    st.title("📦 Building Information Modeling (BIM) IFC Export")
    
    ifc_payload = {
        "IfcProject": {
            "Name": "Imagine Architectural Building",
            "Units": "METRIC",
            "Storeys": 6,
            "Elements": [
                {"Type": "IfcBeam", "Material": "C30/37 Concrete", "Span_m": 6.0},
                {"Type": "IfcColumn", "Material": "C35/45 Concrete", "Height_m": 3.5}
            ]
        }
    }
    json_str = json.dumps(ifc_payload, indent=4)
    st.code(json_str, language="json")
    st.download_button("📥 Download IFC Metadata (JSON)", data=json_str, file_name="imagine_bim.json", mime="application/json")

# ------------------------------------------------------------
# MODULE 7: PROJECT GOVERNANCE & APPROVALS
# ------------------------------------------------------------
elif nav_option == "🔒 Project Governance & Approvals":
    st.title("🔒 Role-Based Governance & Sign-off")
    st.write(f"Active User Role: **`{current_role}`**")

    if not can_approve:
        st.warning("⚠️ Access Restricted: Only `Admin` or `Project Lead` roles can execute stage-gate approvals.")
    else:
        st.success("✅ Sign-off Authorization Verified.")
        with st.form("approval_form"):
            project_code = st.text_input("Project Code", "PRJ-2026-001")
            new_status = st.selectbox("Stage Action", ["Approved", "Returned for Revision", "Rejected"])
            remarks = st.text_area("Governance Remarks")
            if st.form_submit_button("Submit Sign-off"):
                execute_query("UPDATE projects SET status = ? WHERE code = ?", (new_status, project_code))
                st.success(f"Project {project_code} updated to '{new_status}'.")

# ------------------------------------------------------------
# MODULE 8: USER & SYSTEM CONTROL (ADMIN ONLY)
# ------------------------------------------------------------
elif nav_option == "⚙️ User & System Control":
    st.title("⚙️ System Control & Directory")
    if current_role != "Admin":
        st.error("Access Restricted")
    else:
        users = execute_query("SELECT id, username, role, email, created_at FROM users", fetch="all") or []
        st.dataframe(pd.DataFrame(users, columns=["ID", "Username", "Role", "Email", "Created At"]), use_container_width=True)
