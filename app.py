import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import os
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from curl_cffi import requests as cffi_requests
import time

st.set_page_config(page_title="Nifty 50 Strategy Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    @media (max-width: 600px) {
        .block-container { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        h1 { font-size: 1.5rem !important; }
        h4 { font-size: 1.1rem !important; }
        div[data-testid="stMetric"] { font-size: 0.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATES ---
if "shop_opened" not in st.session_state: st.session_state["shop_opened"] = False
if "current_page" not in st.session_state: st.session_state["current_page"] = "Stock Screener"

# --- MAIN APP LOGIC ---
if not st.session_state["shop_opened"]:
    st.markdown("<h1 style='text-align: center; color: #1a9641;'>🏪 Vedhi Finance-Nifty50 Shop</h1>", unsafe_allow_html=True)
    if os.path.exists("shop_image.png.png"): st.image("shop_image.png.png", use_container_width=True)
    if st.button("🚪 Open the Shop", use_container_width=True):
        st.session_state["shop_opened"] = True
        st.rerun()
else:
    # --- NAVIGATION BAR ---
    colA, colB = st.columns([9, 1])
    with colA: st.markdown("<h4 style='color: #1a9641;'>Vedhi Finance | 📈 Nifty 50 Strategy</h4>", unsafe_allow_html=True)
    with colB:
        if st.button("🔒 Exit"):
            st.session_state["shop_opened"] = False
            st.rerun()

    nav1, nav2, nav3, nav4 = st.columns(4)
    if nav1.button("🔍 Screener"): st.session_state["current_page"] = "Stock Screener"
    if nav2.button("💼 Portfolio"): st.session_state["current_page"] = "Portfolio Tracker"
    if nav3.button("🗺️ Heat Map"): st.session_state["current_page"] = "Sector Heat Map"
    if nav4.button("📈 Charts"): st.session_state["current_page"] = "Charts"
    
    menu = st.session_state["current_page"]

    # --- CONTENT PAGES (Correctly indented under the 'else' block) ---
    if menu == "Stock Screener":
        st.write("### 🔍 Stock Screener")
        # PASTE YOUR SCREENER LOGIC HERE
        
    elif menu == "Portfolio Tracker":
        st.write("### 💼 Portfolio Tracker")
        # PASTE YOUR PORTFOLIO LOGIC HERE
        
    elif menu == "Sector Heat Map":
        st.write("### 🗺️ Sector Heat Map")
        # PASTE YOUR HEAT MAP LOGIC HERE
        
    elif menu == "Charts":
        st.write("### 📈 Charts")
        # PASTE YOUR CHARTS LOGIC HERE
