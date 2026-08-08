# =========================================================
# IMAGINE – Architectural Intellect & East African Forex Engine
# v21.8 – Black Edition, Imaginative Logo, Minimal UI
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
    /* Remove glows and bright borders */
    .stApp, .stSidebar { box-shadow: none; }
    .stMetric { box-shadow: none; }
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------
# IMAGINATIVE LOGO – Architectural compass + minimal wordmark
# ------------------------------------------------------------
LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80" width="240" height="64">
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#888"/>
      <stop offset="100%" stop-color="#ccc"/>
    </linearGradient>
  </defs>
  <!-- Compass mark -->
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
# DATABASE MIGRATION & AUTH (unchanged)
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
        return True, f"User '{username}' created."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT username, role, email FROM users")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(username):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

init_user_db()

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

# ------------------------------------------------------------
# LOGIN / SIGN UP PAGE (Black, logo only)
# ------------------------------------------------------------
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
            if st.form_submit_button("Sign Up"):
                if not new_u or not new_p:
                    st.error("Username and password required.")
                else:
                    ok, msg = register_user(new_u, new_p, new_e)
                    if ok:
                        st.success(msg + " You can now login.")
                    else:
                        st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    login_page()
    st.stop()

# ------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------
def logout():
    for key in ["authenticated", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------------------------------------------------------------
# DYNAMIC FOREX RATES (unchanged)
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

# ------------------------------------------------------------
# MEMORY & LOGGING (unchanged)
# ------------------------------------------------------------
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
# CORE GENERATION FUNCTIONS (unchanged)
# ------------------------------------------------------------
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
    else:
        d = design["loads"]
        if "seismic_zone" not in d: d["seismic_zone"] = "Moderate (PGA=0.15g)"
        if "wind_zone" not in d: d["wind_zone"] = "Moderate (28 m/s)"
        if "g_k" not in d: d["g_k"] = 5.5
        if "q_k" not in d: d["q_k"] = 2.5 if design.get("domain")=="Residential" else (4.0 if design.get("domain")=="Commercial" else 7.5)
        if "steel_section" not in d: d["steel_section"] = None
    if "analysis" not in design: design["analysis"] = run_eurocode_analysis(design)
    if "zoning" not in design: design["zoning"] = verify_zoning_laws(design)
    if "boq" not in design: design["boq"] = compute_detailed_forex_boq(design)
    return design

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
        "Reinforced Concrete (Eurocode 2)":350,
        "Structural Steel Profile (Eurocode 3)":400,
        "Timber Profile (Eurocode 5)":280
    }
    if rate_overrides is None:
        rate_overrides = {}
    rate_per_m2 = rate_overrides.get(design["material_frame"], base_rates.get(design["material_frame"], 350))
    gfa = design["total_gfa"]
    substructure = 0.15 * rate_per_m2 * gfa
    superstructure = 0.70 * rate_per_m2 * gfa
    finishes = 0.10 * rate_per_m2 * gfa
    preliminaries = 0.05 * rate_per_m2 * gfa
    total_usd = (substructure + superstructure + finishes + preliminaries) * mult * (1 + risk)
    return {
        "substructure": round(substructure,2),
        "superstructure": round(superstructure,2),
        "finishes": round(finishes,2),
        "preliminaries": round(preliminaries,2),
        "total_usd": round(total_usd,2),
        "total_local": round(total_usd * fx["rate_to_usd"],2),
        "local_currency": fx["currency"],
        "symbol": fx["symbol"],
        "rate_used": fx["rate_to_usd"]
    }

def refresh_forex_rates():
    base = {
        "Kenya": 129.49,
        "Uganda": 3665.20,
        "Tanzania": 2625.00,
        "South Sudan": 4626.40
    }
    for country, rate in base.items():
        new_rate = rate * random.uniform(0.98, 1.02)
        st.session_state.regional_fx[country]["rate_to_usd"] = round(new_rate, 2)
    st.session_state.memory["forex_rates"] = st.session_state.regional_fx
    save_memory(st.session_state.memory)
    log_event("Forex rates updated (simulated live change)")

# ------------------------------------------------------------
# 2D & 3D VISUALS (unchanged)
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
    return {"project_name":f"ARC_{design['id']}","elements":elements}

# ------------------------------------------------------------
# SIDEBAR – LOGO ONLY, no other images
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown(f"**{st.session_state.username}** ({st.session_state.role})")
    nav = st.pills("Workspace", ["Control Hub", "Synthesis Lab"], default="Control Hub")
    st.markdown("---")

    if st.session_state.role == "admin":
        with st.expander("Forex Rates (Admin)"):
            st.write("Current rates:")
            for country, fx in st.session_state.regional_fx.items():
                st.write(f"{country}: {fx['symbol']} {fx['rate_to_usd']:,.2f}")
            if st.button("Simulate Live Rate Change"):
                refresh_forex_rates()
                st.success("Rates updated!")
                st.rerun()
            for country in st.session_state.regional_fx.keys():
                new_val = st.number_input(
                    f"{country} rate",
                    value=st.session_state.regional_fx[country]["rate_to_usd"],
                    step=0.01,
                    format="%.2f",
                    key=f"fx_{country}"
                )
                if new_val != st.session_state.regional_fx[country]["rate_to_usd"]:
                    st.session_state.regional_fx[country]["rate_to_usd"] = new_val
                    st.session_state.memory["forex_rates"] = st.session_state.regional_fx
                    save_memory(st.session_state.memory)

    with st.expander("Configuration Matrix", expanded=True):
        country = st.selectbox("Region", list(st.session_state.regional_fx.keys()))
        domain = st.selectbox("Category", list(ARCH_DOMAINS.keys()))
        btype = st.selectbox("Typology", ARCH_DOMAINS[domain]["types"])
        plot = st.slider("Plot (m²)", 200, 5000, 800, 50)
        floors = st.slider("Storeys", 1, 12, 3)
        baths = st.slider("Bathrooms", 1, 10, 2)
        soil = st.selectbox("Soil", list(SOIL_PROFILES.keys()))
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
# MAIN WORKSPACE (unchanged functionality, cosmetic text)
# ------------------------------------------------------------
if nav == "Control Hub":
    st.title("Regional Telemetry Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KES", st.session_state.regional_fx["Kenya"]["rate_to_usd"])
    col2.metric("UGX", st.session_state.regional_fx["Uganda"]["rate_to_usd"])
    col3.metric("TZS", st.session_state.regional_fx["Tanzania"]["rate_to_usd"])
    col4.metric("SSP", st.session_state.regional_fx["South Sudan"]["rate_to_usd"])
    st.markdown("---")
    my_designs = [d for d in st.session_state.memory["designs"] if d.get("username") == st.session_state.username]
    st.metric("My Archetypes", len(my_designs))
    if st.session_state.memory["logs"]:
        st.subheader("Recent Events")
        for e in reversed(st.session_state.memory["logs"][-5:]):
            st.caption(f"{e['time'][-11:-3]} — {e['msg']} ({e.get('user','')})")

elif nav == "Synthesis Lab":
    st.title("Generative Synthesis & Analysis")
    if trigger:
        with st.spinner("Synthesizing..."):
            design = generate_building_model(
                domain, btype, floors, baths, country, material, plot, soil,
                g_k, q_k, steel, seismic, wind, st.session_state.username
            )
            design = ensure_design_compatibility(design)
            st.session_state.active_design = design
            st.session_state.memory["designs"].append(design)
            log_event(f"Generated #{design['id']}")
            save_memory(st.session_state.memory)

    if st.session_state.active_design:
        d = ensure_design_compatibility(st.session_state.active_design)
        if d.get("username") != st.session_state.username:
            st.warning("Design not owned by current user.")
        else:
            st.subheader(f"Active Design: {d['id']} — {d['type']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Region", d["country"])
            col2.metric("GFA", f"{d['total_gfa']:,.0f} m²")
            col3.metric("Floors", d["floors"])
            col4.metric("Doors/Windows", f"{d['doors']}/{d['windows']}")

            tabs = st.tabs([
                "2D Interactive", "3D Isometric", "Structural Passport", "Zoning",
                "BoQ & Forex", "Forex Forecast", "Drift Animation", "Cost Sensitivity",
                "Design Compare", "Export IFC"
            ])
            with tabs[0]:
                st.markdown("### Interactive 2D Blueprint")
                d = draw_interactive_blueprint(d)
                st.session_state.active_design = d
                save_memory(st.session_state.memory)
            with tabs[1]:
                draw_3d_isometric_view(d)
            with tabs[2]:
                st.json(d["analysis"])
            with tabs[3]:
                zon = d["zoning"]
                st.write(f"Coverage: {zon['coverage']} (max {ARCH_DOMAINS[d['domain']]['max_coverage']}) — {'OK' if zon['coverage_ok'] else 'VIOLATION'}")
                st.write(f"FAR: {zon['far']} (max {ARCH_DOMAINS[d['domain']]['max_far']}) — {'OK' if zon['far_ok'] else 'VIOLATION'}")
                st.write(f"Overall: {zon['status']}")
            with tabs[4]:
                boq = d["boq"]
                colA, colB = st.columns(2)
                with colA:
                    st.metric("Substructure", f"${boq['substructure']:,.2f}")
                    st.metric("Superstructure", f"${boq['superstructure']:,.2f}")
                    st.metric("Finishes", f"${boq['finishes']:,.2f}")
                with colB:
                    st.metric("Total USD", f"${boq['total_usd']:,.2f}")
                    st.metric(f"Total {boq['local_currency']}", f"{boq['symbol']} {boq['total_local']:,.2f}")
            with tabs[5]:
                st.subheader("Forex Rate Forecast")
                cur = st.selectbox("Currency", list(st.session_state.regional_fx.keys()), key="forex_cur")
                horizon = st.radio("Horizon", ["short","medium","long"], horizontal=True, key="fx_hor")
                steps_map = {"short":7,"medium":30,"long":90}
                steps = st.slider("Days", 1, 90, steps_map[horizon])
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
                st.metric("Current", f"{st.session_state.regional_fx[cur]['symbol']} {base_rate}")
                st.metric(f"{steps}-day avg", f"{st.session_state.regional_fx[cur]['symbol']} {np.mean(forecast):.2f}")
                trend = "rising" if smoothed[-1] > np.mean(smoothed[-30:]) else "falling"
                st.write(f"Trend: {trend}")
                fig, ax = plt.subplots(figsize=(8,4))
                ax.plot(hist_dates, history, label="Historical", color="#888")
                ax.plot(hist_dates, smoothed, "--", color="#aaa", label="Smoothed")
                ax.plot(forecast_dates, forecast, "o-", color="#ddd", label="Forecast")
                ax.legend()
                ax.set_facecolor('#111111')
                fig.patch.set_facecolor('#000000')
                ax.tick_params(colors='white')
                st.pyplot(fig)
            with tabs[6]:
                st.subheader("Wind Drift Animation")
                drift_range = st.slider("Drift amplitude factor", 0.0, 1.0, 0.3, 0.05)
                draw_3d_isometric_view(d, drift_factor=drift_range)
                st.caption("Slide to simulate sway under wind load.")
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
                with colB: st.metric(f"Updated {updated_boq['local_currency']}",
                                     f"{updated_boq['symbol']} {updated_boq['total_local']:,.2f}")
            with tabs[8]:
                st.subheader("Design Comparison")
                my_designs_list = [d for d in st.session_state.memory["designs"] if d.get("username")==st.session_state.username]
                if len(my_designs_list) < 2:
                    st.warning("Save at least two designs to compare.")
                else:
                    ids = [f"{d['id']} - {d['type']}" for d in my_designs_list]
                    d1_idx = st.selectbox("Design A", range(len(ids)), format_func=lambda x:ids[x])
                    d2_idx = st.selectbox("Design B", range(len(ids)), index=min(1,len(ids)-1),
                                         format_func=lambda x:ids[x])
                    if st.button("Compare"):
                        d1 = my_designs_list[d1_idx]
                        d2 = my_designs_list[d2_idx]
                        st.write("### Overlay Blueprint")
                        st.image(draw_2d_blueprint(d1, overlay_design=d2), use_container_width=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("A GFA", d1["total_gfa"])
                            st.metric("A Cost USD", d1["boq"]["total_usd"])
                            st.metric("A Floors", d1["floors"])
                        with col2:
                            st.metric("B GFA", d2["total_gfa"])
                            st.metric("B Cost USD", d2["boq"]["total_usd"])
                            st.metric("B Floors", d2["floors"])
            with tabs[9]:
                st.subheader("Export to IFC/Revit JSON")
                ifc_json = generate_ifc_json(d)
                st.download_button(
                    "Download IFC-like JSON",
                    data=json.dumps(ifc_json, indent=2),
                    file_name=f"ARC_{d['id']}_ifc.json",
                    mime="application/json"
                )
                st.json(ifc_json, expanded=False)
    else:
        st.info("Configure parameters and press Execute Generation.")