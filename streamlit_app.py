# =========================================================
# IMAGINE – Architectural Intellect, MEP Engine & Forex Suite
# Combined Enterprise Edition | Eurocode, MEP Passport & BIM
# =========================================================

import os
import json
import uuid
import math
import hashlib
import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import plotly.express as px
import plotly.graph_objects as go

# Optional PostgreSQL support
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# ------------------------------------------------------------
# 1. PAGE CONFIG & MODERN CSS STYLING
# ------------------------------------------------------------
st.set_page_config(
    page_title="Imagine | Architectural & MEP Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_theme():
    st.markdown("""
    <style>
    /* Dark Modern Theme Base */
    .stApp {
        background-color: #0b0e14;
        color: #d1d5db;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stSidebar {
        background-color: #111622;
        border-right: 1px solid #1f293d;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #f3f4f6 !important;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Improved Glassmorphism Login Container */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .login-card {
        background: rgba(17, 22, 34, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(88, 166, 255, 0.05);
        max-width: 460px;
        width: 100%;
        margin: 0 auto;
    }
    .login-header-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .login-header-subtitle {
        color: #9ca3af;
        font-size: 0.88rem;
        text-align: center;
        margin-bottom: 1.8rem;
    }
    
    /* Demo Badge Box */
    .demo-badge-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1.5rem;
        font-size: 0.82rem;
        color: #93c5fd;
        line-height: 1.5;
    }
    .demo-badge-box code {
        background: rgba(15, 23, 42, 0.8);
        color: #38bdf8;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
    }

    /* Metric Cards */
    .stMetric {
        background: rgba(17, 22, 34, 0.8) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        border: 1px solid #1f293d !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #1f293d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        color: #9ca3af;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(31, 41, 55, 0.5) !important;
        color: #60a5fa !important;
        border-bottom: 2px solid #60a5fa !important;
    }
    
    /* Custom Primary Buttons */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: linear-gradient(135deg, #1f293d 0%, #111827 100%);
        color: #f3f4f6;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #60a5fa;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(96, 165, 250, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_theme()

# ------------------------------------------------------------
# 2. LOGO VECTOR GRAPHIC
# ------------------------------------------------------------
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80" width="240" height="64">
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60a5fa"/>
      <stop offset="50%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#f472b6"/>
    </linearGradient>
  </defs>
  <g transform="translate(150, 28)">
    <!-- Architectural compass and structural crosshair -->
    <circle cx="0" cy="0" r="18" stroke="url(#brandGrad)" stroke-width="2" fill="none"/>
    <line x1="0" y1="-16" x2="0" y2="16" stroke="url(#brandGrad)" stroke-width="1.5" stroke-dasharray="2,2"/>
    <line x1="-16" y1="0" x2="16" y2="0" stroke="url(#brandGrad)" stroke-width="1.5" stroke-dasharray="2,2"/>
    <polygon points="0,-14 3,0 0,14 -3,0" fill="url(#brandGrad)"/>
    <circle cx="0" cy="0" r="3" fill="#0b0e14"/>
  </g>
  <text x="150" y="68" text-anchor="middle"
        font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="22"
        fill="url(#brandGrad)" letter-spacing="5">IMAGINE</text>
</svg>
"""

# ------------------------------------------------------------
# 3. DATABASE ENGINE & AUTHENTICATION
# ------------------------------------------------------------
USER_DB = Path("imagine_app.db")

def get_db_connection():
    pg_url = os.environ.get("DATABASE_URL")
    if HAS_POSTGRES and pg_url:
        try:
            conn = psycopg2.connect(pg_url)
            return conn, "postgres"
        except Exception:
            pass
    conn = sqlite3.connect(USER_DB, check_same_thread=False)
    return conn, "sqlite"

def hash_password(password: str, salt: str = "") -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_database():
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password_hash VARCHAR(256) NOT NULL,
        salt VARCHAR(64) NOT NULL DEFAULT 'legacy_salt',
        role VARCHAR(20) DEFAULT 'user',
        email VARCHAR(100) DEFAULT ''
    );
    """)
    
    # Designs & MEP Projects Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS designs (
        id VARCHAR(50) PRIMARY KEY,
        username VARCHAR(50),
        data_json TEXT NOT NULL,
        created_at VARCHAR(50)
    );
    """)

    # System Audit Logs
    c.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp VARCHAR(50),
        username VARCHAR(50),
        action VARCHAR(255)
    );
    """ if db_type == "sqlite" else """
    CREATE TABLE IF NOT EXISTS system_logs (
        id SERIAL PRIMARY KEY,
        timestamp VARCHAR(50),
        username VARCHAR(50),
        action VARCHAR(255)
    );
    """)
    conn.commit()

    # Seed Default Users if empty
    c.execute("SELECT COUNT(*) FROM users;")
    if c.fetchone()[0] == 0:
        sample_users = [
            ("admin", "admin123", "admin", "admin@imagine.arch"),
            ("engineer", "engineer123", "engineer", "engineer@imagine.arch"),
            ("architect", "architect123", "architect", "architect@imagine.arch")
        ]
        for u, p, r, e in sample_users:
            s = uuid.uuid4().hex
            h = hash_password(p, s)
            if db_type == "sqlite":
                c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?);", (u, h, s, r, e))
            else:
                c.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s);", (u, h, s, r, e))
        conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    q = "SELECT password_hash, salt, role FROM users WHERE username=?;" if db_type == "sqlite" else "SELECT password_hash, salt, role FROM users WHERE username=%s;"
    c.execute(q, (username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        db_hash, salt, role = row
        if hash_password(password, salt) == db_hash or hash_password(password, "") == db_hash:
            return True, role
    return False, None

def register_user(username, password, email="", role="architect"):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    try:
        salt = uuid.uuid4().hex
        pwd_hash = hash_password(password, salt)
        q = "INSERT INTO users VALUES (?, ?, ?, ?, ?);" if db_type == "sqlite" else "INSERT INTO users VALUES (%s, %s, %s, %s, %s);"
        c.execute(q, (username, pwd_hash, salt, role, email))
        conn.commit()
        return True, f"Account '{username}' created successfully."
    except Exception as e:
        return False, "Username already exists or database error."
    finally:
        conn.close()

def log_event(msg):
    username = st.session_state.get("username", "system")
    conn, db_type = get_db_connection()
    c = conn.cursor()
    now_str = datetime.now().isoformat()
    q = "INSERT INTO system_logs (timestamp, username, action) VALUES (?, ?, ?);" if db_type == "sqlite" else "INSERT INTO system_logs (timestamp, username, action) VALUES (%s, %s, %s);"
    try:
        c.execute(q, (now_str, username, msg))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

init_database()

# ------------------------------------------------------------
# 4. SESSION STATE MANAGEMENT
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

REGIONAL_FX_DEFAULTS = {
    "Kenya": {"currency": "KES", "rate_to_usd": 129.49, "symbol": "KSh", "cost_multiplier": 1.00, "risk_premium": 0.02},
    "Uganda": {"currency": "UGX", "rate_to_usd": 3665.20, "symbol": "USh", "cost_multiplier": 0.95, "risk_premium": 0.03},
    "Tanzania": {"currency": "TZS", "rate_to_usd": 2625.00, "symbol": "TSh", "cost_multiplier": 0.98, "risk_premium": 0.025},
    "South Sudan": {"currency": "SSP", "rate_to_usd": 4626.40, "symbol": "SSP", "cost_multiplier": 1.35, "risk_premium": 0.08}
}

if "regional_fx" not in st.session_state:
    st.session_state.regional_fx = REGIONAL_FX_DEFAULTS.copy()

if "memory" not in st.session_state:
    st.session_state.memory = {"designs": [], "logs": []}

if "active_design" not in st.session_state:
    st.session_state.active_design = None

# ------------------------------------------------------------
# 5. IMPROVED LOGIN & SIGN UP WINDOW
# ------------------------------------------------------------
def render_improved_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;">' + LOGO_SVG + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-header-title">Imagine Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-header-subtitle">Architectural Intellect, Eurocode & MEP Passport Engine</div>', unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔒 Sign In", "📝 Create Account"])
    
    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Username", placeholder="e.g. admin, engineer, architect")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            submit_btn = st.form_submit_button("Sign In to Engine", use_container_width=True)
            
            if submit_btn:
                if not u or not p:
                    st.error("Please provide both username and password.")
                else:
                    ok, role = authenticate_user(u.strip(), p.strip())
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.username = u.strip()
                        st.session_state.role = role
                        log_event("User logged in successfully")
                        st.success(f"Welcome back, {u}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
                        
    with tab_signup:
        with st.form("signup_form", clear_on_submit=False):
            new_u = st.text_input("Choose Username", placeholder="e.g. j_doe")
            new_p = st.text_input("Create Password", type="password", placeholder="••••••••")
            new_e = st.text_input("Email (optional)", placeholder="designer@studio.com")
            new_r = st.selectbox("Role", ["architect", "engineer", "admin", "user"])
            reg_btn = st.form_submit_button("Create New Account", use_container_width=True)
            
            if reg_btn:
                if not new_u or not new_p:
                    st.error("Username and password are required.")
                else:
                    ok, msg = register_user(new_u.strip(), new_p.strip(), new_e.strip(), new_r)
                    if ok:
                        st.success(msg + " You may now sign in.")
                    else:
                        st.error(msg)
                        
    st.markdown("""
    <div class="demo-badge-box">
        <b>🔑 Demo Access Accounts:</b><br>
        • <b>Admin:</b> <code>admin</code> / <code>admin123</code><br>
        • <b>Engineer:</b> <code>engineer</code> / <code>engineer123</code><br>
        • <b>Architect:</b> <code>architect</code> / <code>architect123</code>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_improved_login()
    st.stop()

def logout():
    log_event("User logged out")
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.active_design = None
    st.rerun()

# ------------------------------------------------------------
# 6. ARCHITECTURAL & MEP DOMAINS DATA
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# 7. MEP PASSPORT CALCULATIONS
# ------------------------------------------------------------
def calculate_mep_passport(floors, total_gfa, occupancy_type):
    area_per_floor = total_gfa / max(1, floors)
    factors = {
        "Residential": {"cooling_w_sqm": 110, "elec_va_sqm": 60, "water_l_person": 150, "occ_sqm_person": 20},
        "Commercial": {"cooling_w_sqm": 140, "elec_va_sqm": 90, "water_l_person": 50, "occ_sqm_person": 10},
        "Industrial": {"cooling_w_sqm": 80, "elec_va_sqm": 120, "water_l_person": 30, "occ_sqm_person": 30},
    }.get(occupancy_type, {"cooling_w_sqm": 120, "elec_va_sqm": 80, "water_l_person": 60, "occ_sqm_person": 15})
    
    total_occ = max(1, int(total_gfa / factors["occ_sqm_person"]))
    cooling_kw = (total_gfa * factors["cooling_w_sqm"]) / 1000.0
    elec_kva = (total_gfa * factors["elec_va_sqm"]) / 1000.0
    water_daily = total_occ * factors["water_l_person"]
    
    return {
        "mech_hvac": {
            "cooling_load_kw": round(cooling_kw, 2),
            "cooling_tons": round(cooling_kw / 3.517, 2),
            "ventilation_rate_cfm": round(total_occ * 20, 0),
            "primary_units_count": max(1, math.ceil(cooling_kw / 150.0))
        },
        "elec_power": {
            "connected_load_kva": round(elec_kva, 2),
            "backup_generator_kva": round(elec_kva * 0.85, 2),
            "solar_pv_kwp": round(min(total_gfa * 0.12, elec_kva * 0.35), 2)
        },
        "plumb_water": {
            "daily_demand_liters": round(water_daily, 0),
            "storage_tank_liters": round(water_daily * 2.2, 0),
            "estimated_occupants": total_occ,
            "booster_pumps": max(1, math.ceil(floors / 4))
        }
    }

# ------------------------------------------------------------
# 8. CORE GENERATIVE & STRUCTURAL CALCULATIONS
# ------------------------------------------------------------
def generate_intelligent_layout(rooms, nx, ny, span):
    grid = np.full((ny, nx), "Corridor", dtype=object)
    indices = [(i, j) for i in range(ny) for j in range(nx)]
    np.random.shuffle(indices)
    for idx, room in enumerate(rooms):
        if idx >= len(indices):
            break
        i, j = indices[idx]
        grid[i, j] = room
    return grid.tolist()

def run_eurocode_analysis(design):
    span = design.get("layout", {}).get("span", 5.0)
    gk = design["loads"]["g_k"]
    qk = design["loads"]["q_k"]
    seismic = SEISMIC_ZONES.get(design["loads"]["seismic_zone"], {"PGA": 0.15})
    wind_speed = WIND_ZONES.get(design["loads"]["wind_zone"], 28)
    soil = SOIL_PROFILES.get(design["soil_type"], {})
    floors = design["floors"]
    
    # EN 1990 ULS combination
    uls_design_load = (1.35 * gk) + (1.50 * qk)
    M_ed = uls_design_load * span**2 / 8.0
    base_pressure = (gk + qk) * floors * 1.5
    footing_width = math.sqrt(base_pressure / max(soil.get("cohesion", 20), 1))
    wind_force = 0.613 * wind_speed**2 * span * floors / 1000.0
    drift = wind_force * floors**3 / 2000.0
    
    return {
        "uls_combination_kNm2": round(uls_design_load, 2),
        "max_moment_kNm": round(M_ed, 2),
        "footing_width_m": round(footing_width, 2),
        "wind_base_shear_kN": round(wind_force, 2),
        "drift_mm": round(drift, 2),
        "seismic_base_shear_kN": round(seismic["PGA"] * floors * 100 * span * 5, 2),
        "status": "PASS" if M_ed < 120 else "REVIEW"
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
    fx = st.session_state.regional_fx[country]
    mult = fx["cost_multiplier"]
    risk = fx["risk_premium"]
    base_rates = {
        "Reinforced Concrete (Eurocode 2)": 350,
        "Structural Steel Profile (Eurocode 3)": 400,
        "Timber Profile (Eurocode 5)": 280
    }
    if rate_overrides is None:
        rate_overrides = {}
    rate_per_m2 = rate_overrides.get(design["material_frame"], base_rates.get(design["material_frame"], 350))
    gfa = design["total_gfa"]
    
    substructure = 0.15 * rate_per_m2 * gfa
    superstructure = 0.65 * rate_per_m2 * gfa
    mep_package = 0.12 * rate_per_m2 * gfa
    finishes = 0.08 * rate_per_m2 * gfa
    
    total_usd = (substructure + superstructure + mep_package + finishes) * mult * (1 + risk)
    return {
        "substructure": round(substructure, 2),
        "superstructure": round(superstructure, 2),
        "mep_package": round(mep_package, 2),
        "finishes": round(finishes, 2),
        "total_usd": round(total_usd, 2),
        "total_local": round(total_usd * fx["rate_to_usd"], 2),
        "local_currency": fx["currency"],
        "symbol": fx["symbol"],
        "rate_used": fx["rate_to_usd"]
    }

def generate_building_model(domain, btype, floors, baths, country, material_frame, plot_size,
                           soil_type, g_k, q_k, steel_section, seismic_zone, wind_zone, username):
    room_map = {
        "Luxury Villa": ["Bedroom", "Bedroom", "Bedroom", "Living Room", "Kitchen", "Bathroom", "Dining", "Office"],
        "Modern Apartment": ["Living Room", "Bedroom", "Kitchen", "Bathroom"],
        "Townhouse Studio": ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Corridor"],
        "Corporate Hub Block": ["Office", "Office", "Office", "Corridor", "Bathroom"],
        "Boutique Retail Space": ["Living Room", "Corridor", "Bathroom"],
        "Medical Clinic Center": ["Office", "Office", "Corridor", "Bathroom"],
        "Distribution Depot": ["Garage", "Garage", "Office", "Corridor"],
        "Heavy Machinery Plant Warehouse": ["Garage", "Garage", "Corridor"]
    }
    rooms = room_map.get(btype, ["Living Room", "Bedroom", "Kitchen", "Bathroom"])
    rooms.extend(["Bathroom"] * max(0, baths - rooms.count("Bathroom")))
    span = 5.0
    ground_footprint = plot_size * 0.4
    bay_area = span * span
    total_bays = max(2, math.ceil(ground_footprint / bay_area))
    nx = max(2, math.ceil(math.sqrt(total_bays)))
    ny = max(2, math.ceil(total_bays / nx))
    layout_grid = generate_intelligent_layout(rooms, nx, ny, span)
    total_gfa = ground_footprint * floors
    doors = max(1, len(rooms) * 2)
    windows = max(2, len(rooms) * 3)
    
    design = {
        "id": f"IMG-{str(uuid.uuid4())[:6].upper()}",
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
        "doors": doors,
        "windows": windows,
        "loads": {
            "g_k": g_k,
            "q_k": q_k,
            "steel_section": steel_section,
            "seismic_zone": seismic_zone,
            "wind_zone": wind_zone
        },
        "created": datetime.now().isoformat()
    }
    
    design["analysis"] = run_eurocode_analysis(design)
    design["zoning"] = verify_zoning_laws(design)
    design["mep"] = calculate_mep_passport(floors, total_gfa, domain)
    design["boq"] = compute_detailed_forex_boq(design)
    return design

def refresh_forex_rates():
    base = {"Kenya": 129.49, "Uganda": 3665.20, "Tanzania": 2625.00, "South Sudan": 4626.40}
    for country, rate in base.items():
        new_rate = rate * random.uniform(0.98, 1.02)
        st.session_state.regional_fx[country]["rate_to_usd"] = round(new_rate, 2)
    log_event("Simulated live Forex market fluctuations")

# ------------------------------------------------------------
# 9. 2D, 3D & BIM VISUALIZATION ENGINES
# ------------------------------------------------------------
def draw_2d_blueprint(design, overlay_design=None):
    layout = design["layout"]["grid"]
    nx = design["layout"]["nx"]
    ny = design["layout"]["ny"]
    fig, ax = plt.subplots(figsize=(8, 8 * ny / nx if nx > 0 else 8))
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_aspect('equal')
    ax.axis('off')
    
    for i in range(ny):
        for j in range(nx):
            room = layout[i][j]
            color = ROOM_COLORS.get(room, "#94a3b8")
            rect = mpatches.Rectangle((j, ny - 1 - i), 1, 1, linewidth=2, edgecolor='white',
                                     facecolor=color, alpha=0.85)
            ax.add_patch(rect)
            ax.text(j + 0.5, ny - 1 - i + 0.5, room[:9], ha='center', va='center',
                    fontsize=7, color='black', weight='bold')
            
    if overlay_design:
        overlay = overlay_design["layout"]["grid"]
        ony = min(ny, overlay_design["layout"]["ny"])
        onx = min(nx, overlay_design["layout"]["nx"])
        for i in range(ony):
            for j in range(onx):
                room = overlay[i][j]
                color = ROOM_COLORS.get(room, "#94a3b8")
                rect = mpatches.Rectangle((j, ny - 1 - i), 1, 1, linewidth=1, edgecolor='red',
                                         facecolor=color, alpha=0.3, hatch='//')
                ax.add_patch(rect)
                
    ax.annotate('N', xy=(0.5, ny + 0.2), fontsize=14, color='white', ha='center',
                arrowprops=dict(facecolor='white', shrink=0.05))
    
    fig.patch.set_facecolor('#0b0e14')
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_3d_isometric_view(design, drift_factor=0):
    layout = design["layout"]["grid"]
    ny = len(layout)
    nx = len(layout[0]) if layout else 0
    floors = design["floors"]
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('none')
    fig.patch.set_facecolor('#0b0e14')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    
    for f in range(floors):
        z = f * 3.0
        offset_x = drift_factor * math.sin(z / 2)
        for i in range(ny):
            for j in range(nx):
                room = layout[i][j]
                color = ROOM_COLORS.get(room, "#94a3b8")
                x = [j + offset_x, j + 1 + offset_x, j + 1 + offset_x, j + offset_x]
                y = [i, i, i + 1, i + 1]
                zz = [z] * 4
                verts = [list(zip(x, y, zz))]
                slab = Poly3DCollection(verts, facecolors=color, alpha=0.5, edgecolors='white')
                ax.add_collection3d(slab)
                for (cx, cy) in [(j + offset_x, i), (j + 1 + offset_x, i), (j + 1 + offset_x, i + 1), (j + offset_x, i + 1)]:
                    ax.plot([cx, cx], [cy, cy], [z, z + 3], color='white', linewidth=0.5)
                    
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_zlim(0, floors * 3)
    ax.axis('off')
    st.pyplot(fig)

def render_plotly_3d_massing(floors, area_per_floor):
    side = np.sqrt(max(10.0, area_per_floor))
    fig = go.Figure()
    for f in range(floors):
        z_bottom = f * 3.5
        z_top = z_bottom + 3.2
        fig.add_trace(go.Mesh3d(
            x=[0, side, side, 0, 0, side, side, 0],
            y=[0, 0, side, side, 0, 0, side, side],
            z=[z_bottom, z_bottom, z_bottom, z_bottom, z_top, z_top, z_top, z_top],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.75,
            name=f"Storey {f+1}",
            showscale=False
        ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Width (m)', backgroundcolor='#0b0e14', gridcolor='#1f293d'),
            yaxis=dict(title='Length (m)', backgroundcolor='#0b0e14', gridcolor='#1f293d'),
            zaxis=dict(title='Height (m)', backgroundcolor='#0b0e14', gridcolor='#1f293d')
        ),
        margin=dict(l=0, r=0, b=0, t=20),
        paper_bgcolor='#0b0e14',
        plot_bgcolor='#0b0e14',
        template="plotly_dark",
        height=450
    )
    return fig

def generate_ifc_json(design):
    grid = design["layout"]["grid"]
    nx = design["layout"]["nx"]
    ny = design["layout"]["ny"]
    span = design["layout"]["span"]
    floors = design["floors"]
    elements = []
    
    for f in range(floors):
        for i in range(ny):
            for j in range(nx):
                room = grid[i][j]
                for (x1, y1), (x2, y2) in [((j, i), (j + 1, i)), ((j + 1, i), (j + 1, i + 1)), ((j, i + 1), (j + 1, i + 1)), ((j, i), (j, i + 1))]:
                    wall = {
                        "type": "IfcWall",
                        "name": f"Wall_F{f}_R{i}{j}",
                        "room": room,
                        "coordinates": {"start": {"x": x1 * span, "y": y1 * span, "z": f * 3}, "end": {"x": x2 * span, "y": y2 * span, "z": f * 3}},
                        "height": 3
                    }
                    elements.append(wall)
                slab = {
                    "type": "IfcSlab",
                    "name": f"Slab_F{f}_R{i}{j}",
                    "coordinates": {"x": j * span, "y": i * span, "z": f * 3},
                    "width": span,
                    "depth": span
                }
                elements.append(slab)
                
    # Add MEP Bim Elements
    elements.append({"type": "IfcDistributionControlElement", "category": "Mechanical HVAC", "payload": design.get("mep", {}).get("mech_hvac", {})})
    elements.append({"type": "IfcElectricDistributionPoint", "category": "Electrical Power", "payload": design.get("mep", {}).get("elec_power", {})})
    elements.append({"type": "IfcTank", "category": "Plumbing System", "payload": design.get("mep", {}).get("plumb_water", {})})
    
    return {"project_id": f"IMG_{design['id']}", "schema": "IFC4_ADD2", "elements": elements}

# ------------------------------------------------------------
# 10. SIDEBAR NAVIGATION & CONFIGURATION MATRIX
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#9ca3af; margin-bottom:12px;'>User: <b>{st.session_state.username}</b> (<i>{st.session_state.role}</i>)</div>", unsafe_allow_html=True)
    
    nav = st.pills("Workspace Mode", ["Control Hub", "Synthesis Lab"], default="Control Hub")
    st.markdown("---")

    if st.session_state.role in ["admin", "engineer"]:
        with st.expander("🌐 Regional Forex Controls"):
            st.caption("Live Rates against USD:")
            for c_name, fx in st.session_state.regional_fx.items():
                st.write(f"• **{c_name}**: {fx['symbol']} {fx['rate_to_usd']:,.2f}")
            if st.button("Simulate Market Movement"):
                refresh_forex_rates()
                st.success("Rates updated!")
                st.rerun()

    with st.expander("🏗️ Configuration Matrix", expanded=True):
        country = st.selectbox("Region / Country", list(st.session_state.regional_fx.keys()))
        domain = st.selectbox("Category", list(ARCH_DOMAINS.keys()))
        btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
        plot = st.slider("Plot Size (m²)", 200, 5000, 800, 50)
        floors = st.slider("Storeys / Floors", 1, 14, 4)
        baths = st.slider("Bathrooms", 1, 10, 2)
        soil = st.selectbox("Soil Profile", list(SOIL_PROFILES.keys()))
        material = st.pills("Framing System", [
            "Reinforced Concrete (Eurocode 2)",
            "Structural Steel Profile (Eurocode 3)",
            "Timber Profile (Eurocode 5)"
        ], default="Reinforced Concrete (Eurocode 2)")
        
        g_k = st.slider("Permanent Load Gk (kN/m²)", 2.0, 8.0, 4.5, 0.5)
        default_q = 2.5 if domain == "Residential" else (4.0 if domain == "Commercial" else 6.5)
        q_k = st.slider("Imposed Load Qk (kN/m²)", 1.0, 10.0, default_q, 0.5)
        steel = st.selectbox("Steel Section", [
            "UB 254x146x31", "UB 305x165x40", "UC 254x254x73", "UC 305x305x97"
        ]) if "Steel" in material else None
        seismic = st.selectbox("Seismic Zone", list(SEISMIC_ZONES.keys()), index=1)
        wind = st.selectbox("Wind Zone", list(WIND_ZONES.keys()), index=1)

    exec_trigger = st.button("🚀 Execute Synthesis Generation", type="primary", use_container_width=True)
    
    st.markdown("---")
    if st.button("Log Out", use_container_width=True):
        logout()

# ------------------------------------------------------------
# 11. MAIN WORKSPACE CONTENT
# ------------------------------------------------------------
if nav == "Control Hub":
    st.title("🏛️ Regional Intelligence & Project Portfolio")
    st.caption("Live financial telemetry, project portfolio tracking, and system telemetry.")
    
    # Forex Telemetry Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kenya (KES)", f"KSh {st.session_state.regional_fx['Kenya']['rate_to_usd']:,.2f}")
    col2.metric("Uganda (UGX)", f"USh {st.session_state.regional_fx['Uganda']['rate_to_usd']:,.2f}")
    col3.metric("Tanzania (TZS)", f"TSh {st.session_state.regional_fx['Tanzania']['rate_to_usd']:,.2f}")
    col4.metric("South Sudan (SSP)", f"SSP {st.session_state.regional_fx['South Sudan']['rate_to_usd']:,.2f}")
    
    st.markdown("---")
    
    # User Project Memory
    my_designs = [d for d in st.session_state.memory["designs"] if d.get("username") == st.session_state.username]
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Workspace Portfolio")
        st.metric("My Synthesized Archetypes", len(my_designs))
        if my_designs:
            selected_idx = st.selectbox(
                "Inspect Saved Design",
                range(len(my_designs)),
                format_func=lambda i: f"{my_designs[i]['id']} — {my_designs[i]['type']}"
            )
            d_sel = my_designs[selected_idx]
            st.markdown(f"""
            <div class="metric-card">
                <h4>{d_sel['id']} ({d_sel['type']})</h4>
                <p><b>Domain:</b> {d_sel['domain']}</p>
                <p><b>Location:</b> {d_sel['country']}</p>
                <p><b>Floors:</b> {d_sel['floors']} Storeys</p>
                <p><b>Gross Area:</b> {d_sel['total_gfa']:,.0f} m²</p>
                <p><b>Total Cost:</b> ${d_sel['boq']['total_usd']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No synthesized designs found. Head to 'Synthesis Lab' to generate your first archetype.")

    with col_b:
        st.subheader("3D Massing & Spatial Envelope Preview")
        if my_designs and 'd_sel' in locals():
            fig_3d = render_plotly_3d_massing(d_sel["floors"], d_sel["ground_footprint"])
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            fig_demo = render_plotly_3d_massing(4, 320.0)
            st.plotly_chart(fig_demo, use_container_width=True)

elif nav == "Synthesis Lab":
    st.title("⚡ Generative Architectural & MEP Synthesis")
    
    if exec_trigger:
        with st.spinner("Synthesizing geometry, Eurocode physics & MEP Passport..."):
            new_design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            st.session_state.active_design = new_design
            st.session_state.memory["designs"].append(new_design)
            log_event(f"Generated design archetype {new_design['id']}")
            st.success(f"Archetype {new_design['id']} synthesized successfully!")

    if st.session_state.active_design:
        d = st.session_state.active_design
        
        st.subheader(f"Active Archetype: {d['id']} — {d['type']}")
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric("Region", d["country"])
        m_c2.metric("Gross Area (GFA)", f"{d['total_gfa']:,.0f} m²")
        m_c3.metric("Storeys", d["floors"])
        m_c4.metric("Total Estimate", f"${d['boq']['total_usd']:,.2f}")

        tabs = st.tabs([
            "📐 2D Blueprint", "🧊 3D Structural View", "❄️⚡🚰 MEP Passport",
            "🏗️ Structural Eurocode", "⚖️ Zoning", "📊 BoQ & Forex",
            "📈 Forex Forecast", "🌊 Wind Drift", "🔄 Design Comparison", "💾 BIM Export"
        ])

        with tabs[0]:
            st.markdown("### Interactive 2D Layout")
            st.image(draw_2d_blueprint(d), use_container_width=True)
            layout = d["layout"]["grid"]
            ny, nx = len(layout), len(layout[0])
            st.markdown("##### Swap Room Locations")
            r_c1, r_c2, r_c3 = st.columns(3)
            with r_c1:
                i1 = st.number_input("Row (Room A)", 0, ny-1, 0)
                j1 = st.number_input("Col (Room A)", 0, nx-1, 0)
            with r_c2:
                i2 = st.number_input("Row (Room B)", 0, ny-1, 0)
                j2 = st.number_input("Col (Room B)", 0, nx-1, 0)
            with r_c3:
                st.write("")
                st.write("")
                if st.button("Swap Positions"):
                    layout[i1][j1], layout[i2][j2] = layout[i2][j2], layout[i1][j1]
                    st.success("Rooms updated!")
                    st.rerun()

        with tabs[1]:
            st.markdown("### 3D Structural Wireframe")
            draw_3d_isometric_view(d)

        with tabs[2]:
            st.markdown("### Integrated MEP Passport (Mechanical, Electrical & Plumbing)")
            mep = d.get("mep", calculate_mep_passport(d["floors"], d["total_gfa"], d["domain"]))
            
            mep1, mep2, mep3 = st.columns(3)
            with mep1:
                st.markdown("#### ❄️ Mechanical (HVAC)")
                st.metric("Cooling Capacity", f"{mep['mech_hvac']['cooling_load_kw']} kW", f"{mep['mech_hvac']['cooling_tons']} Tons")
                st.write(f"• **Air Ventilation:** {mep['mech_hvac']['ventilation_rate_cfm']:,} CFM")
                st.write(f"• **Chillers / Plant Units:** {mep['mech_hvac']['primary_units_count']} Primary Units")

            with mep2:
                st.markdown("#### ⚡ Electrical Power")
                st.metric("Connected Load", f"{mep['elec_power']['connected_load_kva']} kVA")
                st.write(f"• **Genset Backup:** {mep['elec_power']['backup_generator_kva']} kVA")
                st.write(f"• **Solar PV Capacity:** {mep['elec_power']['solar_pv_kwp']} kWp")

            with mep3:
                st.markdown("#### 🚰 Plumbing & Water")
                st.metric("Daily Water Demand", f"{mep['plumb_water']['daily_demand_liters']:,} L/day")
                st.write(f"• **Storage Reserve:** {mep['plumb_water']['storage_tank_liters']:,} L")
                st.write(f"• **Booster Pump Sets:** {mep['plumb_water']['booster_pumps']} Sets")
                st.write(f"• **Design Occupancy:** {mep['plumb_water']['estimated_occupants']} Persons")

        with tabs[3]:
            st.markdown("### Eurocode Structural Analysis (EN 1990 / EN 1991 / EN 1992)")
            st.json(d["analysis"])

        with tabs[4]:
            st.markdown("### Urban Zoning Compliance")
            zon = d["zoning"]
            z_c1, z_c2, z_c3 = st.columns(3)
            z_c1.metric("Site Coverage", f"{zon['coverage']*100:.1f}%", f"Max: {ARCH_DOMAINS[d['domain']]['max_coverage']*100:.0f}%")
            z_c2.metric("Floor Area Ratio (FAR)", zon['far'], f"Max: {ARCH_DOMAINS[d['domain']]['max_far']}")
            z_c3.metric("Zoning Status", zon['status'])

        with tabs[5]:
            st.markdown("### Bill of Quantities (BoQ) & Forex Breakdown")
            boq = d["boq"]
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                st.metric("Substructure", f"${boq['substructure']:,.2f}")
                st.metric("Superstructure", f"${boq['superstructure']:,.2f}")
                st.metric("MEP Systems Package", f"${boq['mep_package']:,.2f}")
                st.metric("Finishes", f"${boq['finishes']:,.2f}")
            with b_c2:
                st.metric("Total Estimate (USD)", f"${boq['total_usd']:,.2f}")
                st.metric(f"Total Local ({boq['local_currency']})", f"{boq['symbol']} {boq['total_local']:,.2f}")
                st.caption(f"Conversion Rate: 1 USD = {boq['rate_used']} {boq['local_currency']}")
            
            # Pie Chart
            df_boq = pd.DataFrame({
                "Category": ["Substructure", "Superstructure", "MEP Package", "Finishes"],
                "Cost_USD": [boq['substructure'], boq['superstructure'], boq['mep_package'], boq['finishes']]
            })
            fig_pie = px.pie(df_boq, names="Category", values="Cost_USD", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(template="plotly_dark", height=350, paper_bgcolor='#0b0e14')
            st.plotly_chart(fig_pie, use_container_width=True)

        with tabs[6]:
            st.markdown("### Forex Time-Series Forecast Engine")
            cur = st.selectbox("Forecast Currency", list(st.session_state.regional_fx.keys()), key="fx_cur")
            days = st.slider("Forecast Horizon (Days)", 7, 90, 30)
            base_rate = st.session_state.regional_fx[cur]["rate_to_usd"]
            np.random.seed(42)
            history = base_rate + np.random.normal(0, 0.4, 90).cumsum()
            forecast = [history[-1] + np.random.normal(0, 0.2) for _ in range(days)]
            
            fig_fx, ax_fx = plt.subplots(figsize=(8, 3.5))
            ax_fx.plot(range(-90, 0), history, label="Historical Rate", color="#60a5fa")
            ax_fx.plot(range(0, days), forecast, "o--", label="Forecast Horizon", color="#f472b6")
            ax_fx.set_facecolor('#111622')
            fig_fx.patch.set_facecolor('#0b0e14')
            ax_fx.tick_params(colors='white')
            ax_fx.legend()
            st.pyplot(fig_fx)

        with tabs[7]:
            st.markdown("### Wind Sway & Structural Drift Simulation")
            drift_val = st.slider("Drift Sway Amplitude", 0.0, 1.0, 0.25, 0.05)
            draw_3d_isometric_view(d, drift_factor=drift_val)

        with tabs[8]:
            st.markdown("### Comparative Design Overlay")
            my_list = [ds for ds in st.session_state.memory["designs"] if ds.get("username") == st.session_state.username]
            if len(my_list) < 2:
                st.info("Synthesize at least two designs to run comparison overlays.")
            else:
                idx_a = st.selectbox("Design A", range(len(my_list)), format_func=lambda i: my_list[i]["id"], key="da")
                idx_b = st.selectbox("Design B", range(len(my_list)), format_func=lambda i: my_list[i]["id"], key="db")
                if st.button("Compare Blueprint Overlay"):
                    st.image(draw_2d_blueprint(my_list[idx_a], overlay_design=my_list[idx_b]), use_container_width=True)

        with tabs[9]:
            st.markdown("### Export BIM / IFC JSON Passport")
            ifc_data = generate_ifc_json(d)
            st.download_button(
                "Download IFC4 Schema (JSON)",
                data=json.dumps(ifc_data, indent=2),
                file_name=f"{d['id']}_BIM_Passport.json",
                mime="application/json"
            )
            st.json(ifc_data, expanded=False)
    else:
        st.info("Configure building parameters in the sidebar matrix and execute generation to inspect results.")
