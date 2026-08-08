# =========================================================
# IMAGINE – Architectural Intellect & East African Forex Engine
# v22.0 – Studio Edition, Minimalist Login & MEP Engine
# =========================================================

import streamlit as st
import json, uuid, math, hashlib, sqlite3, random
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ------------------------------------------------------------
# PAGE CONFIG & ELEGANT DARK THEME CSS
# ------------------------------------------------------------
st.set_page_config(page_title="Imagine Studio", page_icon="🏛️", layout="wide")

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
        max-width: 440px;
        margin: 3rem auto 0 auto;
        padding: 2.5rem;
        background: rgba(18, 22, 31, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h2 {
        font-size: 1.5rem;
        font-weight: 500;
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

    /* Minimalist Metrics & Cards */
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
  <text x="66" y="58" font-family="-apple-system, sans-serif" font-weight="400" font-size="9" fill="#94a3b8" letter-spacing="2">ARCHITECTURAL INTELLECT</text>
</svg>
"""

# ------------------------------------------------------------
# DATABASE & AUTHENTICATION
# ------------------------------------------------------------
USER_DB = Path("arc_users.db")

def init_user_db():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password_hash TEXT NOT NULL,
                  role TEXT DEFAULT 'user',
                  email TEXT DEFAULT '')''')
    try:
        c.execute("SELECT salt FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN salt TEXT NOT NULL DEFAULT 'legacy_no_salt'")
        conn.commit()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        salt = uuid.uuid4().hex
        admin_hash = hash_password("admin123", salt)
        c.execute("INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)",
                  ("admin", admin_hash, salt, "admin", "admin@arc.studio"))
    conn.commit()
    conn.close()

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

def authenticate_user(username, password):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    try:
        c.execute("SELECT password_hash, salt, role FROM users WHERE username=?", (username,))
        row = c.fetchone()
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN salt TEXT NOT NULL DEFAULT 'legacy_no_salt'")
        conn.commit()
        c.execute("SELECT password_hash, salt, role FROM users WHERE username=?", (username,))
        row = c.fetchone()
    conn.close()
    if row:
        db_hash, salt, role = row
        if salt == "legacy_no_salt":
            if hashlib.sha256(password.encode()).hexdigest() == db_hash:
                new_salt = uuid.uuid4().hex
                new_hash = hash_password(password, new_salt)
                conn = sqlite3.connect(USER_DB)
                conn.execute("UPDATE users SET password_hash=?, salt=? WHERE username=?",
                             (new_hash, new_salt, username))
                conn.commit()
                conn.close()
                return True, role
        else:
            if hash_password(password, salt) == db_hash:
                return True, role
    return False, None

def register_user(username, password, email="", role="user"):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    try:
        salt = uuid.uuid4().hex
        pwd_hash = hash_password(password, salt)
        c.execute("INSERT INTO users (username, password_hash, salt, role, email) VALUES (?,?,?,?,?)",
                  (username, pwd_hash, salt, role, email))
        conn.commit()
        return True, f"User '{username}' created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

init_user_db()

# ------------------------------------------------------------
# SESSION STATE & REFINED LOGIN PORTAL
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="login-header">{LOGO_SVG}<p>Sign in to your design studio space</p></div>', unsafe_allow_html=True)
        
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
                            st.rerun()
                        else:
                            st.error("Invalid credentials provided.")
                            
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                new_u = st.text_input("New Username", placeholder="e.g. j_doe", key="s_u")
                new_p = st.text_input("Choose Password", type="password", placeholder="••••••••", key="s_p")
                new_e = st.text_input("Email Address", placeholder="name@firm.com", key="s_e")
                register = st.form_submit_button("Register New Account")
                
                if register:
                    if not new_u or not new_p:
                        st.warning("Username and password are required.")
                    else:
                        ok, msg = register_user(new_u, new_p, new_e)
                        if ok:
                            st.success(msg + " You can now sign in.")
                        else:
                            st.error(msg)
                            
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    render_login_portal()
    st.stop()

def logout():
    for key in ["authenticated", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------------------------------------------------------------
# DOMAIN DATA & REGIONAL CONSTANTS
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

MEMORY_FILE = Path("arc_studio_v21.json")

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"designs":[], "logs":[], "forex_rates": REGIONAL_FX_DEFAULTS.copy()}

def save_memory(mem):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2), encoding="utf-8")

def log_event(msg):
    mem = st.session_state.memory
    mem["logs"].append({
        "time": datetime.now().isoformat(),
        "user": st.session_state.username,
        "msg": msg
    })
    save_memory(mem)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()
    if "forex_rates" in st.session_state.memory:
        st.session_state.regional_fx = st.session_state.memory["forex_rates"]
    else:
        st.session_state.memory["forex_rates"] = st.session_state.regional_fx

if "active_design" not in st.session_state:
    st.session_state.active_design = None

# ------------------------------------------------------------
# MEP & STRUCTURAL CALCULATIONS ENGINE
# ------------------------------------------------------------
def run_mep_analysis(design):
    gfa = design["total_gfa"]
    domain = design.get("domain", "Residential")
    baths = design.get("bathrooms", 2)
    
    # 1. Mechanical (HVAC)
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
    
    # 3. Plumbing & Sanitation Engine
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
        "max_moment_kNm": round(M,2),
        "footing_width_m": round(footing_width,2),
        "wind_base_shear_kN": round(wind_force,2),
        "drift_mm": round(drift,2),
        "seismic_base_shear_kN": round(seismic["PGA"]*floors*100*span*5,2),
        "status": "PASS" if M<100 else "REVIEW"
    }

def verify_zoning_laws(design):
    max_cov = ARCH_DOMAINS[design["domain"]]["max_coverage"]
    max_far = ARCH_DOMAINS[design["domain"]]["max_far"]
    cov = design["ground_footprint"] / design["plot_size"]
    far = design["total_gfa"] / design["plot_size"]
    return {
        "coverage": round(cov,2),
        "coverage_ok": cov <= max_cov,
        "far": round(far,2),
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
    
    if "mep" not in design: 
        design["mep"] = run_mep_analysis(design)
    if "analysis" not in design: 
        design["analysis"] = run_eurocode_analysis(design)
    if "zoning" not in design: 
        design["zoning"] = verify_zoning_laws(design)
    if "boq" not in design: 
        design["boq"] = compute_detailed_forex_boq(design)
        
    return design

for i, d_item in enumerate(st.session_state.memory.get("designs", [])):
    st.session_state.memory["designs"][i] = ensure_design_compatibility(d_item)

def refresh_forex_rates():
    base = {"Kenya": 129.49, "Uganda": 3665.20, "Tanzania": 2625.00, "South Sudan": 4626.40}
    for country, rate in base.items():
        new_rate = rate * random.uniform(0.98, 1.02)
        st.session_state.regional_fx[country]["rate_to_usd"] = round(new_rate, 2)
    st.session_state.memory["forex_rates"] = st.session_state.regional_fx
    save_memory(st.session_state.memory)
    log_event("Forex rates updated (simulated live change)")

# ------------------------------------------------------------
# VISUALIZATIONS
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
            rect = mpatches.Rectangle((j, ny-1-i), 1, 1, linewidth=2, edgecolor='white',
                                     facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            ax.text(j+0.5, ny-1-i+0.5, room[:8], ha='center', va='center',
                    fontsize=7, color='black', weight='bold')
    if overlay_design:
        overlay = overlay_design["layout"]["grid"]
        ony = min(ny, overlay_design["layout"]["ny"])
        onx = min(nx, overlay_design["layout"]["nx"])
        for i in range(ony):
            for j in range(onx):
                room = overlay[i][j]
                color = ROOM_COLORS.get(room, "#94a3b8")
                rect = mpatches.Rectangle((j, ny-1-i), 1, 1, linewidth=1, edgecolor='red',
                                         facecolor=color, alpha=0.3, hatch='//')
                ax.add_patch(rect)
    ax.annotate('N', xy=(0.5, ny+0.2), fontsize=14, color='white', ha='center',
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
                room = grid[i][j]
                for (x1,y1),(x2,y2) in [((j,i),(j+1,i)),((j+1,i),(j+1,i+1)),((j,i+1),(j+1,i+1)),((j,i),(j,i+1))]:
                    wall = {"type":"IfcWall","name":f"Wall_F{f}_R{i}{j}",
                            "coordinates":{"start":{"x":x1*span,"y":y1*span,"z":f*3},"end":{"x":x2*span,"y":y2*span,"z":f*3}},"height":3}
                    elements.append(wall)
                slab = {"type":"IfcSlab","name":f"Slab_F{f}_R{i}{j}",
                        "coordinates":{"x":j*span,"y":i*span,"z":f*3},"width":span,"depth":span}
                elements.append(slab)
    return {"project_name":f"ARC_{design['id']}","elements":elements}

# ------------------------------------------------------------
# SIDEBAR NAVIGATION & CONTROLS
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"**User:** `{st.session_state.username}` ({st.session_state.role.upper()})")
    nav = st.pills("Workspace", ["Control Hub", "Synthesis Lab"], default="Control Hub")
    st.markdown("---")

    if st.session_state.role == "admin":
        with st.expander("Forex Rates (Admin Control)"):
            st.write("Live FX Table:")
            for country, fx in st.session_state.regional_fx.items():
                st.write(f"{country}: {fx['symbol']} {fx['rate_to_usd']:,.2f}")
            if st.button("Simulate Market Movement"):
                refresh_forex_rates()
                st.success("Rates updated!")
                st.rerun()
            for country in st.session_state.regional_fx.keys():
                new_val = st.number_input(
                    f"{country} Rate",
                    value=st.session_state.regional_fx[country]["rate_to_usd"],
                    step=0.01,
                    format="%.2f",
                    key=f"fx_{country}"
                )
                if new_val != st.session_state.regional_fx[country]["rate_to_usd"]:
                    st.session_state.regional_fx[country]["rate_to_usd"] = new_val
                    st.session_state.memory["forex_rates"] = st.session_state.regional_fx
                    save_memory(st.session_state.memory)

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
    my_designs = [d for d in st.session_state.memory["designs"] if d.get("username") == st.session_state.username]
    st.metric("My Saved Projects", len(my_designs))
    
    if st.session_state.memory["logs"]:
        st.subheader("System Activity Log")
        for e in reversed(st.session_state.memory["logs"][-5:]):
            st.caption(f"**{e['time'][-8:-3]}** — {e['msg']} *(by {e.get('user','')})*")

elif nav == "Synthesis Lab":
    st.title("Generative Synthesis & Analysis Engine")
    
    if trigger:
        with st.spinner("Synthesizing building model & calculating MEP/Eurocode metrics..."):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            design = ensure_design_compatibility(design)
            st.session_state.active_design = design
            st.session_state.memory["designs"].append(design)
            log_event(f"Generated Archetype #{design['id']}")
            save_memory(st.session_state.memory)

    if st.session_state.active_design:
        d = ensure_design_compatibility(st.session_state.active_design)
        if d.get("username") != st.session_state.username:
            st.warning("Active design belongs to another user space.")
        else:
            st.subheader(f"Active Model: #{d['id']} — {d['type']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Target Region", d["country"])
            col2.metric("Gross Floor Area", f"{d['total_gfa']:,.0f} m²")
            col3.metric("Storeys", d["floors"])
            col4.metric("Doors / Windows", f"{d['doors']} / {d['windows']}")

            tabs = st.tabs([
                "2D Interactive", "3D Isometric", "Structural Passport", "MEP Passport",
                "Zoning", "BoQ & Forex", "Forex Forecast", "Drift Animation",
                "Cost Sensitivity", "Design Compare", "Export IFC"
            ])
            
            with tabs[0]:
                st.markdown("### Interactive Floorplan Grid")
                d = draw_interactive_blueprint(d)
                st.session_state.active_design = d
                save_memory(st.session_state.memory)
                
            with tabs[1]:
                draw_3d_isometric_view(d)
                
            with tabs[2]:
                st.json(d["analysis"])
                
            with tabs[3]:
                st.markdown("### MEP Infrastructure & Service Passport")
                mep = d.get("mep") or run_mep_analysis(d)
                d["mep"] = mep
                
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
                    st.write(f"**Transformer Min:** {mep['electrical']['transformer_rating_kva']} kVA")
                    st.write(f"**Standby Genset:** {mep['electrical']['generator_rating_kva']} kVA")
                    
                with col_m3:
                    st.markdown("#### Plumbing & Sanitation")
                    st.metric("Daily Water Demand", f"{mep['plumbing']['daily_water_demand_liters']:,.0f} L/day")
                    st.write(f"**Est. Occupancy:** {mep['plumbing']['est_occupants']} Persons")
                    st.write(f"**Storage Reserve:** {mep['plumbing']['storage_tank_capacity_m3']} m³")
                    st.write(f"**Fixture Units:** {mep['plumbing']['total_wsfu']} WSFU / {mep['plumbing']['total_dfu']} DFU")
                    
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
                my_designs_list = [d for d in st.session_state.memory["designs"] if d.get("username")==st.session_state.username]
                if len(my_designs_list) < 2:
                    st.info("Create and save at least two designs to run side-by-side comparison.")
                else:
                    ids = [f"{d['id']} - {d['type']}" for d in my_designs_list]
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
                st.subheader("IFC Schema Export")
                ifc_json = generate_ifc_json(d)
                st.download_button(
                    "Download BIM IFC-JSON",
                    data=json.dumps(ifc_json, indent=2),
                    file_name=f"IMAGINE_{d['id']}_ifc.json",
                    mime="application/json"
                )
                st.json(ifc_json, expanded=False)
    else:
        st.info("Configure design parameters in the sidebar and click **Execute Generative Model**.")
