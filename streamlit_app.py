# =========================================================
# IMAGINE – Architectural Intellect, MEP Engine & Enterprise System
# Integrated Black-Edition & Glassmorphic Engine v22.0
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

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Optional PostgreSQL driver import with fallback
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# ------------------------------------------------------------
# PAGE CONFIGURATION & GLASSMORPHIC BLACK THEME
# ------------------------------------------------------------
st.set_page_config(
    page_title="Imagine | Architectural & Engineering Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #dddddd; }
        .stSidebar { background-color: #0c0c0c; border-right: 1px solid #222222; }
        h1, h2, h3, h4, h5, h6 { color: #eeeeee !important; font-weight: 600; }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(20, 20, 20, 0.65);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.5);
        }
        
        .login-box {
            background: rgba(15, 15, 15, 0.85);
            backdrop-filter: blur(16px);
            padding: 2.5rem;
            border-radius: 16px;
            border: 1px solid #333333;
            max-width: 440px;
            margin: 3rem auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }
        
        .stMetric {
            background: rgba(30, 30, 30, 0.4);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #333333;
            color: #eee;
        }
        
        .stButton button {
            background: #1e1e1e;
            color: #dddddd;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid #444444;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background: #2c2c2c;
            color: #ffffff;
            border-color: #666666;
        }
        
        .badge-role {
            background-color: #2563eb;
            color: #ffffff;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 0;
            border-bottom: 2px solid transparent;
            color: #888888;
            padding: 0.5rem 1rem;
        }
        .stTabs [aria-selected="true"] {
            background: transparent !important;
            border-bottom: 2px solid #ffffff;
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ------------------------------------------------------------
# LOGO BRANDING SVG
# ------------------------------------------------------------
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80" width="220" height="60">
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
        font-family="'Segoe UI', Arial, sans-serif" font-weight="400" font-size="26"
        fill="url(#lg)" letter-spacing="5">Imagine</text>
</svg>
"""

# ------------------------------------------------------------
# HYBRID DATABASE CONNECTION & EXECUTOR
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
            conn = psycopg2.connect(pg_url)
            return conn, "postgres"
        except Exception:
            pass

    conn = sqlite3.connect("imagine_platform.db", check_same_thread=False)
    return conn, "sqlite"

def format_query(query: str, db_type: str) -> str:
    if db_type == "postgres":
        return query.replace("?", "%s")
    return query

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
        st.error(f"Database Query Execution Error: {e}")
    finally:
        conn.close()
    return result

# ------------------------------------------------------------
# SECURITY & DATABASE INITIALIZATION
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
            role VARCHAR(30) NOT NULL DEFAULT 'user',
            email VARCHAR(100) DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if is_pg else """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL DEFAULT 'imagine_architectural_platform_salt_2026',
            role TEXT NOT NULL DEFAULT 'user',
            email TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute_query(users_sql)

    projects_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            budget NUMERIC(12, 2) NOT NULL,
            status VARCHAR(30) NOT NULL,
            created_by VARCHAR(50) NOT NULL,
            design_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """ if is_pg else """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            budget REAL NOT NULL,
            status TEXT NOT NULL,
            created_by TEXT NOT NULL,
            design_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute_query(logs_sql)

    admin_user = execute_query("SELECT id FROM users WHERE username = ?", ("admin",), fetch="one")
    if not admin_user:
        salt = uuid.uuid4().hex
        pwd_hash = hash_password("admin123", salt)
        execute_query(
            "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?, ?, ?, ?, ?)",
            ("admin", pwd_hash, salt, "Admin", "admin@arc.studio")
        )

init_db()

def authenticate_user(username: str, password: str):
    if not username or not password:
        return False, None
    row = execute_query(
        "SELECT password_hash, salt, role FROM users WHERE username = ?",
        (username,),
        fetch="one"
    )
    if row:
        db_hash, salt, role = row
        if hash_password(password, salt) == db_hash:
            return True, role
        # Legacy unsalted hash fallback
        if hash_password(password, "imagine_architectural_platform_salt_2026") == db_hash:
            return True, role
    return False, None

def register_user(username, password, email="", role="user"):
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
    username = st.session_state.get("username", "system")
    execute_query("INSERT INTO system_logs (username, message) VALUES (?, ?)", (username, msg))

# ------------------------------------------------------------
# DOMAIN DATA & REGIONAL CONSTANTS
# ------------------------------------------------------------
REGIONAL_FX_DEFAULTS = {
    "Kenya": {"currency": "KES", "rate_to_usd": 129.49, "symbol": "KSh", "cost_multiplier": 1.0, "risk_premium": 0.02},
    "Uganda": {"currency": "UGX", "rate_to_usd": 3665.20, "symbol": "USh", "cost_multiplier": 0.95, "risk_premium": 0.03},
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
# MEP & STRUCTURAL CALCULATIONS ENGINE
# ------------------------------------------------------------
def run_mep_analysis(design):
    gfa = design["total_gfa"]
    domain = design.get("domain", "Residential")
    baths = design.get("bathrooms", 2)
    
    # 1. HVAC Engine
    hvac_densities = {"Residential": 120.0, "Commercial": 160.0, "Industrial": 100.0}
    w_per_m2 = hvac_densities.get(domain, 130.0)
    total_cooling_w = gfa * w_per_m2
    cooling_kw = total_cooling_w / 1000.0
    cooling_tr = cooling_kw / 3.517
    airflow_cfm = cooling_tr * 400.0
    fresh_air_cfm = airflow_cfm * 0.15
    
    # 2. Electrical Engine
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
    
    # 3. Plumbing Engine
    occ_factor = {"Residential": 15.0, "Commercial": 10.0, "Industrial": 30.0}.get(domain, 15.0)
    est_occupants = max(2, math.ceil(gfa / occ_factor))
    lpcd = {"Residential": 150.0, "Commercial": 50.0, "Industrial": 35.0}.get(domain, 100.0)
    daily_water_demand_l = est_occupants * lpcd
    storage_tank_m3 = round((daily_water_demand_l * 1.5) / 1000.0, 2)
    wsfu = (baths * 8) + (math.ceil(gfa / 100) * 4)
    dfu = math.ceil(wsfu * 1.25)
    
    return {
        "mechanical": {
            "cooling_load_kw": round(cooling_kw, 2),
            "cooling_load_tr": round(cooling_tr, 2),
            "supply_airflow_cfm": round(airflow_cfm, 0),
            "fresh_air_cfm": round(fresh_air_cfm, 0),
            "design_density_w_m2": w_per_m2
        },
        "electrical": {
            "connected_load_kw": round(total_connected_kw, 2),
            "connected_load_kva": round(connected_kva, 2),
            "max_demand_kva": round(max_demand_kva, 2),
            "transformer_rating_kva": max(50, transformer_kva),
            "generator_rating_kva": max(30, generator_kva),
            "diversity_factor": diversity
        },
        "plumbing": {
            "est_occupants": est_occupants,
            "daily_water_demand_liters": round(daily_water_demand_l, 0),
            "storage_tank_capacity_m3": storage_tank_m3,
            "total_wsfu": wsfu,
            "total_dfu": dfu
        }
    }

def run_eurocode_analysis(design):
    span = design.get("layout", {}).get("span", 5.0)
    gk = design["loads"]["g_k"]
    qk = design["loads"]["q_k"]
    seismic = SEISMIC_ZONES.get(design["loads"]["seismic_zone"], {"PGA": 0.15})
    wind_speed = WIND_ZONES.get(design["loads"]["wind_zone"], 28)
    soil = SOIL_PROFILES.get(design["soil_type"], {})
    floors = design["floors"]
    M = (gk + 1.5 * qk) * span**2 / 8
    base_pressure = (gk + qk) * floors * 1.5
    footing_width = math.sqrt(base_pressure / max(soil.get("cohesion", 20), 1))
    wind_force = 0.613 * wind_speed**2 * span * floors / 1000
    drift = wind_force * floors**3 / 2000
    return {
        "max_moment_kNm": round(M, 2),
        "footing_width_m": round(footing_width, 2),
        "wind_base_shear_kN": round(wind_force, 2),
        "drift_mm": round(drift, 2),
        "seismic_base_shear_kN": round(seismic["PGA"] * floors * 100 * span * 5, 2),
        "status": "PASS" if M < 100 else "REVIEW"
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
    indices = [(i, j) for i in range(ny) for j in range(nx)]
    np.random.shuffle(indices)
    for idx, room in enumerate(rooms):
        if idx >= len(indices): break
        i, j = indices[idx]
        grid[i, j] = room
    return grid.tolist()

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
        "id": str(uuid.uuid4())[:6].upper(),
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
    design["mep"] = run_mep_analysis(design)
    design["zoning"] = verify_zoning_laws(design)
    design["boq"] = compute_detailed_forex_boq(design)
    return design

# ------------------------------------------------------------
# VISUALIZATIONS & DRAWING ENGINES
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
                                     facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            ax.text(j + 0.5, ny - 1 - i + 0.5, room[:8], ha='center', va='center',
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
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#000000')
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
        i1 = st.number_input("Row (Room 1)", 0, ny - 1, 0, key="r1")
        j1 = st.number_input("Col (Room 1)", 0, nx - 1, 0, key="c1")
    with cols[1]:
        i2 = st.number_input("Row (Room 2)", 0, ny - 1, 0, key="r2")
        j2 = st.number_input("Col (Room 2)", 0, nx - 1, 0, key="c2")
    with cols[2]:
        if st.button("Swap Selected Rooms"):
            layout[i1][j1], layout[i2][j2] = layout[i2][j2], layout[i1][j1]
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
    fig.patch.set_facecolor('#000000')
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
                for (x1, y1), (x2, y2) in [((j, i), (j + 1, i)), ((j + 1, i), (j + 1, i + 1)), ((j, i + 1), (j + 1, i + 1)), ((j, i), (j, i + 1))]:
                    wall = {
                        "type": "IfcWall", "name": f"Wall_F{f}_R{i}{j}",
                        "coordinates": {"start": {"x": x1 * span, "y": y1 * span, "z": f * 3}, "end": {"x": x2 * span, "y": y2 * span, "z": f * 3}},
                        "height": 3
                    }
                    elements.append(wall)
                slab = {
                    "type": "IfcSlab", "name": f"Slab_F{f}_R{i}{j}",
                    "coordinates": {"x": j * span, "y": i * span, "z": f * 3},
                    "width": span, "depth": span
                }
                elements.append(slab)
    return {"project_name": f"ARC_{design['id']}", "elements": elements}

# ------------------------------------------------------------
# SESSION & AUTHENTICATION STATE HANDLERS
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

def render_login_signup():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;">' + LOGO_SVG + '</div>', unsafe_allow_html=True)
    st.caption("<p style='text-align:center;'>Architectural & Engineering Platform</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Register"])
    with tab1:
        with st.form("login_form"):
            u = st.text_input("Username", placeholder="e.g. admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Sign In", use_container_width=True):
                ok, role = authenticate_user(u.strip(), p.strip())
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.username = u.strip()
                    st.session_state.role = role
                    log_system_event("User logged in")
                    st.success("Authenticated! Loading system...")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    with tab2:
        with st.form("register_form"):
            new_u = st.text_input("Username")
            new_p = st.text_input("Password", type="password")
            new_e = st.text_input("Email (optional)")
            new_r = st.selectbox("Requested Role", ["Architect", "Engineer", "Project Manager", "Viewer"])
            if st.form_submit_button("Create Account", use_container_width=True):
                if not new_u or not new_p:
                    st.error("Username and password are required.")
                else:
                    ok, msg = register_user(new_u.strip(), new_p.strip(), new_e.strip(), new_r)
                    if ok:
                        st.success(msg + " You can now sign in.")
                    else:
                        st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_login_signup()
    st.stop()

def logout():
    log_system_event("User logged out")
    for key in ["authenticated", "username", "role", "active_design"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------------------------------------------------------------
# SIDEBAR CONTROL PANEL & CONFIGURATION MATRIX
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"User: **{st.session_state.username}**")
    st.markdown(f"Role: <span class='badge-role'>{st.session_state.role}</span>", unsafe_allow_html=True)
    st.markdown("---")

    nav_options = [
        "Control Hub",
        "Generative Synthesis Lab",
        "Projects & Management",
        "Engineering Calculators",
        "Forex & Budgeting"
    ]
    if st.session_state.role == "Admin":
        nav_options.append("User & Admin Control")

    choice = st.radio("System Module", nav_options)
    st.markdown("---")

    if choice == "Generative Synthesis Lab":
        with st.expander("Configuration Matrix", expanded=True):
            country = st.selectbox("Region", list(st.session_state.regional_fx.keys()))
            domain = st.selectbox("Category", list(ARCH_DOMAINS.keys()))
            btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
            plot = st.slider("Plot Size (m²)", 200, 5000, 800, 50)
            floors = st.slider("Storeys", 1, 12, 3)
            baths = st.slider("Bathrooms", 1, 10, 2)
            soil = st.selectbox("Soil Profile", list(SOIL_PROFILES.keys()))
            material = st.pills("Structural Frame", [
                "Reinforced Concrete (Eurocode 2)",
                "Structural Steel Profile (Eurocode 3)",
                "Timber Profile (Eurocode 5)"
            ], default="Reinforced Concrete (Eurocode 2)")
            g_k = st.slider("Permanent Load (kN/m²)", 3.0, 8.0, 5.5, 0.5)
            default_q = 2.5 if domain == "Residential" else (4.0 if domain == "Commercial" else 7.5)
            q_k = st.slider("Imposed Load (kN/m²)", 1.5, 10.0, default_q, 0.5)
            steel = st.selectbox("Steel Section", [
                "UB 254x146x31", "UB 305x165x40", "UC 254x254x73", "UC 305x305x97"
            ]) if "Steel" in material else None
            seismic = st.selectbox("Seismic Zone", list(SEISMIC_ZONES.keys()), index=1)
            wind = st.selectbox("Wind Zone", list(WIND_ZONES.keys()), index=1)

        trigger_gen = st.button("Execute Generation", type="primary", use_container_width=True)

    if st.button("Sign Out", use_container_width=True):
        logout()

# ------------------------------------------------------------
# MODULE 1: CONTROL HUB & TELEMETRY
# ------------------------------------------------------------
if choice == "Control Hub":
    st.title("🏛️ Regional Telemetry & Operations Dashboard")
    st.caption("Live foreign exchange tracking, system health, and persistent storage metrics.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("KES / USD", f"{st.session_state.regional_fx['Kenya']['rate_to_usd']:,.2f}")
    c2.metric("UGX / USD", f"{st.session_state.regional_fx['Uganda']['rate_to_usd']:,.2f}")
    c3.metric("TZS / USD", f"{st.session_state.regional_fx['Tanzania']['rate_to_usd']:,.2f}")
    c4.metric("SSP / USD", f"{st.session_state.regional_fx['South Sudan']['rate_to_usd']:,.2f}")
    
    st.markdown("---")
    colA, colB = st.columns([2, 1])
    
    with colA:
        st.subheader("System Projects Database")
        projects = execute_query("SELECT id, title, category, budget, status, created_by FROM projects", fetch="all")
        if projects:
            df = pd.DataFrame(projects, columns=["ID", "Title", "Category", "Budget ($)", "Status", "Owner"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No active projects found. Navigate to Projects or Synthesis Lab to create one.")
            
    with colB:
        st.subheader("Recent System Telemetry")
        logs = execute_query("SELECT username, message, created_at FROM system_logs ORDER BY id DESC LIMIT 6", fetch="all")
        if logs:
            for l in logs:
                st.caption(f"**{l[0]}**: {l[1]} *(at {l[2]})*")
        else:
            st.caption("No recent events logged.")

# ------------------------------------------------------------
# MODULE 2: GENERATIVE SYNTHESIS LAB
# ------------------------------------------------------------
elif choice == "Generative Synthesis Lab":
    st.title("Generative Synthesis & Analysis Engine")
    
    if 'trigger_gen' in locals() and trigger_gen:
        with st.spinner("Synthesizing structural model and MEP services..."):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            st.session_state.active_design = design
            
            # Save generated model to database
            execute_query(
                "INSERT INTO projects (title, category, budget, status, created_by, design_data) VALUES (?, ?, ?, ?, ?, ?)",
                (f"{design['type']} ({design['id']})", design['domain'], design['boq']['total_usd'], "Generated", st.session_state.username, json.dumps(design))
            )
            log_system_event(f"Generated Archetype Model #{design['id']}")

    if st.session_state.active_design:
        d = st.session_state.active_design
        st.subheader(f"Active Model Archetype: {d['id']} — {d['type']}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Region", d["country"])
        m2.metric("GFA", f"{d['total_gfa']:,.0f} m²")
        m3.metric("Storeys", d["floors"])
        m4.metric("Doors / Windows", f"{d['doors']} / {d['windows']}")

        tabs = st.tabs([
            "2D Interactive", "3D Isometric", "Structural Passport", "MEP Passport",
            "Zoning", "BoQ & Forex", "Forex Forecast", "Drift Animation",
            "Cost Sensitivity", "Design Compare", "Export IFC"
        ])
        
        with tabs[0]:
            st.markdown("### Interactive 2D Layout")
            d = draw_interactive_blueprint(d)
            st.session_state.active_design = d
            
        with tabs[1]:
            st.markdown("### 3D Structural Isometric")
            draw_3d_isometric_view(d)
            
        with tabs[2]:
            st.markdown("### Structural Eurocode Analysis")
            st.json(d["analysis"])
            
        with tabs[3]:
            st.markdown("### MEP Infrastructure & Load Passport")
            mep = d.get("mep") or run_mep_analysis(d)
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown("#### Mechanical (HVAC)")
                st.metric("Cooling Capacity", f"{mep['mechanical']['cooling_load_tr']} TR")
                st.write(f"**Heat Load:** {mep['mechanical']['cooling_load_kw']} kW")
                st.write(f"**Supply Airflow:** {mep['mechanical']['supply_airflow_cfm']:,.0f} CFM")
                st.write(f"**Fresh Air Intake:** {mep['mechanical']['fresh_air_cfm']:,.0f} CFM")
            with col_m2:
                st.markdown("#### Electrical Power")
                st.metric("Max Demand", f"{mep['electrical']['max_demand_kva']} kVA")
                st.write(f"**Connected Load:** {mep['electrical']['connected_load_kva']} kVA")
                st.write(f"**Transformer Rating:** {mep['electrical']['transformer_rating_kva']} kVA")
                st.write(f"**Genset Backup:** {mep['electrical']['generator_rating_kva']} kVA")
            with col_m3:
                st.markdown("#### Plumbing & Sanitation")
                st.metric("Daily Water Demand", f"{mep['plumbing']['daily_water_demand_liters']:,.0f} L/day")
                st.write(f"**Est. Occupancy:** {mep['plumbing']['est_occupants']} Persons")
                st.write(f"**Storage Reserve:** {mep['plumbing']['storage_tank_capacity_m3']} m³")
                st.write(f"**Fixture Units:** {mep['plumbing']['total_wsfu']} WSFU / {mep['plumbing']['total_dfu']} DFU")
                
        with tabs[4]:
            st.markdown("### Zoning Compliance")
            zon = d["zoning"]
            st.write(f"**Coverage:** {zon['coverage']} (max {ARCH_DOMAINS[d['domain']]['max_coverage']}) — {'✅ OK' if zon['coverage_ok'] else '❌ VIOLATION'}")
            st.write(f"**FAR:** {zon['far']} (max {ARCH_DOMAINS[d['domain']]['max_far']}) — {'✅ OK' if zon['far_ok'] else '❌ VIOLATION'}")
            st.write(f"**Overall Compliance:** {zon['status']}")
            
        with tabs[5]:
            st.markdown("### Bill of Quantities & Regional Forex")
            boq = d["boq"]
            colA, colB, colC = st.columns(3)
            with colA:
                st.markdown("**Substructure & Structure**")
                st.metric("Substructure", f"${boq['substructure']:,.2f}")
                st.metric("Superstructure", f"${boq['superstructure']:,.2f}")
            with colB:
                st.markdown("**MEP Engineering**")
                st.metric("HVAC Services", f"${boq['hvac_services']:,.2f}")
                st.metric("Electrical Systems", f"${boq['electrical_services']:,.2f}")
                st.metric("Plumbing Services", f"${boq['plumbing_services']:,.2f}")
            with colC:
                st.markdown("**Totals & Conversion**")
                st.metric("Total USD", f"${boq['total_usd']:,.2f}")
                st.metric(f"Total {boq['local_currency']}", f"{boq['symbol']} {boq['total_local']:,.2f}")
                
        with tabs[6]:
            st.markdown("### Forex Market Forecast")
            cur = st.selectbox("Currency", list(st.session_state.regional_fx.keys()), key="forex_cur")
            horizon = st.radio("Horizon", ["short", "medium", "long"], horizontal=True, key="fx_hor")
            steps_map = {"short": 7, "medium": 30, "long": 90}
            steps = st.slider("Days", 1, 90, steps_map[horizon])
            base_rate = st.session_state.regional_fx[cur]["rate_to_usd"]
            
            np.random.seed(42)
            history = base_rate + np.random.normal(0, 0.5, 90).cumsum()
            alpha = 0.3
            smoothed = [history[0]]
            for i in range(1, len(history)):
                smoothed.append(alpha * history[i] + (1 - alpha) * smoothed[-1])
            forecast = [smoothed[-1]] * steps
            forecast_dates = [datetime.now() + timedelta(days=i + 1) for i in range(steps)]
            hist_dates = [datetime.now() - timedelta(days=i) for i in range(90, 0, -1)]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(hist_dates, history, label="Historical", color="#666666")
            ax.plot(hist_dates, smoothed, "--", color="#aaaaaa", label="Smoothed Trend")
            ax.plot(forecast_dates, forecast, "o-", color="#ffffff", label="Forecast")
            ax.legend()
            ax.set_facecolor('#111111')
            fig.patch.set_facecolor('#000000')
            ax.tick_params(colors='white')
            st.pyplot(fig)
            
        with tabs[7]:
            st.markdown("### Wind Drift Simulation")
            drift_range = st.slider("Drift amplitude factor", 0.0, 1.0, 0.3, 0.05)
            draw_3d_isometric_view(d, drift_factor=drift_range)
            
        with tabs[8]:
            st.markdown("### Cost Sensitivity Adjuster")
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
                new_rates[mat] = st.slider(mat, 10, 600, rate, 5)
            updated_boq = compute_detailed_forex_boq(d, rate_overrides=new_rates)
            ca, cb = st.columns(2)
            ca.metric("Updated Total USD", f"${updated_boq['total_usd']:,.2f}")
            cb.metric(f"Updated Local ({updated_boq['local_currency']})", f"{updated_boq['symbol']} {updated_boq['total_local']:,.2f}")
            
        with tabs[9]:
            st.markdown("### Model Comparison Engine")
            all_saved = execute_query("SELECT design_data FROM projects WHERE design_data != '{}'", fetch="all")
            parsed_designs = []
            if all_saved:
                for row in all_saved:
                    try:
                        parsed_designs.append(json.loads(row[0]))
                    except Exception:
                        pass
            if len(parsed_designs) < 2:
                st.warning("Generate at least two models to enable side-by-side comparison.")
            else:
                ids = [f"{des['id']} - {des['type']}" for des in parsed_designs]
                d1_idx = st.selectbox("Model A", range(len(ids)), format_func=lambda x: ids[x], key="cmp1")
                d2_idx = st.selectbox("Model B", range(len(ids)), index=min(1, len(ids) - 1), format_func=lambda x: ids[x], key="cmp2")
                if st.button("Compare Archetypes"):
                    d1, d2 = parsed_designs[d1_idx], parsed_designs[d2_idx]
                    st.image(draw_2d_blueprint(d1, overlay_design=d2), use_container_width=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Model A GFA", f"{d1['total_gfa']} m²")
                        st.metric("Model A Cost", f"${d1['boq']['total_usd']:,.2f}")
                    with c2:
                        st.metric("Model B GFA", f"{d2['total_gfa']} m²")
                        st.metric("Model B Cost", f"${d2['boq']['total_usd']:,.2f}")
                        
        with tabs[10]:
            st.markdown("### IFC / Revit Export Engine")
            ifc_json = generate_ifc_json(d)
            st.download_button(
                "Download IFC BIM Schema (JSON)",
                data=json.dumps(ifc_json, indent=2),
                file_name=f"Imagine_BIM_{d['id']}.json",
                mime="application/json"
            )
            st.json(ifc_json, expanded=False)
    else:
        st.info("Configure parameters in the sidebar matrix and click 'Execute Generation'.")

# ------------------------------------------------------------
# MODULE 3: PROJECTS & MANAGEMENT
# ------------------------------------------------------------
elif choice == "Projects & Management":
    st.title("📋 Architecture & Project Management")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Register New Project")
        with st.form("new_project_form"):
            title = st.text_input("Project Title")
            category = st.selectbox("Category", ["New Construction", "Renovation", "MEP Upgrade", "Structural Retrofit"])
            budget = st.number_input("Budget ($)", min_value=1000.0, step=5000.0)
            status = st.selectbox("Initial Status", ["Planning", "Design Phase", "In Review", "Approved"])
            
            if st.form_submit_button("Register Project", use_container_width=True):
                if title:
                    execute_query(
                        "INSERT INTO projects (title, category, budget, status, created_by) VALUES (?, ?, ?, ?, ?)",
                        (title, category, budget, status, st.session_state.username)
                    )
                    log_system_event(f"Registered project '{title}'")
                    st.success(f"Project '{title}' successfully created.")
                    st.rerun()
                else:
                    st.warning("Project title is required.")

    with col2:
        st.subheader("Project Inventory")
        rows = execute_query("SELECT id, title, category, budget, status, created_by, created_at FROM projects", fetch="all")
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Title", "Category", "Budget ($)", "Status", "Created By", "Timestamp"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No projects recorded. Use the form to register one.")

# ------------------------------------------------------------
# MODULE 4: STANDALONE ENGINEERING CALCULATORS
# ------------------------------------------------------------
elif choice == "Engineering Calculators":
    st.title("⚡ Interactive MEP & Structural Calculators")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Electrical Panel Load", "HVAC Airflow", "Plumbing Pipe Sizing", "Beam Eurocode Check"])
    
    with tab1:
        st.subheader("Electrical Demand Estimator")
        area = st.number_input("Floor Area (m²)", min_value=10.0, value=150.0)
        density = st.slider("Power Density (W/m²)", 10, 100, 35)
        safety_factor = st.slider("Safety Factor", 1.0, 1.5, 1.25)
        total_kw = (area * density * safety_factor) / 1000.0
        amps_3phase = (total_kw * 1000) / (400 * 1.732 * 0.85)
        c1, c2 = st.columns(2)
        c1.metric("Estimated Demand", f"{total_kw:.2f} kW")
        c2.metric("3-Phase Current (400V)", f"{amps_3phase:.2f} A")
        
    with tab2:
        st.subheader("HVAC Airflow Requirement")
        room_vol = st.number_input("Room Volume (m³)", min_value=20.0, value=300.0)
        ach = st.number_input("Air Changes per Hour (ACH)", min_value=1, value=6)
        cfm = (room_vol * ach * 35.315) / 60.0
        st.metric("Required Supply Airflow", f"{cfm:.1f} CFM")
        
    with tab3:
        st.subheader("Plumbing Flow Rate Calculator")
        wsfu = st.number_input("Total Fixture Units (WSFU)", min_value=1, value=25)
        est_gpm = wsfu * 0.75
        st.metric("Peak Demand Flow", f"{est_gpm:.2f} GPM")
        
    with tab4:
        st.subheader("Beam Eurocode Bending Check")
        c1, c2 = st.columns(2)
        with c1:
            length = st.number_input("Span Length (m)", min_value=1.0, value=6.0)
            udl = st.number_input("Uniform Load (kN/m)", min_value=1.0, value=15.0)
            fy = st.selectbox("Steel Grade (fy MPa)", [275, 355, 460], index=1)
        with c2:
            w_el = st.number_input("Section Modulus Wel (cm³)", min_value=50.0, value=400.0)
            
        max_moment = (udl * (length ** 2)) / 8.0
        capacity = (w_el * 1e-6 * (fy * 1e3))
        utilization = (max_moment / capacity) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Bending Moment", f"{max_moment:.2f} kNm")
        m2.metric("Moment Capacity", f"{capacity:.2f} kNm")
        m3.metric("Utilization", f"{utilization:.1f}%", delta="SAFE" if utilization <= 100 else "OVERLOADED", delta_color="normal" if utilization <= 100 else "inverse")

# ------------------------------------------------------------
# MODULE 5: FOREX & BUDGETING ENGINE
# ------------------------------------------------------------
elif choice == "Forex & Budgeting":
    st.title("💱 Multi-Currency Forex & Budget Conversion")
    
    rates = {c: data["rate_to_usd"] for c, data in st.session_state.regional_fx.items()}
    rates["USD"] = 1.0
    rates["EUR"] = 0.92
    rates["GBP"] = 0.78

    c1, c2, c3 = st.columns(3)
    with c1:
        amount = st.number_input("Base Amount", min_value=1.0, value=10000.0)
    with c2:
        from_curr = st.selectbox("From Currency", list(rates.keys()), index=0)
    with c3:
        to_curr = st.selectbox("To Currency", list(rates.keys()), index=1)

    usd_val = amount / rates[from_curr]
    converted = usd_val * rates[to_curr]

    st.markdown("---")
    st.subheader(f"Converted Value: **{converted:,.2f} {to_curr}**")

# ------------------------------------------------------------
# MODULE 6: ADMIN & USER CONTROL (ADMIN ONLY)
# ------------------------------------------------------------
elif choice == "User & Admin Control":
    st.title("⚙️ User & Access Control Management")
    if st.session_state.role != "Admin":
        st.error("Access Restricted: Requires Administrator privileges.")
        st.stop()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Admin User Registration")
        with st.form("create_user_admin_form"):
            new_u = st.text_input("Username")
            new_p = st.text_input("Password", type="password")
            new_r = st.selectbox("Role", ["Admin", "Project Manager", "Engineer", "Architect", "Viewer"])
            new_e = st.text_input("Email")
            
            if st.form_submit_button("Create User", use_container_width=True):
                if new_u and new_p:
                    ok, msg = register_user(new_u.strip(), new_p.strip(), new_e.strip(), new_r)
                    if ok:
                        st.success(f"User '{new_u}' registered.")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Username and password are required.")

    with col2:
        st.subheader("Live Forex Matrix Overrides")
        for country in list(st.session_state.regional_fx.keys()):
            cur_rate = st.session_state.regional_fx[country]["rate_to_usd"]
            new_val = st.number_input(f"{country} ({st.session_state.regional_fx[country]['currency']}) Rate to USD", value=cur_rate, step=0.1)
            st.session_state.regional_fx[country]["rate_to_usd"] = new_val

    st.markdown("---")
    st.subheader("System User Directory")
    users = execute_query("SELECT id, username, role, email, created_at FROM users", fetch="all")
    if users:
        st.dataframe(pd.DataFrame(users, columns=["ID", "Username", "Role", "Email", "Created At"]), use_container_width=True)
