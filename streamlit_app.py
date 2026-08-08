# =========================================================
# IMAGINE – Architectural Intellect, Structural/MEP & Forex Engine
# v22.0 – Black Edition, Dynamic DB Engine & Integrated MEP
# =========================================================

import streamlit as st
import json, uuid, math, hashlib, sqlite3, random, os
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ------------------------------------------------------------
# DATABASE ENGINE (PostgreSQL with SQLite Fallback)
# ------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL") or (st.secrets.get("DATABASE_URL") if "DATABASE_URL" in st.secrets else None)

def get_db_connection():
    if DATABASE_URL:
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            return conn, "postgresql"
        except Exception as e:
            st.warning(f"PostgreSQL connection failed, falling back to SQLite: {e}")
    
    conn = sqlite3.connect("arc_studio_v22.db")
    return conn, "sqlite"

def init_db():
    conn, db_type = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password_hash VARCHAR(128) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            email VARCHAR(100) DEFAULT ''
        )
    ''')
    
    # Designs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS designs (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            domain VARCHAR(50),
            btype VARCHAR(100),
            country VARCHAR(50),
            data_json TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            approved_by VARCHAR(50) DEFAULT '',
            created_at VARCHAR(50)
        )
    ''')
    
    # Audit log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id VARCHAR(36) PRIMARY KEY,
            created_at VARCHAR(50),
            username VARCHAR(50),
            message TEXT
        )
    ''')

    # Seed initial Admin account if none exists
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        salt = uuid.uuid4().hex
        admin_hash = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
        c.execute(
            "INSERT INTO users (username, password_hash, salt, role, email) VALUES (%s, %s, %s, %s, %s)" if db_type == "postgresql" 
            else "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)",
            ("admin", admin_hash, salt, "admin", "admin@arc.studio")
        )
        
        # Seed an Engineer role as well
        eng_salt = uuid.uuid4().hex
        eng_hash = hashlib.sha256(("engineer123" + eng_salt).encode()).hexdigest()
        c.execute(
            "INSERT INTO users (username, password_hash, salt, role, email) VALUES (%s, %s, %s, %s, %s)" if db_type == "postgresql" 
            else "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)",
            ("engineer", eng_hash, eng_salt, "engineer", "engineer@arc.studio")
        )

    conn.commit()
    conn.close()

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

def authenticate_user(username, password):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    query = "SELECT password_hash, salt, role FROM users WHERE username=%s" if db_type == "postgresql" else "SELECT password_hash, salt, role FROM users WHERE username=?"
    c.execute(query, (username,))
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
    try:
        salt = uuid.uuid4().hex
        pwd_hash = hash_password(password, salt)
        query = "INSERT INTO users (username, password_hash, salt, role, email) VALUES (%s,%s,%s,%s,%s)" if db_type == "postgresql" else "INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)"
        c.execute(query, (username, pwd_hash, salt, role, email))
        conn.commit()
        return True, f"User '{username}' successfully registered."
    except Exception as e:
        return False, f"User registration failed: {e}"
    finally:
        conn.close()

def save_design_db(design):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    query = """
        INSERT INTO designs (id, username, domain, btype, country, data_json, status, approved_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """ if db_type == "postgresql" else """
        INSERT INTO designs (id, username, domain, btype, country, data_json, status, approved_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    c.execute(query, (
        design["id"], design["username"], design["domain"], design["type"],
        design["country"], json.dumps(design), design.get("status", "PENDING"),
        design.get("approved_by", ""), design["created"]
    ))
    conn.commit()
    conn.close()

def update_design_status_db(design_id, status, approver):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    query = "UPDATE designs SET status=%s, approved_by=%s WHERE id=%s" if db_type == "postgresql" else "UPDATE designs SET status=?, approved_by=? WHERE id=?"
    c.execute(query, (status, approver, design_id))
    conn.commit()
    conn.close()

def load_user_designs_db(username, role):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    if role in ["admin", "engineer"]:
        query = "SELECT data_json FROM designs"
        c.execute(query)
    else:
        query = "SELECT data_json FROM designs WHERE username=%s" if db_type == "postgresql" else "SELECT data_json FROM designs WHERE username=?"
        c.execute(query, (username,))
    
    rows = c.fetchall()
    conn.close()
    designs = []
    for row in rows:
        designs.append(json.loads(row[0]))
    return designs

def log_event_db(username, msg):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    query = "INSERT INTO system_logs (id, created_at, username, message) VALUES (%s,%s,%s,%s)" if db_type == "postgresql" else "INSERT INTO system_logs (id, created_at, username, message) VALUES (?,?,?,?)"
    c.execute(query, (str(uuid.uuid4())[:8], datetime.now().isoformat(), username, msg))
    conn.commit()
    conn.close()

def get_recent_logs_db(limit=5):
    conn, db_type = get_db_connection()
    c = conn.cursor()
    query = f"SELECT created_at, username, message FROM system_logs ORDER BY created_at DESC LIMIT {limit}"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return [{"time": r[0], "user": r[1], "msg": r[2]} for r in rows]

init_db()

# ------------------------------------------------------------
# CUSTOM THEME – Pure Black, Minimal Highlights
# ------------------------------------------------------------
st.set_page_config(page_title="Imagine", page_icon="🏛️", layout="wide")
st.markdown("""
<style>
    .stApp { background: #000000; color: #dddddd; }
    .stSidebar { background: #111111; border-right: 1px solid #333333; }
    h1,h2,h3,h4,h5,h6 { color: #cccccc !important; font-weight: 600; }
    .stMetric { background: rgba(80,80,80,0.15); border-radius:8px; padding:10px; border:1px solid #444; color:#eee; }
    .stButton button {
        background: #222; color: #ddd; font-weight:bold; border-radius:6px;
        border: 1px solid #555;
    }
    .stButton button:hover { background:#333; color:white; border-color:#777; }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius:0; border-bottom:2px solid transparent;
        color: #999; padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important; border-bottom:2px solid #ccc;
        color: #eee !important;
    }
    .login-box {
        background: #111111; padding: 2rem; border-radius: 12px;
        border: 1px solid #333; max-width: 400px; margin: 4rem auto;
        box-shadow: none;
    }
    .logo-container { text-align: center; margin-bottom: 1.5rem; }
    .stApp, .stSidebar { box-shadow: none; }
    .stMetric { box-shadow: none; }
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGO SVG
# ------------------------------------------------------------
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80" width="240" height="64">
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#888"/>
      <stop offset="100%" stop-color="#ccc"/>
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
# SESSION STATE & AUTH
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

def login_page():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="logo-container">' + LOGO_SVG + '</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                ok, role = authenticate_user(u, p)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.username = u
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    with tab2:
        with st.form("register_form"):
            new_u = st.text_input("Choose Username")
            new_p = st.text_input("Create Password", type="password")
            new_e = st.text_input("Email (optional)")
            req_role = st.selectbox("Role", ["user", "engineer"])
            if st.form_submit_button("Sign Up"):
                if not new_u or not new_p:
                    st.error("Username and password required.")
                else:
                    ok, msg = register_user(new_u, new_p, new_e, role=req_role)
                    if ok:
                        st.success(msg + " You can now login.")
                    else:
                        st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    login_page()
    st.stop()

def logout():
    for key in ["authenticated", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------------------------------------------------------------
# CONFIGURATION MATRICES & DOMAINS
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
ROOM_COLORS = {"Bedroom":"#a78bfa","Living Room":"#34d399","Kitchen":"#fbbf24","Bathroom":"#60a5fa","Office":"#f87171","Dining":"#f472b6","Corridor":"#94a3b8","Garage":"#64748b"}

if "active_design" not in st.session_state:
    st.session_state.active_design = None

# ------------------------------------------------------------
# MEP & EUROCODE CALCULATIONS
# ------------------------------------------------------------
def run_mep_analysis(design):
    """Calculates Mechanical (HVAC), Electrical Demand, and Plumbing (MEP) requirements."""
    gfa = design["total_gfa"]
    domain = design.get("domain", "Residential")
    
    # 1. Mechanical / HVAC Cooling Load (kW & Tons)
    cooling_factor_w = 150.0 if domain == "Commercial" else (110.0 if domain == "Residential" else 80.0)
    hvac_kw = (gfa * cooling_factor_w) / 1000.0
    hvac_tons = hvac_kw / 3.517
    
    # 2. Electrical Demand Load (kVA)
    elec_density_va = 55.0 if domain == "Commercial" else (35.0 if domain == "Residential" else 45.0)
    base_elec_kva = (gfa * elec_density_va) / 1000.0
    total_elec_kva = base_elec_kva + (hvac_kw * 0.85)
    
    # 3. Plumbing & Sanitary Water Demand
    est_occupants = max(2, int(gfa / 18.0))
    per_capita_liters = 180.0
    daily_water_l = est_occupants * per_capita_liters
    peak_plumbing_flow_ls = (daily_water_l / (8.0 * 3600.0)) * 3.2
    
    return {
        "hvac_cooling_kw": round(hvac_kw, 2),
        "hvac_capacity_tons": round(hvac_tons, 2),
        "electrical_demand_kva": round(total_elec_kva, 2),
        "estimated_occupants": est_occupants,
        "daily_water_demand_liters": round(daily_water_l, 0),
        "peak_plumbing_flow_ls": round(peak_plumbing_flow_ls, 2),
        "mep_status": "COMPLIANT"
    }

def run_eurocode_analysis(design):
    span = design.get("layout", {}).get("span", 5.0)
    gk = design["loads"]["g_k"]
    qk = design["loads"]["q_k"]
    seismic = SEISMIC_ZONES.get(design["loads"]["seismic_zone"], {"PGA":0.15})
    wind_speed = WIND_ZONES.get(design["loads"]["wind_zone"], 28)
    soil = SOIL_PROFILES.get(design["soil_type"], {})
    floors = design["floors"]
    
    M = (gk + 1.5*qk) * span**2 / 8
    base_pressure = (gk + qk) * floors * 1.5
    footing_width = math.sqrt(base_pressure / max(soil.get("cohesion", 20), 1))
    wind_force = 0.613 * wind_speed**2 * span * floors / 1000
    drift = wind_force * floors**3 / 2000
    
    return {
        "max_moment_kNm": round(M, 2),
        "footing_width_m": round(footing_width, 2),
        "wind_base_shear_kN": round(wind_force, 2),
        "drift_mm": round(drift, 2),
        "seismic_base_shear_kN": round(seismic["PGA"]*floors*100*span*5, 2),
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
        "status": "APPROVED" if (cov<=max_cov and far<=max_far) else "VIOLATION"
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
    superstructure = 0.45 * rate_per_m2 * gfa
    mep_trade = 0.25 * rate_per_m2 * gfa  # Mechanical, Electrical, Plumbing Services (25%)
    finishes = 0.10 * rate_per_m2 * gfa
    preliminaries = 0.05 * rate_per_m2 * gfa
    
    total_usd = (substructure + superstructure + mep_trade + finishes + preliminaries) * mult * (1 + risk)
    return {
        "substructure": round(substructure, 2),
        "superstructure": round(superstructure, 2),
        "mep_services": round(mep_trade, 2),
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
        "status": "PENDING",
        "approved_by": "",
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
        ground_footprint = design.get("ground_footprint", design["plot_size"]*0.4)
        bay_area = span * span
        total_bays = max(2, math.ceil(ground_footprint / bay_area))
        nx = max(2, math.ceil(math.sqrt(total_bays)))
        ny = max(2, math.ceil(total_bays / nx))
        layout_grid = generate_intelligent_layout(design.get("rooms", ["Living Room","Bedroom","Kitchen","Bathroom"]), nx, ny, span)
        design["layout"] = {"grid": layout_grid, "nx": nx, "ny": ny, "span": span}
    if "loads" not in design:
        design["loads"] = {"g_k":5.5, "q_k":2.5 if design.get("domain")=="Residential" else (4.0 if design.get("domain")=="Commercial" else 7.5),
                           "steel_section": None, "seismic_zone":"Moderate (PGA=0.15g)", "wind_zone":"Moderate (28 m/s)"}
    if "analysis" not in design: design["analysis"] = run_eurocode_analysis(design)
    if "mep" not in design: design["mep"] = run_mep_analysis(design)
    if "zoning" not in design: design["zoning"] = verify_zoning_laws(design)
    if "boq" not in design: design["boq"] = compute_detailed_forex_boq(design)
    if "status" not in design: design["status"] = "PENDING"
    return design

# ------------------------------------------------------------
# 2D & 3D VISUALS
# ------------------------------------------------------------
def draw_2d_blueprint(design, overlay_design=None):
    layout = design["layout"]["grid"]
    nx = design["layout"]["nx"]
    ny = design["layout"]["ny"]
    fig, ax = plt.subplots(figsize=(8, 8*ny/nx if nx>0 else 8))
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_aspect('equal')
    ax.axis('off')
    for i in range(ny):
        for j in range(nx):
            room = layout[i][j]
            color = ROOM_COLORS.get(room, "#94a3b8")
            rect = mpatches.Rectangle((j, ny-1-i), 1, 1, linewidth=2, edgecolor='white', facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            ax.text(j+0.5, ny-1-i+0.5, room[:8], ha='center', va='center', fontsize=7, color='black', weight='bold')
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
        i1 = st.number_input("Row (first room)", 0, ny-1, 0, key="r1")
        j1 = st.number_input("Col (first room)", 0, nx-1, 0, key="c1")
    with cols[1]:
        i2 = st.number_input("Row (second room)", 0, ny-1, 0, key="r2")
        j2 = st.number_input("Col (second room)", 0, nx-1, 0, key="c2")
    with cols[2]:
        if st.button("Swap Rooms"):
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
                room = grid[i][j]
                for (x1,y1),(x2,y2) in [((j,i),(j+1,i)),((j+1,i),(j+1,i+1)),((j,i+1),(j+1,i+1)),((j,i),(j,i+1))]:
                    wall = {"type":"IfcWall","name":f"Wall_F{f}_R{i}{j}",
                            "coordinates":{"start":{"x":x1*span,"y":y1*span,"z":f*3},"end":{"x":x2*span,"y":y2*span,"z":f*3}},"height":3}
                    elements.append(wall)
                slab = {"type":"IfcSlab","name":f"Slab_F{f}_R{i}{j}",
                        "coordinates":{"x":j*span,"y":i*span,"z":f*3},"width":span,"depth":span}
                elements.append(slab)
    return {"project_name":f"ARC_{design['id']}","mep_data":design["mep"],"elements":elements}

# ------------------------------------------------------------
# SIDEBAR NAVIGATION & CONFIGURATION MATRIX
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"**{st.session_state.username}** (`{st.session_state.role}`)")
    nav = st.pills("Workspace", ["Control Hub", "Synthesis Lab"], default="Control Hub")
    st.markdown("---")

    if st.session_state.role == "admin":
        with st.expander("Forex Rates (Admin)"):
            st.write("Current rates:")
            for country_k, fx in st.session_state.regional_fx.items():
                st.write(f"{country_k}: {fx['symbol']} {fx['rate_to_usd']:,.2f}")
            for country_k in st.session_state.regional_fx.keys():
                new_val = st.number_input(
                    f"{country_k} rate",
                    value=st.session_state.regional_fx[country_k]["rate_to_usd"],
                    step=0.01,
                    format="%.2f",
                    key=f"fx_{country_k}"
                )
                if new_val != st.session_state.regional_fx[country_k]["rate_to_usd"]:
                    st.session_state.regional_fx[country_k]["rate_to_usd"] = new_val

    with st.expander("Configuration Matrix", expanded=True):
        country = st.selectbox("Region", list(st.session_state.regional_fx.keys()))
        domain = st.selectbox("Category", list(ARCH_DOMAINS.keys()))
        btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
        plot = st.slider("Plot (m²)", 200, 5000, 800, 50)
        floors = st.slider("Storeys", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)
        soil = st.selectbox("Soil Profile", list(SOIL_PROFILES.keys()))
        material = st.pills("Framing", [
            "Reinforced Concrete (Eurocode 2)",
            "Structural Steel Profile (Eurocode 3)",
            "Timber Profile (Eurocode 5)"
        ], default="Reinforced Concrete (Eurocode 2)")
        g_k = st.slider("Permanent Load (kN/m²)", 3.0, 8.0, 5.5, 0.5)
        default_q = 2.5 if domain=="Residential" else (4.0 if domain=="Commercial" else 7.5)
        q_k = st.slider("Imposed Load (kN/m²)", 1.5, 10.0, default_q, 0.5)
        steel = st.selectbox("Steel Section", [
            "UB 254x146x31","UB 305x165x40","UC 254x254x73","UC 305x305x97"
        ]) if "Steel" in material else None
        seismic = st.selectbox("Seismic Zone", list(SEISMIC_ZONES.keys()), index=1)
        wind = st.selectbox("Wind Zone", list(WIND_ZONES.keys()), index=1)

    trigger = st.sidebar.button("Execute Generation", type="primary", use_container_width=True)
    if st.button("Logout"):
        logout()

# ------------------------------------------------------------
# MAIN WORKSPACE
# ------------------------------------------------------------
if nav == "Control Hub":
    st.title("Regional Telemetry Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KES", st.session_state.regional_fx["Kenya"]["rate_to_usd"])
    col2.metric("UGX", st.session_state.regional_fx["Uganda"]["rate_to_usd"])
    col3.metric("TZS", st.session_state.regional_fx["Tanzania"]["rate_to_usd"])
    col4.metric("SSP", st.session_state.regional_fx["South Sudan"]["rate_to_usd"])
    st.markdown("---")
    
    my_designs = load_user_designs_db(st.session_state.username, st.session_state.role)
    colA, colB = st.columns(2)
    colA.metric("Saved Archetypes", len(my_designs))
    colB.metric("DB Storage Engine", "PostgreSQL" if DATABASE_URL else "SQLite (Local)")
    
    recent_logs = get_recent_logs_db(5)
    if recent_logs:
        st.subheader("System Event Stream")
        for e in recent_logs:
            st.caption(f"{e['time'][-11:-3]} — {e['msg']} ({e.get('user','')})")

elif nav == "Synthesis Lab":
    st.title("Generative Synthesis & Analysis Engine")
    if trigger:
        with st.spinner("Synthesizing Structural & MEP Models..."):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            design = ensure_design_compatibility(design)
            st.session_state.active_design = design
            save_design_db(design)
            log_event_db(st.session_state.username, f"Generated Design #{design['id']}")

    if st.session_state.active_design:
        d = ensure_design_compatibility(st.session_state.active_design)
        
        st.subheader(f"Active Design: {d['id']} — {d['type']}")
        
        # Design Sign-Off & Approval Workflow for Engineers/Admins
        if st.session_state.role in ["admin", "engineer"]:
            col_stat, col_btn = st.columns([3, 1])
            with col_stat:
                st.info(f"Status: **{d.get('status', 'PENDING')}** | Signed off by: {d.get('approved_by', 'None')}")
            with col_btn:
                if d.get("status") != "APPROVED" and st.button("Sign-Off & Approve"):
                    d["status"] = "APPROVED"
                    d["approved_by"] = st.session_state.username
                    update_design_status_db(d["id"], "APPROVED", st.session_state.username)
                    log_event_db(st.session_state.username, f"Approved Design #{d['id']}")
                    st.success("Design approved!")
                    st.rerun()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Region", d["country"])
        col2.metric("GFA", f"{d['total_gfa']:,.0f} m²")
        col3.metric("Floors", d["floors"])
        col4.metric("Doors/Windows", f"{d['doors']}/{d['windows']}")

        tabs = st.tabs([
            "2D Interactive", "3D Isometric", "Structural Passport", "MEP Passport",
            "Zoning", "BoQ & Forex", "Forex Forecast", "Cost Sensitivity", "Export IFC"
        ])
        
        with tabs[0]:
            st.markdown("### Interactive 2D Blueprint")
            d = draw_interactive_blueprint(d)
            st.session_state.active_design = d
        with tabs[1]:
            draw_3d_isometric_view(d)
        with tabs[2]:
            st.markdown("### Eurocode Structural Analysis")
            st.json(d["analysis"])
        with tabs[3]:
            st.markdown("### Mechanical, Electrical & Plumbing (MEP) Passport")
            mep = d["mep"]
            colM1, colM2, colM3 = st.columns(3)
            colM1.metric("HVAC Cooling Load", f"{mep['hvac_cooling_kw']} kW ({mep['hvac_capacity_tons']} Tons)")
            colM2.metric("Electrical Demand", f"{mep['electrical_demand_kva']} kVA")
            colM3.metric("Daily Water Demand", f"{mep['daily_water_demand_liters']:,.0f} L/day")
            st.caption(f"Estimated Peak Plumbing Flow: **{mep['peak_plumbing_flow_ls']} L/s** | Occupancy Estimate: **{mep['estimated_occupants']} persons**")
        with tabs[4]:
            zon = d["zoning"]
            st.write(f"Coverage: {zon['coverage']} (max {ARCH_DOMAINS[d['domain']]['max_coverage']}) — {'OK' if zon['coverage_ok'] else 'VIOLATION'}")
            st.write(f"FAR: {zon['far']} (max {ARCH_DOMAINS[d['domain']]['max_far']}) — {'OK' if zon['far_ok'] else 'VIOLATION'}")
            st.write(f"Overall: {zon['status']}")
        with tabs[5]:
            boq = d["boq"]
            colA, colB = st.columns(2)
            with colA:
                st.metric("Substructure", f"${boq['substructure']:,.2f}")
                st.metric("Superstructure", f"${boq['superstructure']:,.2f}")
                st.metric("MEP Trade Services", f"${boq['mep_services']:,.2f}")
                st.metric("Finishes", f"${boq['finishes']:,.2f}")
            with colB:
                st.metric("Total USD", f"${boq['total_usd']:,.2f}")
                st.metric(f"Total {boq['local_currency']}", f"{boq['symbol']} {boq['total_local']:,.2f}")
        with tabs[6]:
            st.subheader("Forex Rate Forecast")
            cur = st.selectbox("Currency", list(st.session_state.regional_fx.keys()), key="forex_cur")
            steps = st.slider("Days Ahead", 1, 90, 30)
            base_rate = st.session_state.regional_fx[cur]["rate_to_usd"]
            np.random.seed(42)
            history = base_rate + np.random.normal(0, 0.5, 90).cumsum()
            forecast = [history[-1]] * steps
            forecast_dates = [datetime.now() + timedelta(days=i+1) for i in range(steps)]
            hist_dates = [datetime.now() - timedelta(days=i) for i in range(90,0,-1)]
            
            fig, ax = plt.subplots(figsize=(8,4))
            ax.plot(hist_dates, history, label="Historical", color="#888")
            ax.plot(forecast_dates, forecast, "o-", color="#ddd", label="Forecast")
            ax.legend()
            ax.set_facecolor('#111111')
            fig.patch.set_facecolor('#000000')
            ax.tick_params(colors='white')
            st.pyplot(fig)
        with tabs[7]:
            st.subheader("Cost Sensitivity Analysis")
            base_rates = {
                "Reinforced Concrete (Eurocode 2)":350,
                "Structural Steel Profile (Eurocode 3)":400,
                "Timber Profile (Eurocode 5)":280
            }
            new_rates = {}
            for mat, rate in base_rates.items():
                new_rates[mat] = st.slider(mat, 200, 600, rate, 10)
            updated_boq = compute_detailed_forex_boq(d, rate_overrides=new_rates)
            colA, colB = st.columns(2)
            with colA: st.metric("Updated Total USD", f"${updated_boq['total_usd']:,.2f}")
            with colB: st.metric(f"Updated {updated_boq['local_currency']}", f"{updated_boq['symbol']} {updated_boq['total_local']:,.2f}")
        with tabs[8]:
            st.subheader("Export IFC / BIM Model Data")
            ifc_json = generate_ifc_json(d)
            st.download_button(
                "Download IFC-like JSON",
                data=json.dumps(ifc_json, indent=2),
                file_name=f"ARC_{d['id']}_ifc.json",
                mime="application/json"
            )
            st.json(ifc_json, expanded=False)
    else:
        st.info("Configure parameters in the sidebar and click 'Execute Generation'.")
