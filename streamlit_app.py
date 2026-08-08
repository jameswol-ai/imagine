# ==============================================================================
# IMAGINE – Architectural Intellect & East African Forex Engine
# v24.0 – Studio Enterprise Edition (PostgreSQL/SQLite Dual DB & Extended MEP)
# ==============================================================================

import streamlit as st
import json, uuid, math, hashlib, random, os
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO, StringIO
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Try importing PostgreSQL connector for production deployments (e.g. Render/Heroku)
try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

import sqlite3

# ------------------------------------------------------------
# PAGE CONFIG & ELEGANT DARK GLASSMORPHISM STYLING
# ------------------------------------------------------------
st.set_page_config(
    page_title="Imagine Studio Enterprise",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main Background & Base Typography */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1a1e29, #0a0c10, #030406);
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .stSidebar {
        background: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Elegant Login Container */
    .login-container {
        max-width: 480px;
        margin: 2.5rem auto 0 auto;
        padding: 2.5rem;
        background: rgba(18, 22, 31, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h2 {
        font-size: 1.5rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        color: #f8fafc !important;
        margin-top: 0.75rem;
        text-transform: uppercase;
    }
    .login-header p {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* Custom Form Fields */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        transition: all 0.2s ease;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
    }

    /* Buttons */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #ffffff;
        font-weight: 600;
        letter-spacing: 0.05em;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
        border: none;
    }

    /* Status Badges */
    .badge-approved {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-review {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-draft {
        background-color: rgba(148, 163, 184, 0.15);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Metrics & Cards */
    .stMetric {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 12px;
        border: 1px solid rgba(255, 255, 255, 0.07);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px 6px 0 0;
        color: #64748b;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# BRANDING LOGO
# ------------------------------------------------------------
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 70" width="220" height="52">
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
  </defs>
  <g transform="translate(30, 35)">
    <circle cx="0" cy="0" r="18" stroke="url(#brandGrad)" stroke-width="2.5" fill="none"/>
    <line x1="-12" y1="0" x2="12" y2="0" stroke="url(#brandGrad)" stroke-width="2"/>
    <line x1="0" y1="-12" x2="0" y2="12" stroke="url(#brandGrad)" stroke-width="2"/>
    <circle cx="0" cy="0" r="4" fill="#38bdf8"/>
  </g>
  <text x="65" y="44" font-family="-apple-system, sans-serif" font-weight="600" font-size="26" fill="#f8fafc" letter-spacing="4">IMAGINE</text>
  <text x="66" y="58" font-family="-apple-system, sans-serif" font-weight="400" font-size="9" fill="#94a3b8" letter-spacing="2">STUDIO ENTERPRISE</text>
</svg>
"""

# ------------------------------------------------------------
# DATABASE LAYER (UNIFIED POSTGRESQL & SQLITE ABSTRACTION)
# ------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
SQLITE_DB = Path("arc_studio_ent.db")

def get_db_connection():
    if DATABASE_URL and HAS_PSYCOPG2:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn, "postgresql"
        except Exception as e:
            st.warning(f"PostgreSQL connection failed, falling back to SQLite: {e}")
    
    conn = sqlite3.connect(SQLITE_DB)
    return conn, "sqlite"

def init_database():
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    if db_type == "postgresql":
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        username VARCHAR(100) PRIMARY KEY,
                        password_hash VARCHAR(256) NOT NULL,
                        salt VARCHAR(64) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user',
                        email VARCHAR(150) DEFAULT ''
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS designs (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(100) NOT NULL,
                        title VARCHAR(150),
                        status VARCHAR(50) DEFAULT 'Draft',
                        data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        username VARCHAR(100),
                        action TEXT
                    )''')
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        email TEXT DEFAULT ''
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS designs (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        title TEXT,
                        status TEXT DEFAULT 'Draft',
                        data TEXT NOT NULL,
                        created_at TEXT,
                        updated_at TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        username TEXT,
                        action TEXT
                    )''')
        
    conn.commit()
    
    # Check default admin user
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    if count == 0:
        salt = uuid.uuid4().hex
        admin_hash = hash_password("admin123", salt)
        if db_type == "postgresql":
            c.execute("INSERT INTO users (username, password_hash, salt, role, email) VALUES (%s,%s,%s,%s,%s)",
                      ("admin", admin_hash, salt, "admin", "admin@arc.studio"))
        else:
            c.execute("INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)",
                      ("admin", admin_hash, salt, "admin", "admin@arc.studio"))
        conn.commit()
        
    conn.close()

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def authenticate_user(username, password):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    
    c.execute(f"SELECT password_hash, salt, role FROM users WHERE username={ph}", (username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        db_hash, salt, role = row
        if hash_password(password, salt) == db_hash:
            return True, role
    return False, None

def register_user(username, password, email="", role="user"):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    
    salt = uuid.uuid4().hex
    pwd_hash = hash_password(password, salt)
    
    try:
        c.execute(f"INSERT INTO users (username, password_hash, salt, role, email) VALUES ({ph},{ph},{ph},{ph},{ph})",
                  (username, pwd_hash, salt, role, email))
        conn.commit()
        return True, f"Account '{username}' successfully registered."
    except Exception as e:
        return False, "Username already exists or registration error."
    finally:
        conn.close()

def log_event(username, action):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    now = datetime.now().isoformat()
    
    if db_type == "postgresql":
        c.execute("INSERT INTO system_logs (timestamp, username, action) VALUES (NOW(), %s, %s)", (username, action))
    else:
        c.execute(f"INSERT INTO system_logs (timestamp, username, action) VALUES ({ph}, {ph}, {ph})", (now, username, action))
        
    conn.commit()
    conn.close()

def save_design_to_db(design):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    
    d_id = design["id"]
    username = design["username"]
    title = f"{design['type']} ({design['country']})"
    status = design.get("status", "Draft")
    json_data = json.dumps(design)
    now = datetime.now().isoformat()
    
    if db_type == "postgresql":
        query = """
        INSERT INTO designs (id, username, title, status, data, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET
            status = EXCLUDED.status,
            data = EXCLUDED.data,
            updated_at = NOW();
        """
        c.execute(query, (d_id, username, title, status, json_data))
    else:
        query = """
        INSERT INTO designs (id, username, title, status, data, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            status = excluded.status,
            data = excluded.data,
            updated_at = excluded.updated_at;
        """
        c.execute(query, (d_id, username, title, status, json_data, now, now))
        
    conn.commit()
    conn.close()

def load_user_designs(username=None, role="user"):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    
    if role in ["admin", "lead_architect"]:
        c.execute("SELECT data FROM designs ORDER BY updated_at DESC")
    else:
        c.execute(f"SELECT data FROM designs WHERE username={ph} ORDER BY updated_at DESC", (username,))
        
    rows = c.fetchall()
    conn.close()
    
    designs = []
    for r in rows:
        data = r[0]
        if isinstance(data, str):
            data = json.loads(data)
        designs.append(ensure_design_compatibility(data))
    return designs

def update_design_status(design_id, new_status):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    ph = "%s" if db_type == "postgresql" else "?"
    
    if db_type == "postgresql":
        c.execute(f"UPDATE designs SET status={ph}, updated_at=NOW() WHERE id={ph}", (new_status, design_id))
    else:
        now = datetime.now().isoformat()
        c.execute(f"UPDATE designs SET status={ph}, updated_at={ph} WHERE id={ph}", (new_status, now, design_id))
        
    conn.commit()
    conn.close()

init_database()

# ------------------------------------------------------------
# SESSION STATE & AUTHENTICATION PORTAL
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="login-header">{LOGO_SVG}<p>Sign in to your enterprise space</p></div>', unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])
        
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("Username", placeholder="e.g. architect", key="l_u")
                p = st.text_input("Password", type="password", placeholder="••••••••", key="l_p")
                submit = st.form_submit_button("Authenticate Studio Access")
                
                if submit:
                    if not u or not p:
                        st.warning("Please enter both username and password.")
                    else:
                        ok, role = authenticate_user(u, p)
                        if ok:
                            st.session_state.authenticated = True
                            st.session_state.username = u
                            st.session_state.role = role
                            log_event(u, "User signed into Studio Enterprise")
                            st.rerun()
                        else:
                            st.error("Invalid credentials provided.")
                            
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                new_u = st.text_input("New Username", placeholder="e.g. j_doe", key="s_u")
                new_p = st.text_input("Choose Password", type="password", placeholder="••••••••", key="s_p")
                new_e = st.text_input("Email Address", placeholder="name@firm.com", key="s_e")
                role_choice = st.selectbox("Role Specialization", ["user", "lead_architect", "mep_engineer", "structural_engineer"])
                register = st.form_submit_button("Register New Account")
                
                if register:
                    if not new_u or not new_p:
                        st.warning("Username and password are required.")
                    else:
                        ok, msg = register_user(new_u, new_p, new_e, role_choice)
                        if ok:
                            st.success(msg + " You can now sign in.")
                        else:
                            st.error(msg)
                            
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_login_portal()
    st.stop()

def logout():
    log_event(st.session_state.username, "User logged out")
    for key in ["authenticated", "username", "role", "active_design"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------------------------------------------------------------
# DOMAIN DATA & REGIONAL FOREX DEFAULTS
# ------------------------------------------------------------
REGIONAL_FX_DEFAULTS = {
    "Kenya": {"currency":"KES","rate_to_usd":129.49,"symbol":"KSh","cost_multiplier":1.0,"risk_premium":0.02},
    "Uganda": {"currency":"UGX","rate_to_usd":3665.20,"symbol":"USh","cost_multiplier":0.95,"risk_premium":0.03},
    "Tanzania": {"currency":"TZS","rate_to_usd":2625.00,"symbol":"TSh","cost_multiplier":0.98,"risk_premium":0.025},
    "South Sudan": {"currency":"SSP","rate_to_usd":4626.40,"symbol":"SSP","cost_multiplier":1.35,"risk_premium":0.08}
}

if "regional_fx" not in st.session_state:
    st.session_state.regional_fx = REGIONAL_FX_DEFAULTS.copy()

ARCH_DOMAINS = {
    "Residential": {"types":["Luxury Villa","Modern Apartment","Townhouse Studio"],"max_coverage":0.5,"max_far":2.5},
    "Commercial": {"types":["Corporate Hub Block","Boutique Retail Space","Medical Clinic Center"],"max_coverage":0.7,"max_far":4.5},
    "Industrial": {"types":["Distribution Depot","Heavy Machinery Plant Warehouse"],"max_coverage":0.6,"max_far":1.8}
}
SOIL_PROFILES = {
    "Kampala Red Lateritic Clay": {"cohesion":35,"friction_angle":12,"unit_weight":18.0},
    "Nairobi Black Cotton Soil": {"cohesion":15,"friction_angle":8,"unit_weight":16.5},
    "Coastal Quartz Sand (Dar)": {"cohesion":0,"friction_angle":32,"unit_weight":19.0},
    "Juba Alluvial Silt Deposit": {"cohesion":20,"friction_angle":15,"unit_weight":17.5}
}
SEISMIC_ZONES = {
    "Low (PGA=0.05g)":{"PGA":0.05,"S":1.0,"importance":1.0},
    "Moderate (PGA=0.15g)":{"PGA":0.15,"S":1.2,"importance":1.0},
    "High (PGA=0.25g)":{"PGA":0.25,"S":1.4,"importance":1.25}
}
WIND_ZONES = {"Low (22 m/s)":22,"Moderate (28 m/s)":28,"High (35 m/s)":35}
ROOM_COLORS = {"Bedroom":"#818cf8","Living Room":"#34d399","Kitchen":"#fbbf24","Bathroom":"#38bdf8","Office":"#f87171","Dining":"#f472b6","Corridor":"#94a3b8","Garage":"#64748b"}

if "active_design" not in st.session_state:
    st.session_state.active_design = None

# ------------------------------------------------------------
# COMPREHENSIVE MEP, STRUCTURAL & SUSTAINABILITY ENGINES
# ------------------------------------------------------------
def run_mep_analysis(design):
    gfa = design["total_gfa"]
    domain = design.get("domain", "Residential")
    baths = design.get("bathrooms", 2)
    floors = design.get("floors", 1)
    
    # 1. Mechanical (HVAC) Sizing Engine
    hvac_densities = {"Residential": 120.0, "Commercial": 160.0, "Industrial": 100.0}
    w_per_m2 = hvac_densities.get(domain, 130.0)
    total_cooling_w = gfa * w_per_m2
    cooling_kw = total_cooling_w / 1000.0
    cooling_tr = cooling_kw / 3.517
    supply_airflow_cfm = cooling_tr * 400.0
    fresh_air_cfm = supply_airflow_cfm * 0.15
    duct_main_area_m2 = (supply_airflow_cfm / 2118.88) / 6.0  # at ~6.0 m/s velocity
    
    # 2. Electrical Power Engine
    elec_densities = {"Residential": 35.0, "Commercial": 65.0, "Industrial": 85.0}
    diversity_factors = {"Residential": 0.70, "Commercial": 0.80, "Industrial": 0.85}
    w_elec_per_m2 = elec_densities.get(domain, 50.0)
    diversity = diversity_factors.get(domain, 0.75)
    pf = 0.85
    
    total_connected_kw = (gfa * w_elec_per_m2) / 1000.0
    connected_kva = total_connected_kw / pf
    max_demand_kva = connected_kva * diversity
    transformer_kva = math.ceil(max_demand_kva * 1.2 / 50.0) * 50
    generator_kva = math.ceil(max_demand_kva * 1.25 / 25.0) * 25
    main_breaker_amps = math.ceil((max_demand_kva * 1000) / (math.sqrt(3) * 415 * pf))
    
    # Solar PV Green Energy Calculation
    pv_capacity_kwp = round(gfa * 0.15 * 0.18, 1) # 15% roof coverage, 18% panel efficiency
    daily_solar_kwh = round(pv_capacity_kwp * 4.8, 1) # ~4.8 peak sun hours in East Africa
    
    # 3. Plumbing, Drainage & Water Management
    occ_factor = {"Residential": 15.0, "Commercial": 10.0, "Industrial": 30.0}.get(domain, 15.0)
    est_occupants = max(2, math.ceil(gfa / occ_factor))
    lpcd = {"Residential": 150.0, "Commercial": 50.0, "Industrial": 35.0}.get(domain, 100.0)
    daily_water_demand_l = est_occupants * lpcd
    storage_tank_m3 = round((daily_water_demand_l * 1.5) / 1000.0, 2)
    wsfu = (baths * 8) + (math.ceil(gfa / 100) * 4)
    dfu = math.ceil(wsfu * 1.25)
    
    # Rainwater Harvesting Potential (East Africa avg ~1000mm rainfall/yr)
    roof_area = design.get("ground_footprint", gfa / floors)
    annual_rainwater_m3 = round(roof_area * 1.00 * 0.85, 1) # 85% runoff coefficient
    
    # Embodied Carbon Estimate
    embodied_carbon_tonnes = round((gfa * 320) / 1000, 1) # ~320 kg CO2/m2 baseline
    
    return {
        "mechanical": {
            "cooling_load_kw": round(cooling_kw, 2),
            "cooling_load_tr": round(cooling_tr, 2),
            "supply_airflow_cfm": round(supply_airflow_cfm, 0),
            "fresh_air_cfm": round(fresh_air_cfm, 0),
            "design_density_w_m2": w_per_m2,
            "main_duct_cross_section_m2": round(duct_main_area_m2, 2)
        },
        "electrical": {
            "connected_load_kw": round(total_connected_kw, 2),
            "connected_load_kva": round(connected_kva, 2),
            "max_demand_kva": round(max_demand_kva, 2),
            "transformer_rating_kva": max(50, transformer_kva),
            "generator_rating_kva": max(30, generator_kva),
            "main_breaker_amps": main_breaker_amps,
            "diversity_factor": diversity,
            "recommended_solar_pv_kwp": pv_capacity_kwp,
            "est_daily_solar_kwh": daily_solar_kwh
        },
        "plumbing": {
            "est_occupants": est_occupants,
            "daily_water_demand_liters": round(daily_water_demand_l, 0),
            "storage_tank_capacity_m3": storage_tank_m3,
            "total_wsfu": wsfu,
            "total_dfu": dfu,
            "annual_rainwater_yield_m3": annual_rainwater_m3
        },
        "sustainability": {
            "embodied_carbon_tonnes_co2": embodied_carbon_tonnes,
            "operational_co2_tonnes_yr": round((total_connected_kw * 0.7 * 8 * 365 * 0.5) / 1000, 1)
        }
    }

def run_eurocode_analysis(design):
    span = design.get("layout", {}).get("span", 5.0)
    gk = design["loads"]["g_k"]
    qk = design["loads"]["q_k"]
    seismic = SEISMIC_ZONES.get(design["loads"]["seismic_zone"], {"PGA":0.15})
    wind_speed = WIND_ZONES.get(design["loads"]["wind_zone"], 28)
    soil = SOIL_PROFILES.get(design["soil_type"], {})
    floors = design["floors"]
    
    # Ultimate Limit State (ULS) Combination
    m_ed = (1.35 * gk + 1.5 * qk) * (span**2) / 8.0
    v_ed = (1.35 * gk + 1.5 * qk) * span / 2.0
    
    # Base Geotechnical & Seismic
    base_pressure = (gk + qk) * floors * 1.5
    footing_width = math.sqrt(base_pressure / max(soil.get("cohesion", 20), 1))
    wind_force = 0.613 * (wind_speed**2) * span * floors / 1000.0
    drift = wind_force * (floors**3) / 2000.0
    seismic_shear = seismic["PGA"] * floors * 100 * span * 5
    
    # Structural Rebar Density Estimate (kg/m3 of concrete)
    rebar_density_kg_m3 = 110.0 if "Concrete" in design.get("material_frame", "") else 0.0
    est_steel_rebar_tonnes = round((design["total_gfa"] * 0.12 * rebar_density_kg_m3) / 1000, 2)
    
    return {
        "uls_design_moment_kNm": round(m_ed, 2),
        "uls_shear_force_kN": round(v_ed, 2),
        "footing_width_m": round(footing_width, 2),
        "wind_base_shear_kN": round(wind_force, 2),
        "drift_mm": round(drift, 2),
        "seismic_base_shear_kN": round(seismic_shear, 2),
        "est_rebar_tonnes": est_steel_rebar_tonnes,
        "status": "PASS" if m_ed < 120 else "REVIEW REQUIRED"
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
        "Timber Profile (Eurocode 5)": 280,
        "HVAC Mechanical Services": 45,
        "Electrical & Lighting Power": 35,
        "Plumbing & Drainage Services": 25
    }
    
    if rate_overrides is None:
        rate_overrides = {}
        
    str_rate = rate_overrides.get(design["material_frame"], base_rates.get(design["material_frame"], 350))
    hvac_rate = rate_overrides.get("HVAC Mechanical Services", base_rates["HVAC Mechanical Services"])
    elec_rate = rate_overrides.get("Electrical & Lighting Power", base_rates["Electrical & Lighting Power"])
    plumb_rate = rate_overrides.get("Plumbing & Drainage Services", base_rates["Plumbing & Drainage Services"])
    
    gfa = design["total_gfa"]
    substructure = 0.15 * str_rate * gfa
    superstructure = 0.70 * str_rate * gfa
    
    hvac_cost = hvac_rate * gfa
    electrical_cost = elec_rate * gfa
    plumbing_cost = plumb_rate * gfa
    total_mep = hvac_cost + electrical_cost + plumbing_cost
    
    finishes = 0.10 * str_rate * gfa
    preliminaries = 0.05 * str_rate * gfa
    
    raw_total_usd = (substructure + superstructure + total_mep + finishes + preliminaries)
    total_usd = raw_total_usd * mult * (1 + risk)
    
    return {
        "substructure": round(substructure, 2),
        "superstructure": round(superstructure, 2),
        "hvac_services": round(hvac_cost, 2),
        "electrical_services": round(electrical_cost, 2),
        "plumbing_services": round(plumbing_cost, 2),
        "total_mep": round(total_mep, 2),
        "finishes": round(finishes, 2),
        "preliminaries": round(preliminaries, 2),
        "total_usd": round(total_usd, 2),
        "total_local": round(total_usd * fx["rate_to_usd"], 2),
        "local_currency": fx["currency"],
        "symbol": fx["symbol"],
        "rate_used": fx["rate_to_usd"]
    }

def generate_intelligent_layout(rooms, nx, ny, span):
    grid = np.full((ny, nx), "Corridor", dtype=object)
    indices = [(i,j) for i in range(ny) for j in range(nx)]
    np.random.shuffle(indices)
    for idx, room in enumerate(rooms):
        if idx >= len(indices): break
        i, j = indices[idx]
        grid[i, j] = room
    return grid.tolist()

def generate_building_model(domain, btype, floors, baths, country, material_frame, plot_size,
                           soil_type, g_k, q_k, steel_section, seismic_zone, wind_zone, username):
    room_map = {
        "Luxury Villa": ["Bedroom","Bedroom","Bedroom","Living Room","Kitchen","Bathroom","Dining","Office"],
        "Modern Apartment": ["Living Room","Bedroom","Kitchen","Bathroom"],
        "Townhouse Studio": ["Living Room","Bedroom","Kitchen","Bathroom","Corridor"],
        "Corporate Hub Block": ["Office","Office","Office","Corridor","Bathroom"],
        "Boutique Retail Space": ["Living Room","Corridor","Bathroom"],
        "Medical Clinic Center": ["Office","Office","Corridor","Bathroom"],
        "Distribution Depot": ["Garage","Garage","Office","Corridor"],
        "Heavy Machinery Plant Warehouse": ["Garage","Garage","Corridor"]
    }
    rooms = room_map.get(btype, ["Living Room","Bedroom","Kitchen","Bathroom"])
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
        "id": str(uuid.uuid4())[:8].upper(),
        "username": username,
        "domain": domain,
        "type": btype,
        "status": "Draft",
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
    design["mep"] = run_mep_analysis(design)
    design["zoning"] = verify_zoning_laws(design)
    design["boq"] = compute_detailed_forex_boq(design)
    return design

def ensure_design_compatibility(design):
    if "layout" not in design:
        span = 5.0
        ground_footprint = design.get("ground_footprint", design.get("plot_size", 500) * 0.4)
        bay_area = span * span
        total_bays = max(2, math.ceil(ground_footprint / bay_area))
        nx = max(2, math.ceil(math.sqrt(total_bays)))
        ny = max(2, math.ceil(total_bays / nx))
        layout_grid = generate_intelligent_layout(design.get("rooms", ["Living Room","Bedroom","Kitchen","Bathroom"]), nx, ny, span)
        design["layout"] = {"grid": layout_grid, "nx": nx, "ny": ny, "span": span}
    if "loads" not in design:
        design["loads"] = {"g_k": 5.5, "q_k": 2.5 if design.get("domain") == "Residential" else (4.0 if design.get("domain") == "Commercial" else 7.5),
                           "steel_section": None, "seismic_zone": "Moderate (PGA=0.15g)", "wind_zone": "Moderate (28 m/s)"}
    if "status" not in design:
        design["status"] = "Draft"
        
    design["mep"] = run_mep_analysis(design)
    design["analysis"] = run_eurocode_analysis(design)
    design["zoning"] = verify_zoning_laws(design)
    design["boq"] = compute_detailed_forex_boq(design)
    return design

def refresh_forex_rates():
    base = {"Kenya": 129.49, "Uganda": 3665.20, "Tanzania": 2625.00, "South Sudan": 4626.40}
    for country, rate in base.items():
        new_rate = rate * random.uniform(0.98, 1.02)
        st.session_state.regional_fx[country]["rate_to_usd"] = round(new_rate, 2)
    log_event(st.session_state.username, "Updated Forex Rates (Market movement simulation)")

# ------------------------------------------------------------
# VISUALIZATION ENGINES
# ------------------------------------------------------------
def draw_2d_blueprint(design, overlay_design=None):
    layout = design["layout"]["grid"]
    nx = design["layout"]["nx"]
    ny = design["layout"]["ny"]
    fig, ax = plt.subplots(figsize=(8, 8*ny/nx if nx>0 else 8))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_aspect('equal')
    ax.axis('off')
    for i in range(ny):
        for j in range(nx):
            room = layout[i][j]
            color = ROOM_COLORS.get(room, "#94a3b8")
            rect = mpatches.Rectangle((j, ny-1-i), 1, 1, linewidth=2, edgecolor='white',
                                     facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            ax.text(j+0.5, ny-1-i+0.5, room[:8], ha='center', va='center',
                    fontsize=8, color='black', weight='bold')
    if overlay_design:
        overlay = overlay_design["layout"]["grid"]
        ony = min(ny, overlay_design["layout"]["ny"])
        onx = min(nx, overlay_design["layout"]["nx"])
        for i in range(ony):
            for j in range(onx):
                room = overlay[i][j]
                color = ROOM_COLORS.get(room, "#94a3b8")
                rect = mpatches.Rectangle((j, ny-1-i), 1, 1, linewidth=1.5, edgecolor='#ef4444',
                                         facecolor=color, alpha=0.35, hatch='//')
                ax.add_patch(rect)
    ax.annotate('N', xy=(0.5, ny+0.15), fontsize=14, color='white', ha='center',
                arrowprops=dict(facecolor='white', shrink=0.05))
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_interactive_blueprint(design):
    st.image(draw_2d_blueprint(design), use_container_width=True)
    layout = design["layout"]["grid"]
    ny = len(layout)
    nx = len(layout[0]) if layout else 0
    cols = st.columns(3)
    with cols[0]:
        i1 = st.number_input("Row (Room A)", 0, ny-1, 0, key="r1")
        j1 = st.number_input("Col (Room A)", 0, nx-1, 0, key="c1")
    with cols[1]:
        i2 = st.number_input("Row (Room B)", 0, ny-1, 0, key="r2")
        j2 = st.number_input("Col (Room B)", 0, nx-1, 0, key="c2")
    with cols[2]:
        if st.button("Swap Positions"):
            layout[i1][j1], layout[i2][j2] = layout[i2][j2], layout[i1][j1]
            save_design_to_db(design)
            st.rerun()
    return design

def draw_3d_isometric_view(design, drift_factor=0):
    layout = design["layout"]["grid"]
    ny = len(layout)
    nx = len(layout[0]) if layout else 0
    floors = design["floors"]
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('none')
    fig.patch.set_facecolor('#0a0c10')
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
                for (cx, cy) in [(j+offset_x,i),(j+1+offset_x,i),(j+1+offset_x,i+1),(j+offset_x,i+1)]:
                    ax.plot([cx, cx], [cy, cy], [z, z+3], color='white', linewidth=0.5)
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_zlim(0, floors * 3)
    ax.axis('off')
    st.pyplot(fig)

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
                for (x1,y1),(x2,y2) in [((j,i),(j+1,i)),((j+1,i),(j+1,i+1)),((j,i+1),(j+1,i+1)),((j,i),(j,i+1))]:
                    wall = {"type":"IfcWall","name":f"Wall_F{f}_R{i}{j}",
                            "coordinates":{"start":{"x":x1*span,"y":y1*span,"z":f*3},"end":{"x":x2*span,"y":y2*span,"z":f*3}},"height":3}
                    elements.append(wall)
                slab = {"type":"IfcSlab","name":f"Slab_F{f}_R{i}{j}",
                        "coordinates":{"x":j*span,"y":i*span,"z":f*3},"width":span,"depth":span}
                elements.append(slab)
    return {"project_name":f"ARC_{design['id']}","elements":elements}

def generate_boq_csv(boq_data):
    output = StringIO()
    output.write("Category,Cost (USD)\n")
    output.write(f"Substructure,{boq_data['substructure']}\n")
    output.write(f"Superstructure,{boq_data['superstructure']}\n")
    output.write(f"HVAC Mechanical Services,{boq_data['hvac_services']}\n")
    output.write(f"Electrical Power Systems,{boq_data['electrical_services']}\n")
    output.write(f"Plumbing & Sanitation,{boq_data['plumbing_services']}\n")
    output.write(f"Finishes,{boq_data['finishes']}\n")
    output.write(f"Preliminaries,{boq_data['preliminaries']}\n")
    output.write(f"TOTAL USD,{boq_data['total_usd']}\n")
    output.write(f"TOTAL LOCAL ({boq_data['local_currency']}),{boq_data['total_local']}\n")
    return output.getvalue()

# ------------------------------------------------------------
# SIDEBAR NAVIGATION & CONTROLS
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"**User:** `{st.session_state.username}` ({st.session_state.role.upper()})")
    nav = st.pills("Workspace", ["Control Hub", "Synthesis Lab", "Governance & Approvals"], default="Control Hub")
    st.markdown("---")

    if st.session_state.role in ["admin", "lead_architect"]:
        with st.expander("Forex Rates (Admin Control)"):
            st.write("Live FX Rates:")
            for country, fx in st.session_state.regional_fx.items():
                st.write(f"{country}: {fx['symbol']} {fx['rate_to_usd']:,.2f}")
            if st.button("Simulate Forex Volatility"):
                refresh_forex_rates()
                st.success("Rates updated!")
                st.rerun()

    with st.expander("Design Parameters", expanded=True):
        country = st.selectbox("Target Region", list(st.session_state.regional_fx.keys()))
        domain = st.selectbox("Category Domain", list(ARCH_DOMAINS.keys()))
        btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
        plot = st.slider("Plot Footprint (m²)", 200, 5000, 800, 50)
        floors = st.slider("Storeys / Levels", 1, 12, 3)
        baths = st.slider("Bathrooms Count", 1, 10, 2)
        soil = st.selectbox("Soil Profile", list(SOIL_PROFILES.keys()))
        material = st.pills("Structural Framing", [
            "Reinforced Concrete (Eurocode 2)",
            "Structural Steel Profile (Eurocode 3)",
            "Timber Profile (Eurocode 5)"
        ], default="Reinforced Concrete (Eurocode 2)")
        g_k = st.slider("Permanent Load g_k (kN/m²)", 3.0, 8.0, 5.5, 0.5)
        default_q = 2.5 if domain=="Residential" else (4.0 if domain=="Commercial" else 7.5)
        q_k = st.slider("Imposed Load q_k (kN/m²)", 1.5, 10.0, default_q, 0.5)
        steel = st.selectbox("Steel Standard Section", [
            "UB 254x146x31","UB 305x165x40","UC 254x254x73","UC 305x305x97"
        ]) if "Steel" in material else None
        seismic = st.selectbox("Seismic Zone Risk", list(SEISMIC_ZONES.keys()), index=1)
        wind = st.selectbox("Wind Speed Zone", list(WIND_ZONES.keys()), index=1)

    trigger = st.sidebar.button("Execute Generative Model", type="primary", use_container_width=True)
    if st.button("Sign Out"):
        logout()

# ------------------------------------------------------------
# MAIN WORKSPACE VIEWS
# ------------------------------------------------------------
if nav == "Control Hub":
    st.title("Regional Telemetry Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KES Rate", f"KSh {st.session_state.regional_fx['Kenya']['rate_to_usd']:,.2f}")
    col2.metric("UGX Rate", f"USh {st.session_state.regional_fx['Uganda']['rate_to_usd']:,.2f}")
    col3.metric("TZS Rate", f"TSh {st.session_state.regional_fx['Tanzania']['rate_to_usd']:,.2f}")
    col4.metric("SSP Rate", f"SSP {st.session_state.regional_fx['South Sudan']['rate_to_usd']:,.2f}")
    
    st.markdown("---")
    my_designs = load_user_designs(st.session_state.username, st.session_state.role)
    st.subheader(f"Project Database ({len(my_designs)} Active Projects)")
    
    if my_designs:
        for d in my_designs:
            c1, c2, c3, c4, c5 = st.columns([1.5, 2, 1.5, 1.5, 1.5])
            c1.write(f"**#{d['id']}**")
            c2.write(f"{d['type']} ({d['country']})")
            c3.write(f"{d['total_gfa']:,.0f} m²")
            
            st_badge = f'<span class="badge-approved">{d["status"]}</span>' if d['status'] == "Approved" else f'<span class="badge-draft">{d["status"]}</span>'
            c4.markdown(st_badge, unsafe_allow_html=True)
            
            if c5.button("Load Project", key=f"load_{d['id']}"):
                st.session_state.active_design = d
                st.success(f"Loaded #{d['id']}")
                st.rerun()

elif nav == "Governance & Approvals":
    st.title("Project Approval & Role Governance")
    if st.session_state.role not in ["admin", "lead_architect"]:
        st.warning("Role-based restriction: Only Lead Architects and Admins can approve project designs.")
    else:
        all_designs = load_user_designs(role="admin")
        st.write("Review pending architectural & engineering designs:")
        for d in all_designs:
            with st.expander(f"Project #{d['id']} — {d['type']} by {d['username']} ({d['status']})"):
                col_a, col_b, col_c = st.columns(3)
                col_a.write(f"**Domain:** {d['domain']}")
                col_a.write(f"**GFA:** {d['total_gfa']:,.0f} m²")
                col_b.write(f"**Eurocode Status:** {d['analysis']['status']}")
                col_b.write(f"**Zoning Status:** {d['zoning']['status']}")
                col_c.write(f"**Total USD:** ${d['boq']['total_usd']:,.2f}")
                
                btn_col1, btn_col2 = st.columns(2)
                if btn_col1.button("Grant Approval ✅", key=f"app_{d['id']}"):
                    update_design_status(d['id'], "Approved")
                    log_event(st.session_state.username, f"Approved Project #{d['id']}")
                    st.success("Project Approved!")
                    st.rerun()
                if btn_col2.button("Request Changes ⚠️", key=f"rev_{d['id']}"):
                    update_design_status(d['id'], "Under Review")
                    log_event(st.session_state.username, f"Flagged Project #{d['id']} for Review")
                    st.warning("Project sent for review.")
                    st.rerun()

elif nav == "Synthesis Lab":
    st.title("Generative Synthesis & MEP Engine")
    
    if trigger:
        with st.spinner("Synthesizing building model & calculating MEP/Eurocode metrics..."):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            st.session_state.active_design = design
            save_design_to_db(design)
            log_event(st.session_state.username, f"Generated Archetype #{design['id']}")

    if st.session_state.active_design:
        d = ensure_design_compatibility(st.session_state.active_design)
        
        st.subheader(f"Active Model: #{d['id']} — {d['type']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Target Region", d["country"])
        col2.metric("Gross Floor Area", f"{d['total_gfa']:,.0f} m²")
        col3.metric("Storeys", d["floors"])
        col4.metric("Approval Status", d.get("status", "Draft"))

        tabs = st.tabs([
            "2D Interactive", "3D Isometric", "Structural Passport", "MEP & Green Passport",
            "Zoning", "BoQ & Forex", "Forex Forecast", "Drift Simulation",
            "Cost Sensitivity", "Design Compare", "Export IFC & BOQ"
        ])
        
        with tabs[0]:
            st.markdown("### Interactive Floorplan Grid")
            d = draw_interactive_blueprint(d)
            st.session_state.active_design = d
            
        with tabs[1]:
            draw_3d_isometric_view(d)
            
        with tabs[2]:
            st.markdown("### Eurocode Structural Analysis")
            st.json(d["analysis"])
            
        with tabs[3]:
            st.markdown("### Extended MEP Infrastructure & Green Building Passport")
            mep = d.get("mep") or run_mep_analysis(d)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.markdown("#### Mechanical (HVAC)")
                st.metric("Cooling Capacity", f"{mep['mechanical']['cooling_load_tr']} TR")
                st.write(f"**Heat Load:** {mep['mechanical']['cooling_load_kw']} kW")
                st.write(f"**Supply Airflow:** {mep['mechanical']['supply_airflow_cfm']:,.0f} CFM")
                st.write(f"**Fresh Air Intake:** {mep['mechanical']['fresh_air_cfm']:,.0f} CFM")
                st.write(f"**Main Duct Area:** {mep['mechanical']['main_duct_cross_section_m2']} m²")
                
            with col_m2:
                st.markdown("#### Electrical Power & Solar PV")
                st.metric("Max Demand", f"{mep['electrical']['max_demand_kva']} kVA")
                st.write(f"**Connected Load:** {mep['electrical']['connected_load_kva']} kVA")
                st.write(f"**Main Breaker:** {mep['electrical']['main_breaker_amps']} A @ 415V")
                st.write(f"**Transformer Min:** {mep['electrical']['transformer_rating_kva']} kVA")
                st.write(f"**Solar PV Capacity:** {mep['electrical']['recommended_solar_pv_kwp']} kWp")
                st.write(f"**Est. Solar Generation:** {mep['electrical']['est_daily_solar_kwh']} kWh/day")
                
            with col_m3:
                st.markdown("#### Plumbing & Sustainability")
                st.metric("Daily Water Demand", f"{mep['plumbing']['daily_water_demand_liters']:,.0f} L/day")
                st.write(f"**Storage Reserve:** {mep['plumbing']['storage_tank_capacity_m3']} m³")
                st.write(f"**Fixture Units:** {mep['plumbing']['total_wsfu']} WSFU / {mep['plumbing']['total_dfu']} DFU")
                st.write(f"**Rainwater Yield:** {mep['plumbing']['annual_rainwater_yield_m3']} m³/year")
                st.write(f"**Embodied Carbon:** {mep['sustainability']['embodied_carbon_tonnes_co2']} tonnes CO₂")
                
        with tabs[4]:
            zon = d["zoning"]
            st.write(f"Coverage Ratio: **{zon['coverage']}** (max {ARCH_DOMAINS[d['domain']]['max_coverage']}) — {'✅ PASS' if zon['coverage_ok'] else '❌ VIOLATION'}")
            st.write(f"FAR: **{zon['far']}** (max {ARCH_DOMAINS[d['domain']]['max_far']}) — {'✅ PASS' if zon['far_ok'] else '❌ VIOLATION'}")
            st.write(f"Overall Status: **{zon['status']}**")
            
        with tabs[5]:
            boq = d["boq"]
            colA, colB, colC = st.columns(3)
            with colA:
                st.markdown("**Structural Elements**")
                st.metric("Substructure", f"${boq['substructure']:,.2f}")
                st.metric("Superstructure", f"${boq['superstructure']:,.2f}")
            with colB:
                st.markdown("**MEP Systems**")
                st.metric("HVAC Mechanical", f"${boq.get('hvac_services', 0.0):,.2f}")
                st.metric("Electrical Power", f"${boq.get('electrical_services', 0.0):,.2f}")
                st.metric("Plumbing / Drainage", f"${boq.get('plumbing_services', 0.0):,.2f}")
            with colC:
                st.markdown("**Total Valuation**")
                st.metric("Total USD", f"${boq['total_usd']:,.2f}")
                st.metric(f"Total {boq['local_currency']}", f"{boq['symbol']} {boq['total_local']:,.2f}")
                
        with tabs[6]:
            st.subheader("Forex Rate Forecast Engine")
            cur = st.selectbox("Currency Pair", list(st.session_state.regional_fx.keys()), key="forex_cur")
            horizon = st.radio("Prediction Horizon", ["short","medium","long"], horizontal=True, key="fx_hor")
            steps_map = {"short":7,"medium":30,"long":90}
            steps = st.slider("Projection Horizon (Days)", 1, 90, steps_map[horizon])
            base_rate = st.session_state.regional_fx[cur]["rate_to_usd"]
            np.random.seed(42)
            history = base_rate + np.random.normal(0, 0.5, 90).cumsum()
            alpha = 0.3
            smoothed = [history[0]]
            for i in range(1, len(history)):
                smoothed.append(alpha * history[i] + (1-alpha) * smoothed[-1])
            forecast = [smoothed[-1]] * steps
            forecast_dates = [datetime.now() + timedelta(days=i+1) for i in range(steps)]
            hist_dates = [datetime.now() - timedelta(days=i) for i in range(90,0,-1)]
            
            st.metric("Spot Rate", f"{st.session_state.regional_fx[cur]['symbol']} {base_rate:,.2f}")
            
            fig, ax = plt.subplots(figsize=(8,4))
            ax.plot(hist_dates, history, label="Historical Rate", color="#64748b")
            ax.plot(hist_dates, smoothed, "--", color="#94a3b8", label="SMA Trend")
            ax.plot(forecast_dates, forecast, "o-", color="#38bdf8", label="Forecasted Rate")
            ax.legend()
            ax.set_facecolor('#0d1117')
            fig.patch.set_facecolor('#030406')
            ax.tick_params(colors='white')
            st.pyplot(fig)
            
        with tabs[7]:
            st.subheader("Wind Drift Simulation")
            drift_range = st.slider("Wind Shear Deflection Factor", 0.0, 1.0, 0.3, 0.05)
            draw_3d_isometric_view(d, drift_factor=drift_range)
            
        with tabs[8]:
            st.subheader("Unit Rate Sensitivity Model")
            base_rates = {
                "Reinforced Concrete (Eurocode 2)": 350,
                "Structural Steel Profile (Eurocode 3)": 400,
                "Timber Profile (Eurocode 5)": 280,
                "HVAC Mechanical Services": 45,
                "Electrical & Lighting Power": 35,
                "Plumbing & Drainage Services": 25
            }
            new_rates = {}
            for mat, rate in base_rates.items():
                new_rates[mat] = st.slider(f"{mat} ($/m²)", 10, 600, rate, 5)
            updated_boq = compute_detailed_forex_boq(d, rate_overrides=new_rates)
            colA, colB = st.columns(2)
            with colA: st.metric("Adjusted Total USD", f"${updated_boq['total_usd']:,.2f}")
            with colB: st.metric(f"Adjusted Total {updated_boq['local_currency']}",
                                 f"{updated_boq['symbol']} {updated_boq['total_local']:,.2f}")
                                 
        with tabs[9]:
            st.subheader("Comparative Archetype Analysis")
            my_designs_list = load_user_designs(st.session_state.username, st.session_state.role)
            if len(my_designs_list) < 2:
                st.info("Create and save at least two designs to run side-by-side comparison.")
            else:
                ids = [f"{d_i['id']} - {d_i['type']}" for d_i in my_designs_list]
                d1_idx = st.selectbox("Primary Design (A)", range(len(ids)), format_func=lambda x:ids[x])
                d2_idx = st.selectbox("Comparison Design (B)", range(len(ids)), index=min(1,len(ids)-1), format_func=lambda x:ids[x])
                if st.button("Generate Overlay View"):
                    d1 = my_designs_list[d1_idx]
                    d2 = my_designs_list[d2_idx]
                    st.write("### Spatial Footprint Comparison")
                    st.image(draw_2d_blueprint(d1, overlay_design=d2), use_container_width=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("A GFA", f"{d1['total_gfa']:,.0f} m²")
                        st.metric("A Cost (USD)", f"${d1['boq']['total_usd']:,.2f}")
                    with col2:
                        st.metric("B GFA", f"{d2['total_gfa']:,.0f} m²")
                        st.metric("B Cost (USD)", f"${d2['boq']['total_usd']:,.2f}")
                        
        with tabs[10]:
            st.subheader("BIM & BoQ Data Exports")
            ifc_json = generate_ifc_json(d)
            boq_csv = generate_boq_csv(d['boq'])
            
            c_exp1, c_exp2 = st.columns(2)
            with c_exp1:
                st.download_button(
                    "Download BIM IFC-JSON",
                    data=json.dumps(ifc_json, indent=2),
                    file_name=f"IMAGINE_{d['id']}_ifc.json",
                    mime="application/json"
                )
            with c_exp2:
                st.download_button(
                    "Download BoQ CSV Spreadsheet",
                    data=boq_csv,
                    file_name=f"IMAGINE_{d['id']}_BoQ.csv",
                    mime="text/csv"
                )
            st.json(ifc_json, expanded=False)
    else:
        st.info("Configure design parameters in the sidebar and click **Execute Generative Model**.")

