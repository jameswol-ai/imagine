# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="IMAGINE Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Dark Blue & Gold CSS
# ---------------------------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: #0e1a2b;
        color: #e0e0e0;
    }
    /* Sidebar */
    .css-1d391kg {
        background: #0b1422;
    }
    .sidebar .sidebar-content {
        background: #0b1422;
    }
    /* Metric cards */
    .metric-card {
        background: #1a2a3f;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        text-align: center;
        border-left: 5px solid #f5b041;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f5b041;
    }
    .metric-change {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    .stButton button {
        background: linear-gradient(135deg, #1a3a5c, #2a5a7c);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(245,176,65,0.3);
        background: #2a5a7c;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1a2a3f;
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        color: #a0b0c0;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #f5b041;
        color: #0e1a2b;
    }
    h1, h2, h3 {
        color: #f5b041;
        font-weight: 600;
    }
    .stDataFrame, .stTable {
        background: #1a2a3f;
        border-radius: 10px;
        padding: 10px;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        background: #1a2a3f;
        border-radius: 8px;
    }
    .stSidebar .stMarkdown {
        color: #d0d0d0;
    }
    .stSidebar .stTitle {
        color: #f5b041;
    }
    .stSidebar .stRadio label {
        color: #d0d0d0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Authentication (mock)
# ---------------------------
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        with st.sidebar:
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In"):
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.role = "Project Manager"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.stop()

check_authentication()

# ---------------------------
# Session state init (same as before)
# ---------------------------
# ... (keep the init_session_state() function and all page functions unchanged)
# The rest of the app is identical to the previous version,
# just with the new CSS styling.

# For brevity, I'll assume you copy the rest from the earlier full version.
# I'll provide the full file at the end.