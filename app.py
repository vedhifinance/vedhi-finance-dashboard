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

# --- CUSTOM CSS FOR MOBILE RESPONSIVENESS ---
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

if "shop_opened" not in st.session_state: st.session_state["shop_opened"] = False
if "current_page" not in st.session_state: st.session_state["current_page"] = "Stock Screener"

def color_pnl_column(val):
    if val > 0: return 'color: #1a9641; font-weight: bold;'
    elif val < 0: return 'color: #d7191c; font-weight: bold;'
    return ''

def get_live_pcr(symbol):
    clean_symbol = symbol.replace(".NS", "").replace("^NSEI", "NIFTY")
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY" if clean_symbol == "NIFTY" else f"https://www.nseindia.com/api/option-chain-equities?symbol={clean_symbol.replace('&', '%26')}"
    try:
        session = cffi_requests.Session(impersonate="chrome120")
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'filtered' in data and 'CE' in data['filtered'] and 'PE' in data['filtered']:
                return round(data['filtered']['PE']['totOI'] / data['filtered']['CE']['totOI'], 2)
    except Exception: pass
    return "N/A"

if not st.session_state["shop_opened"]:
    st.markdown("<h1 style='text-align: center; color: #1a9641;'>🏪 Vedhi Finance-Nifty50 Shop</h1>", unsafe_allow_html=True)
    if os.path.exists("shop_image.png.png"): st.image("shop_image.png.png", use_container_width=True)
    if st.button("🚪 Open the Shop", use_container_width=True):
        st.session_state["shop_opened"] = True
        st.rerun()
else:
    colA, colB = st.columns([9, 1])
    with colA: st.markdown("<h4 style='color: #1a9641;'>Vedhi Finance | 📈 Nifty 50 Strategy</h4>", unsafe_allow_html=True)
    with colB:
        if st.button("🔒 Exit"):
            st.session_state["shop_opened"] = False
            st.rerun()

    nav1, nav2, nav3, nav4 = st.columns(4)
    if nav1.button("🔍 Screener", use_container_width=True): st.session_state["current_page"] = "Stock Screener"
    if nav2.button("💼 Portfolio", use_container_width=True): st.session_state["current_page"] = "Portfolio Tracker"
    if nav3.button("🗺️ Heat Map", use_container_width=True): st.session_state["current_page"] = "Sector Heat Map"
    if nav4.button("📈 Charts", use_container_width=True): st.session_state["current_page"] = "Charts"
    
    menu = st.session_state["current_page"]
    NIFTY50_TICKERS = ["ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BEL.NS", "BHARTIARTL.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "ETERNAL.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDIGO.NS", "INFY.NS", "ITC.NS", "JIOFIN.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "MAXHEALTH.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHRIRAMFIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "TMPV.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"]
    if menu == "Stock Screener":
        # (Insert your original Stock Screener logic here)
    elif menu == "Portfolio Tracker":
        # (Insert your original Portfolio Tracker logic here)
    elif menu == "Sector Heat Map":
        # (Insert your original Sector Heat Map logic here)
    elif menu == "Charts":
        # (Insert your original Charts logic here)
