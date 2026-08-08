import os
import sqlite3
import hashlib
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Optional PostgreSQL support
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & MODERN CSS STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Imagine | Architecture & MEP Passport Engine",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def inject_custom_css():
    st.markdown("""
    <style>
    /* Dark Modern Theme Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Login Card Glassmorphism */
    .login-card {
        background: rgba(22, 27, 34, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 12px 32px 0 rgba(0, 0, 0, 0.37);
        max-width: 480px;
        margin: 2rem auto;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .login-subtitle {
        color: #8b949e;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Sample Credentials Badge Box */
    .demo-credentials-box {
        background: rgba(56, 139, 253, 0.1);
        border: 1px solid rgba(56, 139, 253, 0.3);
        border-radius: 8px;
        padding: 0.85rem;
        margin-top: 1.5rem;
        font-size: 0.85rem;
        color: #58a6ff;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: #ffffff;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# -----------------------------------------------------------------------------
# 2. DATABASE ENGINE & DATA SEEDING
# -----------------------------------------------------------------------------
def get_db_connection():
    pg_url = os.environ.get("DATABASE_URL")
    if HAS_POSTGRES and pg_url:
        try:
            conn = psycopg2.connect(pg_url)
            return conn, "postgres"
        except Exception:
            pass
    
    conn = sqlite3.connect("imagine_app.db", check_same_thread=False)
    return conn, "sqlite"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password_hash VARCHAR(256) NOT NULL,
        role VARCHAR(20) NOT NULL
    );
    """)
    
    # Designs / Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS designs (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        location VARCHAR(100),
        floors INT,
        area_per_floor REAL,
        use_type VARCHAR(50),
        mep_passport TEXT,
        created_by VARCHAR(50)
    );
    """)

    # Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR(50),
        action VARCHAR(255)
    );
    """ if db_type == "sqlite" else """
    CREATE TABLE IF NOT EXISTS system_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR(50),
        action VARCHAR(255)
    );
    """)
    conn.commit()

    # Seed Sample Users if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("admin", hash_password("admin123"), "admin"),
            ("engineer", hash_password("engineer123"), "engineer"),
            ("architect", hash_password("architect123"), "user"),
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?);" if db_type == "sqlite" else "INSERT INTO users VALUES (%s, %s, %s);", sample_users)
        conn.commit()

    # Seed Sample Projects & MEP Passports if empty
    cursor.execute("SELECT COUNT(*) FROM designs;")
    if cursor.fetchone()[0] == 0:
        sample_projects = [
            (
                "PRJ-001", "Nairobi Commercial Tower", "Nairobi, Kenya", 12, 1200.0, "Commercial",
                json.dumps({
                    "mech_hvac": {"cooling_load_kw": 450.0, "chillers_count": 2, "ventilation_rate_cfm": 18000},
                    "elec_power": {"connected_load_kva": 650.0, "backup_generator_kva": 500, "solar_pv_kwp": 120},
                    "plumb_water": {"daily_demand_liters": 42000, "storage_tank_liters": 85000, "booster_pumps": 3}
                }),
                "architect"
            ),
            (
                "PRJ-002", "Kampala Modern Villa", "Kampala, Uganda", 3, 350.0, "Residential",
                json.dumps({
                    "mech_hvac": {"cooling_load_kw": 45.0, "vrf_units_count": 6, "ventilation_rate_cfm": 2200},
                    "elec_power": {"connected_load_kva": 65.0, "backup_generator_kva": 30, "solar_pv_kwp": 15},
                    "plumb_water": {"daily_demand_liters": 3500, "storage_tank_liters": 10000, "booster_pumps": 1}
                }),
                "engineer"
            ),
            (
                "PRJ-003", "Dar es Salaam Logistics Hub", "Dar es Salaam, Tanzania", 2, 2500.0, "Industrial",
                json.dumps({
                    "mech_hvac": {"cooling_load_kw": 300.0, "rooftop_pack_count": 4, "ventilation_rate_cfm": 35000},
                    "elec_power": {"connected_load_kva": 850.0, "backup_generator_kva": 800, "solar_pv_kwp": 300},
                    "plumb_water": {"daily_demand_liters": 15000, "storage_tank_liters": 40000, "booster_pumps": 2}
                }),
                "admin"
            )
        ]
        placeholder = "(?, ?, ?, ?, ?, ?, ?, ?)" if db_type == "sqlite" else "(%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(f"INSERT INTO designs VALUES {placeholder};", sample_projects)
        conn.commit()

    conn.close()

init_db()

# -----------------------------------------------------------------------------
# 3. HELPER COMPUTATIONS & DATA FETCHING
# -----------------------------------------------------------------------------
def verify_user(username, password):
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT password_hash, role FROM users WHERE username = ?;" if db_type == "sqlite" else "SELECT password_hash, role FROM users WHERE username = %s;"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return row[1]  # Return role
    return None

def fetch_all_projects():
    conn, _ = get_db_connection()
    df = pd.read_sql("SELECT * FROM designs", conn)
    conn.close()
    return df

def calculate_mep_passport(floors, area_per_floor, occupancy_type):
    total_area = floors * area_per_floor
    
    # MEP Calculation Factors
    factors = {
        "Residential": {"cooling_w_sqm": 110, "elec_va_sqm": 60, "water_l_person": 150, "occ_sqm_person": 20},
        "Commercial":  {"cooling_w_sqm": 140, "elec_va_sqm": 90, "water_l_person": 50,  "occ_sqm_person": 10},
        "Industrial":  {"cooling_w_sqm": 80,  "elec_va_sqm": 120, "water_l_person": 30,  "occ_sqm_person": 30},
    }.get(occupancy_type, {"cooling_w_sqm": 120, "elec_va_sqm": 80, "water_l_person": 60, "occ_sqm_person": 15})
    
    total_occ = max(1, int(total_area / factors["occ_sqm_person"]))
    cooling_kw = (total_area * factors["cooling_w_sqm"]) / 1000.0
    elec_kva = (total_area * factors["elec_va_sqm"]) / 1000.0
    water_daily = total_occ * factors["water_l_person"]
    
    return {
        "mech_hvac": {
            "cooling_load_kw": round(cooling_kw, 2),
            "cooling_tons": round(cooling_kw / 3.517, 2),
            "ventilation_rate_cfm": round(total_occ * 20, 0)
        },
        "elec_power": {
            "connected_load_kva": round(elec_kva, 2),
            "backup_generator_kva": round(elec_kva * 0.8, 2),
            "solar_pv_kwp": round(min(total_area * 0.15, elec_kva * 0.3), 2)
        },
        "plumb_water": {
            "daily_demand_liters": round(water_daily, 0),
            "storage_tank_liters": round(water_daily * 2, 0),
            "estimated_occupants": total_occ
        }
    }

# -----------------------------------------------------------------------------
# 4. SESSION STATE MANAGEMENT & AUTHENTICATION UI
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""

def render_login_page():
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-title">IMAGINE ARCHITECTURE</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">BIM, Structural Eurocode & MEP Passport Engine</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. admin, engineer, architect")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In to Engine", use_container_width=True)
            
            if submitted:
                role = verify_user(username.strip(), password.strip())
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        st.markdown("""
        <div class="demo-credentials-box">
            <b>🔑 Pre-configured Sample Accounts:</b><br>
            • <b>Admin:</b> <code>admin</code> / <code>admin123</code><br>
            • <b>Engineer:</b> <code>engineer</code> / <code>engineer123</code><br>
            • <b>Architect:</b> <code>architect</code> / <code>architect123</code>
        </div>
        """, unsafe_allow_html=True)

if not st.session_state["logged_in"]:
    render_login_page()
    st.stop()

# -----------------------------------------------------------------------------
# 5. MAIN DASHBOARD & NAVIGATION
# -----------------------------------------------------------------------------
# Sidebar Header & User Details
st.sidebar.markdown(f"### 👤 {st.session_state['username'].upper()}")
st.sidebar.caption(f"Role: **{st.session_state['role'].upper()}**")

if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.rerun()

st.sidebar.divider()
navigation = st.sidebar.radio(
    "Engine Modules",
    ["📁 Projects & MEP Explorer", "⚡ Generate MEP Passport", "🏗️ Eurocode Structural & Zoning", "📊 BoQ & Forex Engine"]
)

# -----------------------------------------------------------------------------
# MODULE 1: PROJECTS & MEP EXPLORER
# -----------------------------------------------------------------------------
if navigation == "📁 Projects & MEP Explorer":
    st.title("📁 Project Portfolio & MEP Passports")
    st.caption("Inspect pre-seeded sample projects and their integrated Mechanical, Electrical, and Plumbing passports.")
    
    df_projects = fetch_all_projects()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Select Project")
        selected_proj_name = st.selectbox("Choose Design Archetype", df_projects["name"].tolist())
        proj_data = df_projects[df_projects["name"] == selected_proj_name].iloc[0]
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>{proj_data['name']}</h4>
            <p><b>ID:</b> {proj_data['id']}</p>
            <p><b>Location:</b> {proj_data['location']}</p>
            <p><b>Type:</b> {proj_data['use_type']}</p>
            <p><b>Floors:</b> {proj_data['floors']} | <b>Floor Area:</b> {proj_data['area_per_floor']} m²</p>
            <p><b>Total Area:</b> {proj_data['floors'] * proj_data['area_per_floor']:,.0f} m²</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("MEP Passport Breakdown")
        try:
            mep_info = json.loads(proj_data["mep_passport"])
            
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.markdown("##### ❄️ Mechanical (HVAC)")
                st.metric("Cooling Load", f"{mep_info['mech_hvac'].get('cooling_load_kw', 'N/A')} kW")
                st.write(f"**Equipment:** {mep_info['mech_hvac'].get('chillers_count', mep_info['mech_hvac'].get('vrf_units_count', 'N/A'))} primary units")
                st.write(f"**Ventilation:** {mep_info['mech_hvac'].get('ventilation_rate_cfm', 'N/A')} CFM")
                
            with m_col2:
                st.markdown("##### ⚡ Electrical")
                st.metric("Connected Load", f"{mep_info['elec_power'].get('connected_load_kva', 'N/A')} kVA")
                st.write(f"**Genset Backup:** {mep_info['elec_power'].get('backup_generator_kva', 'N/A')} kVA")
                st.write(f"**Solar PV Target:** {mep_info['elec_power'].get('solar_pv_kwp', 'N/A')} kWp")

            with m_col3:
                st.markdown("##### 🚰 Plumbing & Water")
                st.metric("Daily Water Demand", f"{mep_info['plumb_water'].get('daily_demand_liters', 'N/A'):,} L/day")
                st.write(f"**Storage Capacity:** {mep_info['plumb_water'].get('storage_tank_liters', 'N/A'):,} L")
                st.write(f"**Booster Pumps:** {mep_info['plumb_water'].get('booster_pumps', 2)} pumps")
                
        except Exception as e:
            st.error("Error parsing MEP passport JSON data.")

    st.divider()

    # 3D Massing Preview Plotly
    st.subheader("📐 3D Massing & Spatial Envelope Preview")
    floors = int(proj_data["floors"])
    area = float(proj_data["area_per_floor"])
    side = np.sqrt(area)
    
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
            opacity=0.7,
            name=f"Floor {f+1}",
            showscale=False
        ))
    
    fig.update_layout(
        scene=dict(xaxis_title='Width (m)', yaxis_title='Length (m)', zaxis_title='Height (m)'),
        margin=dict(l=0, r=0, b=0, t=30),
        template="plotly_dark",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 2: GENERATE MEP PASSPORT
# -----------------------------------------------------------------------------
elif navigation == "⚡ Generate MEP Passport":
    st.title("⚡ Dynamic MEP Passport Generator")
    st.caption("Calculate Mechanical, Electrical, and Plumbing parameters for new building proposals.")
    
    with st.form("mep_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            project_name = st.text_input("Project Name", value="Kigali Innovation Hub")
            location = st.text_input("Location", value="Kigali, Rwanda")
        with col2:
            floors = st.number_input("Number of Floors", min_value=1, max_value=100, value=6)
            area_per_floor = st.number_input("Floor Area (m²)", min_value=50.0, max_value=10000.0, value=800.0)
        with col3:
            use_type = st.selectbox("Occupancy Type", ["Commercial", "Residential", "Industrial"])
            submit = st.form_submit_button("Generate MEP Passport", use_container_width=True)
            
    if submit:
        passport = calculate_mep_passport(floors, area_per_floor, use_type)
        
        st.success(f"MEP Passport generated for **{project_name}** ({use_type})!")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("#### ❄️ Mechanical (HVAC)")
            st.metric("Cooling Capacity", f"{passport['mech_hvac']['cooling_load_kw']} kW", f"{passport['mech_hvac']['cooling_tons']} Tons")
            st.write(f"• Fresh Air Rate: **{passport['mech_hvac']['ventilation_rate_cfm']} CFM**")
            
        with m2:
            st.markdown("#### ⚡ Electrical Demand")
            st.metric("Connected Power", f"{passport['elec_power']['connected_load_kva']} kVA")
            st.write(f"• Diesel Genset: **{passport['elec_power']['backup_generator_kva']} kVA**")
            st.write(f"• Recommended Solar: **{passport['elec_power']['solar_pv_kwp']} kWp**")

        with m3:
            st.markdown("#### 🚰 Plumbing & Water")
            st.metric("Water Consumption", f"{passport['plumb_water']['daily_demand_liters']:,} L/day")
            st.write(f"• Storage Buffer: **{passport['plumb_water']['storage_tank_liters']:,} L**")
            st.write(f"• Est. Occupancy: **{passport['plumb_water']['estimated_occupants']} People**")

        # Code block representation of Passport
        st.markdown("##### Passport Payload (JSON)")
        st.json(passport)

# -----------------------------------------------------------------------------
# MODULE 3: EUROCODE STRUCTURAL & ZONING
# -----------------------------------------------------------------------------
elif navigation == "🏗️ Eurocode Structural & Zoning":
    st.title("🏗️ Structural Eurocode & Zoning Verification")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Structural Load Input (EN 1991)")
        dead_load = st.slider("Permanent Load (Gk) [kN/m²]", 1.0, 10.0, 3.5)
        live_load = st.slider("Variable Load (Qk) [kN/m²]", 0.5, 7.5, 2.5)
        gamma_g = 1.35
        gamma_q = 1.50
        
        # Ultimate Limit State (ULS)
        uls_combination = (gamma_g * dead_load) + (gamma_q * live_load)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>EN 1900 ULS Design Combination</h4>
            <p><b>Ed = 1.35 Gk + 1.50 Qk</b></p>
            <h2 style="color: #58a6ff;">{uls_combination:.2f} kN/m²</h2>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("Urban Zoning Check")
        plot_area = st.number_input("Plot Area (m²)", value=2000.0)
        building_footprint = st.number_input("Building Footprint Area (m²)", value=800.0)
        total_building_area = st.number_input("Total Gross Floor Area (m²)", value=4800.0)
        
        site_coverage = (building_footprint / plot_area) * 100.0
        far = total_building_area / plot_area
        
        st.write(f"• **Site Coverage:** {site_coverage:.1f}% (Max Allowed: 60%)")
        st.write(f"• **Floor Area Ratio (FAR):** {far:.2f} (Max Allowed: 3.5)")
        
        if site_coverage <= 60 and far <= 3.5:
            st.success("✅ Design complies with standard urban planning zoning limits!")
        else:
            st.warning("⚠️ Warning: Design exceeds default FAR or site coverage limits.")

# -----------------------------------------------------------------------------
# MODULE 4: BOQ & FOREX ENGINE
# -----------------------------------------------------------------------------
elif navigation == "📊 BoQ & Forex Engine":
    st.title("📊 Bill of Quantities (BoQ) & Currency Conversion")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Core Material Quantities")
        concrete_m3 = st.number_input("Concrete Volume (m³)", value=1200.0)
        rebar_tons = st.number_input("Reinforcement Steel (Tons)", value=110.0)
        mep_lump_sum_usd = st.number_input("MEP Installation Package ($)", value=180000.0)
        
        # Base Costs in USD
        cost_concrete = concrete_m3 * 160.0
        cost_rebar = rebar_tons * 950.0
        total_usd = cost_concrete + cost_rebar + mep_lump_sum_usd
        
    with col2:
        st.subheader("Forex Currency Conversion")
        target_currency = st.selectbox("Target Currency", ["KES (Kenya)", "UGX (Uganda)", "TZS (Tanzania)", "EUR (Euro)"])
        
        fx_rates = {
            "KES (Kenya)": 129.5,
            "UGX (Uganda)": 3680.0,
            "TZS (Tanzania)": 2620.0,
            "EUR (Euro)": 0.92
        }
        
        rate = fx_rates[target_currency]
        converted_total = total_usd * rate
        
        st.metric("Total Project Estimate (USD)", f"${total_usd:,.2f}")
        st.metric(f"Converted Estimate ({target_currency.split()[0]})", f"{converted_total:,.2f}")

    # Cost Distribution Chart
    st.divider()
    st.subheader("Cost Breakdown")
    df_cost = pd.DataFrame({
        "Category": ["Concrete", "Reinforcement Steel", "MEP Package"],
        "Cost_USD": [cost_concrete, cost_rebar, mep_lump_sum_usd]
    })
    fig_pie = px.pie(df_cost, names="Category", values="Cost_USD", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_pie, use_container_width=True)
