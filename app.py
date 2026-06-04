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
    /* Default (Laptop) */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Mobile Devices (Screens smaller than 600px) */
    @media (max-width: 600px) {
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        h1 { font-size: 1.5rem !important; }
        h4 { font-size: 1.1rem !important; }
        div[data-testid="stMetric"] { font-size: 0.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATES ---
if "shop_opened" not in st.session_state:
    st.session_state["shop_opened"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Stock Screener"

def color_pnl_column(val):
    if val > 0: return 'color: #1a9641; font-weight: bold;'
    elif val < 0: return 'color: #d7191c; font-weight: bold;'
    return ''

# --- HELPER FUNCTIONS ---
def get_live_pcr(symbol):
    clean_symbol = symbol.replace(".NS", "").replace("^NSEI", "NIFTY")
    if clean_symbol == "NIFTY":
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    else:
        clean_symbol = clean_symbol.replace("&", "%26")
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={clean_symbol}"
    try:
        session = cffi_requests.Session(impersonate="chrome120")
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'filtered' in data and 'CE' in data['filtered'] and 'PE' in data['filtered']:
                tot_ce_oi = data['filtered']['CE']['totOI']
                tot_pe_oi = data['filtered']['PE']['totOI']
                if tot_ce_oi > 0: return round(tot_pe_oi / tot_ce_oi, 2)
    except Exception: pass
    return "N/A"

# --- REMAINDER OF YOUR LOGIC ---
# (Keep the rest of your existing code from line 46 to the end here)
# ... [Insert your existing logic for the rest of the app] ...
