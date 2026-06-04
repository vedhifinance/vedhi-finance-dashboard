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

# --- CUSTOM CSS TO PUSH UI TO TOP ---
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATES ---
if "shop_opened" not in st.session_state:
    st.session_state["shop_opened"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Stock Screener"

def color_pnl_column(val):
    if val > 0:
        return 'color: #1a9641; font-weight: bold;'
    elif val < 0:
        return 'color: #d7191c; font-weight: bold;'
    return ''

# --- HELPER FUNCTIONS ---
def get_live_pcr(symbol):
    """
    Scrapes the NSE website for real-time Options Chain data using curl_cffi 
    to bypass strict TLS fingerprinting firewalls.
    """
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
                if tot_ce_oi > 0:
                    return round(tot_pe_oi / tot_ce_oi, 2)
    except Exception:
        pass
    
    return "N/A"

# --- 1. WELCOME / LANDING PAGE VIEW ---
if not st.session_state["shop_opened"]:
    st.markdown("<h1 style='text-align: center; font-family: Georgia; color: #1a9641; margin-top: 20px;'>🏪 Vedhi Finance-Nifty50 Shop</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 1.2em;'>Quality Nifty 50 stocks at a discount. Buy low, sell high, keep the spread</p>", unsafe_allow_html=True)
    
    image_path = "shop_image.png.png"
    
    col_left, col_mid, col_right = st.columns([1, 8, 1])
    with col_mid:
        if os.path.exists(image_path):
            st.image(image_path, width="stretch")
        else:
            st.markdown(
                """
                <div style='border: 2px dashed #1a9641; padding: 50px; text-align: center; border-radius: 10px; background-color: #1e1e1e;'>
                    <span style='font-size: 3em;'>🏪</span><br>
                    <p style='color: #ffffff; margin-top: 10px;'><b>[ Place your 'shop_image' in the project folder ]</b></p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Open the Shop", width="stretch"):
            st.session_state["shop_opened"] = True
            st.rerun()

# --- 2. MAIN DASHBOARD VIEW ---
else:
    # Header and Exit Button minimized to save vertical space
    colA, colB = st.columns([9, 1])
    with colA:
        st.markdown("<h4 style='color: #1a9641; margin-top: -10px; margin-bottom: 0px;'>Vedhi Finance | 📈 Nifty 50 Strategy</h4>", unsafe_allow_html=True)
    with colB:
        if st.button("🔒 Exit"):
            st.session_state["shop_opened"] = False
            st.rerun()

    st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)

    # --- TOP BUTTON NAVIGATION BAR ---
    nav1, nav2, nav3, nav4 = st.columns(4)
    with nav1:
        if st.button("🔍 Stock Screener", width="stretch"): st.session_state["current_page"] = "Stock Screener"
    with nav2:
        if st.button("💼 Portfolio Tracker", width="stretch"): st.session_state["current_page"] = "Portfolio Tracker"
    with nav3:
        if st.button("🗺️ Sector Heat Map", width="stretch"): st.session_state["current_page"] = "Sector Heat Map"
    with nav4:
        if st.button("📈 Charts", width="stretch"): st.session_state["current_page"] = "Charts"
        
    menu = st.session_state["current_page"]

    NIFTY50_TICKERS = [
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BEL.NS", "BHARTIARTL.NS",
        "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "ETERNAL.NS",
        "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HINDALCO.NS",
        "HINDUNILVR.NS", "ICICIBANK.NS", "INDIGO.NS", "INFY.NS", "ITC.NS",
        "JIOFIN.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS",
        "MARUTI.NS", "MAXHEALTH.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
        "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHRIRAMFIN.NS",
        "SUNPHARMA.NS", "TATACONSUM.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS",
        "TITAN.NS", "TMPV.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]

    # --- SCREENER LOGIC ---
    if menu == "Stock Screener":
        scr_tab1, scr_tab2, scr_tab3 = st.tabs(["📈 Nifty 50 Stocks", "📊 Gold & Silver", "📊 ETFs Screener"])
        
        with scr_tab1:
            if st.button("Run Nifty Screener", key="run_nifty"):
                buy_signals = []
                with st.spinner("Scanning Nifty 50 stocks..."):
                    for ticker in NIFTY50_TICKERS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            if len(df) < 50: continue
                            
                            df['EMA_20'] = ta.ema(df['Close'], length=20)
                            df['EMA_50'] = ta.ema(df['Close'], length=50)
                            df['RSI_14'] = ta.rsi(df['Close'], length=14)
                            df['Avg_Vol_20'] = df['Volume'].rolling(window=20).mean()
                            
                            prev_row, latest_row = df.iloc[-2], df.iloc[-1]
                            prev_open, prev_close = float(prev_row['Open']), float(prev_row['Close'])
                            current_close, current_vol = float(latest_row['Close']), float(latest_row['Volume'])
                            
                            avg_vol = float(latest_row['Avg_Vol_20'])
                            ema_20 = float(latest_row['EMA_20'])
                            ema_50 = float(latest_row['EMA_50'])
                            rsi_14 = float(latest_row['RSI_14'])
                            
                            if current_close < ema_20 and current_close > ema_50 and rsi_14 < 40 and (prev_close > prev_open) and (current_vol > avg_vol):
                                buy_signals.append({
                                    "Ticker": ticker.replace(".NS", ""), "Price": round(current_close, 2),
                                    "20 EMA": round(ema_20, 2), "50 EMA": round(ema_50, 2), "RSI": round(rsi_14, 2),
                                    "Volume": f"{int(current_vol):,}", "Avg Vol (20d)": f"{int(avg_vol):,}"
                                })
                        except: continue
                if buy_signals:
                    st.success(f"Found {len(buy_signals)} stocks matching the setup!")
                    st.dataframe(pd.DataFrame(buy_signals), hide_index=True, width="stretch")
                else: st.warning("No stocks currently meet the criteria.")
            
            st.markdown("---")
            st.markdown("### 📋 Screener Rules Summary")
            crit_col1, crit_col2, crit_col3, crit_col4 = st.columns(4)
            crit_col1.markdown("**1. Pullback Check:**\nPrice pulled below **20 EMA** but safely above **50 EMA**.")
            crit_col2.markdown("**2. RSI Level:**\n**RSI (14)** calculation value must be strictly below **40**.")
            crit_col3.markdown("**3. Price Action:**\nPrevious day's candle must be bullish (**Close > Open**).")
            crit_col4.markdown("**4. Volume Surge:**\nCurrent volume must exceed its **20-day average**.")
        
        with scr_tab2:
            METAL_TICKERS = ["GOLDBEES.NS", "SILVERBEES.NS"]
            if st.button("Scan Gold & Silver", key="run_metals"):
                metal_signals = []
                with st.spinner("Analyzing structures..."):
                    for ticker in METAL_TICKERS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            df['EMA_50'] = ta.ema(df['Close'], length=50)
                            close_p, ema50 = float(df.iloc[-1]['Close']), float(df.iloc[-1]['EMA_50'])
                            status = "🟢 Above 50 EMA" if close_p > ema50 else "🔴 Below 50 EMA"
                            metal_signals.append({
                                "Asset": "Gold" if "GOLD" in ticker else "Silver", "Ticker": ticker.replace(".NS", ""),
                                "Live Price": round(close_p, 2), "50 EMA": round(ema50, 2), "Status": status
                            })
                        except: continue
                if metal_signals: st.dataframe(pd.DataFrame(metal_signals), hide_index=True, width="stretch")
            
            st.markdown("---")
            st.markdown("### 📋 Metals Rule Summary")
            st.markdown("🔍 Tracks structural momentum: **🟢 Status** highlights long-term buyers defending the **50 EMA line**.")

        with scr_tab3:
            TARGET_ETFS = ["PSUBNKBEES.NS", "BANKBEES.NS", "JUNIORBEES.NS"] 
            if st.button("Run ETF Screener", key="run_etfs"):
                etf_signals = []
                with st.spinner("Scanning ETFs..."):
                    for ticker in TARGET_ETFS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            df['EMA_20'], df['RSI_14'] = ta.ema(df['Close'], length=20), ta.rsi(df['Close'], length=14)
                            close, ema20, rsi = float(df.iloc[-1]['Close']), float(df.iloc[-1]['EMA_20']), float(df.iloc[-1]['RSI_14'])
                            action = "Watching"
                            if close < ema20 and rsi <= 40: action = "🔥 DOUBLE SIGNAL"
                            elif close < ema20: action = "📉 Pullback Zone"
                            elif rsi <= 40: action = "🔄 RSI Reversal"
                            etf_signals.append({
                                "ETF Name": ticker.replace(".NS", ""), "Live Price": round(close, 2),
                                "20 EMA": round(ema20, 2), "RSI (14)": round(rsi, 2), "Status": action
                            })
                        except: continue
                if etf_signals: st.dataframe(pd.DataFrame(etf_signals), hide_index=True, width="stretch")
            
            st.markdown("---")
            st.markdown("### 📋 ETF Rules Summary")
            etf_col1, etf_col2, etf_col3 = st.columns(3)
            etf_col1.markdown("**📉 Pullback Zone:**\nPrice crosses below the structural **20 EMA line**.")
            etf_col2.markdown("**🔄 RSI Reversal:**\nOversold metric detected where **RSI (14) <= 40**.")
            etf_col3.markdown("**🔥 DOUBLE SIGNAL:**\nHigh probability setup matching **both** criteria above.")

    # --- PORTFOLIO TRACKER LOGIC ---
    elif menu == "Portfolio Tracker":
        HOLDINGS_FILE = "portfolio_holdings.csv"
        HISTORY_FILE = "portfolio_history.csv"
        
        if os.path.exists(HOLDINGS_FILE): holdings_df = pd.read_csv(HOLDINGS_FILE)
        else: holdings_df = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity", "Buy Date"])
            
        if os.path.exists(HISTORY_FILE): history_df = pd.read_csv(HISTORY_FILE)
        else: history_df = pd.DataFrame(columns=["Ticker", "Buy Price", "Sell Price", "Quantity", "Brokerage", "Profit/Loss", "Holding Days", "Date Sold"])

        tab_buy, tab_sell = st.tabs(["➕ Buy a Stock", "➖ Sell a Stock"])
        
        with tab_buy:
            with st.form("buy_form", clear_on_submit=True):
                clean_tickers = [t.replace(".NS", "") for t in NIFTY50_TICKERS]
                ticker_input = st.selectbox("Select Stock", clean_tickers)
                buy_price = st.number_input("Buy Price (₹)", min_value=0.0, step=0.1)
                quantity = st.number_input("Quantity", min_value=1, step=1)
                buy_date = st.date_input("Purchase Date")
                
                if st.form_submit_button("Add to Holdings") and buy_price > 0:
                    new_row = pd.DataFrame([{"Ticker": ticker_input, "Buy Price": buy_price, "Quantity": quantity, "Buy Date": str(buy_date)}])
                    holdings_df = pd.concat([holdings_df, new_row], ignore_index=True)
                    holdings_df.to_csv(HOLDINGS_FILE, index=False)
                    st.success(f"Successfully added {quantity} shares of {ticker_input}!")
                    st.rerun()

        with tab_sell:
            if not holdings_df.empty:
                with st.form("sell_form", clear_on_submit=True):
                    unique_holdings = holdings_df["Ticker"].unique()
                    ticker_to_sell = st.selectbox("Select Stock to Sell", unique_holdings)
                    
                    stock_data = holdings_df[holdings_df["Ticker"] == ticker_to_sell].iloc[0]
                    st.info(f"You own {stock_data['Quantity']} shares bought on {stock_data['Buy Date']} at ₹{stock_data['Buy Price']:.2f}")
                    
                    sell_price = st.number_input("Sell Price (₹)", min_value=0.0, step=0.1)
                    sell_date = st.date_input("Sale Date")
                    brokerage = st.number_input("Total Brokerage & Taxes Paid (₹)", min_value=0.0, step=1.0, value=20.0)
                    
                    if st.form_submit_button("Log Sale & Realize P&L") and sell_price > 0:
                        b_price, qty = float(stock_data['Buy Price']), int(stock_data['Quantity'])
                        net_pnl = ((sell_price - b_price) * qty) - brokerage
                        
                        try:
                            held_days = (pd.to_datetime(sell_date).date() - pd.to_datetime(stock_data['Buy Date']).date()).days
                            held_days_str = f"{held_days} Days" if held_days > 0 else "Same Day"
                        except: held_days_str = "Unknown"
                        
                        new_history_row = pd.DataFrame([{"Ticker": ticker_to_sell, "Buy Price": b_price, "Sell Price": sell_price, "Quantity": qty, "Brokerage": round(brokerage, 2), "Profit/Loss": round(net_pnl, 2), "Holding Days": held_days_str, "Date Sold": str(sell_date)}])
                        history_df = pd.concat([history_df, new_history_row], ignore_index=True)
                        history_df.to_csv(HISTORY_FILE, index=False)
                        
                        holdings_df = holdings_df[holdings_df["Ticker"] != ticker_to_sell]
                        holdings_df.to_csv(HOLDINGS_FILE, index=False)
                        
                        if net_pnl >= 0: st.success(f"Booked Net Profit of ₹{net_pnl:,.2f}!")
                        else: st.error(f"Booked Net Loss of ₹{abs(net_pnl):,.2f}!")
                        st.rerun()
            else:
                st.write("You don't have any current holdings to sell.")

        st.write("---")
        display_holdings, display_history = st.tabs(["📂 Current Open Holdings", "📜 Closed Trade History"])
        
        with display_holdings:
            if not holdings_df.empty:
                with st.spinner("Fetching live prices and calculating 50 EMA stop loss..."):
                    live_holdings = []
                    total_invested, total_current_val = 0, 0
                    today = pd.to_datetime("today").date()
                    
                    for index, row in holdings_df.iterrows():
                        ticker = row["Ticker"]
                        ns_ticker = ticker + ".NS" if not ticker.endswith(".NS") else ticker
                        try:
                            stock_data = yf.Ticker(ns_ticker).history(period="6mo")
                            current_price = float(stock_data['Close'].iloc[-1])
                            ema_50 = float(ta.ema(stock_data['Close'], length=50).iloc[-1])
                            
                            if current_price < ema_50:
                                status = "🛑 Sell (Below 50 EMA)"
                            else:
                                status = "✅ Hold"
                        except: 
                            current_price = row["Buy Price"]
                            ema_50 = 0.0
                            status = "⚠️ Data Error"
                            
                        try:
                            holding_days = (today - pd.to_datetime(row["Buy Date"]).date()).days
                            holding_days_str = f"{holding_days} Days" if holding_days > 0 else "Today"
                        except: holding_days_str = "N/A"
                            
                        invested = row["Quantity"] * row["Buy Price"]
                        current_val = row["Quantity"] * current_price
                        pnl = current_val - invested
                        
                        total_invested += invested
                        total_current_val += current_val
                        
                        live_holdings.append({
                            "Ticker": ticker, "Buy Date": row["Buy Date"], "Holding Period": holding_days_str,
                            "Quantity": row["Quantity"], "Avg Buy Price": round(row["Buy Price"], 2),
                            "Live Price": round(current_price, 2), "50 EMA Stop Loss": round(ema_50, 2), "Status": status,
                            "Invested (₹)": round(invested, 2), "Current Value (₹)": round(current_val, 2), 
                            "Unrealized P&L (₹)": round(pnl, 2), "P&L (%)": f"{round((pnl/invested)*100, 2) if invested else 0}%"
                        })
                        
                styled_holdings_df = pd.DataFrame(live_holdings).style.map(color_pnl_column, subset=["Unrealized P&L (₹)"]).format(precision=2)
                st.dataframe(styled_holdings_df, hide_index=True, width="stretch")
                
                total_pnl = total_current_val - total_invested
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Invested", f"₹{total_invested:,.2f}")
                col2.metric("Current Value", f"₹{total_current_val:,.2f}")
                col3.metric("Total Unrealized P&L", f"₹{total_pnl:,.2f}", delta=f"{(total_pnl/total_invested)*100:.2f}%" if total_invested else "0%")
            else:
                st.info("Your portfolio is currently empty.")
                
        with display_history:
            if not history_df.empty:
                edited_history = st.data_editor(history_df, num_rows="dynamic", hide_index=True, width="stretch", key="history_editor")
                if st.button("Save History Changes"):
                    edited_history.to_csv(HISTORY_FILE, index=False)
                    st.success("Trade history updated successfully!")
                    st.rerun()
                
                total_pnl = edited_history["Profit/Loss"].sum()
                if total_pnl >= 0: st.metric("Total Realized Net Profit", f"₹{total_pnl:,.2f}")
                else: st.metric("Total Realized Net Loss", f"₹{total_pnl:,.2f}")
            else:
                st.info("No closed trades in your history yet.")

    # --- SECTOR HEAT MAP LOGIC ---
    elif menu == "Sector Heat Map":
        NIFTY_SECTORS = {
            "Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "HDFCLIFE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "JIOFIN.NS"],
            "IT": ["INFY.NS", "TCS.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
            "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS"],
            "Automobiles": ["M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "TMPV.NS"],
            "Consumer": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "TATACONSUM.NS", "ASIANPAINT.NS", "TITAN.NS", "TRENT.NS"],
            "Healthcare": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "MAXHEALTH.NS"],
            "Materials": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "GRASIM.NS", "ULTRACEMCO.NS"],
            "Industrials": ["LT.NS", "ADANIPORTS.NS", "ADANIENT.NS", "BEL.NS"],
            "Telecom": ["BHARTIARTL.NS"],
            "Aviation": ["INDIGO.NS"]
        }
        
        if st.button("Refresh Heat Map"):
            heat_data = []
            with st.spinner("Building the Heat Map..."):
                for sector, tickers in NIFTY_SECTORS.items():
                    for ticker in tickers:
                        try:
                            df = yf.Ticker(ticker).history(period="5d")
                            if len(df) >= 2:
                                prev_close, current_close = float(df['Close'].iloc[-2]), float(df['Close'].iloc[-1])
                                heat_data.append({"Sector": sector, "Stock": ticker.replace(".NS", ""), "Price": round(current_close, 2), "Change (%)": round(((current_close - prev_close) / prev_close) * 100, 2)})
                        except: continue
                            
            if heat_data:
                df_heat = pd.DataFrame(heat_data)
                df_heat["Size"] = 1 
                fig = px.treemap(
                    df_heat, 
                    path=["Sector", "Stock"], 
                    values="Size", 
                    color="Change (%)", 
                    color_continuous_scale=[[0.0, "#d7191c"], [0.5, "#262626"], [1.0, "#1a9641"]], 
                    color_continuous_midpoint=0, 
                    custom_data=["Price", "Change (%)"]
                )
                fig.update_traces(
                    texttemplate="<b>%{label}</b><br>%{customdata[1]}%", 
                    hovertemplate="<b>%{label}</b><br>Price: ₹%{customdata[0]:,}<br>Change: %{customdata[1]}%"
                )
                fig.update_layout(
                    margin=dict(t=10, l=10, r=10, b=10), 
                    height=650, 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, width="stretch")

    # --- TECHNICAL CHARTS LOGIC ---
    elif menu == "Charts":
        st.info("💡 **The 20 EMA and 50 EMA lines are drawn on the graph below!**")
        selected_asset = st.selectbox("Select Asset to Analyze", ["NIFTY 50 INDEX"] + [t.replace(".NS", "") for t in NIFTY50_TICKERS])
        actual_ticker = "^NSEI" if selected_asset == "NIFTY 50 INDEX" else f"{selected_asset}.NS"
            
        with st.spinner(f"Loading chart and live PCR data for {selected_asset}..."):
            df = yf.Ticker(actual_ticker).history(period="6mo")
            live_pcr = get_live_pcr(selected_asset)
            
            if not df.empty:
                df['EMA_20'] = ta.ema(df['Close'], length=20)
                df['EMA_50'] = ta.ema(df['Close'], length=50)
                
                delta = df['Close'].diff()
                gain, loss = delta.where(delta > 0, 0).fillna(0), -delta.where(delta < 0, 0).fillna(0)
                avg_gain, avg_loss = gain.ewm(alpha=1/14, adjust=False).mean(), loss.ewm(alpha=1/14, adjust=False).mean()
                df['RSI'] = 100 - (100 / (1 + avg_gain / avg_loss))
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Current Price", f"₹{df['Close'].iloc[-1]:,.2f}")
                c2.metric("20 EMA (Yellow)", f"₹{df['EMA_20'].iloc[-1]:,.2f}" if not pd.isna(df['EMA_20'].iloc[-1]) else "N/A")
                c3.metric("50 EMA (Orange)", f"₹{df['EMA_50'].iloc[-1]:,.2f}" if not pd.isna(df['EMA_50'].iloc[-1]) else "N/A")
                c4.metric("Current RSI", f"{df['RSI'].iloc[-1]:.2f}")
                c5.metric("Live PCR", live_pcr)
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.4])
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='yellow', width=1.5), name="20 EMA"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='orange', width=1.5), name="50 EMA"), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00b4d8', width=2), name="RSI"), row=2, col=1)
                fig.update_layout(height=750, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), xaxis_rangeslider_visible=False, showlegend=False)
                
            st.plotly_chart(fig, width="stretch")
