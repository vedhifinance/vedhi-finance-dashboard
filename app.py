import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import os
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Nifty 50 Strategy Dashboard", layout="wide")

# --- SESSION STATE FOR LANDING PAGE ---
if "shop_opened" not in st.session_state:
    st.session_state["shop_opened"] = False

# Helper function to color-code profit (Green) and loss (Red)
def color_pnl_column(val):
    if val > 0:
        return 'color: #1a9641; font-weight: bold;'
    elif val < 0:
        return 'color: #d7191c; font-weight: bold;'
    return ''

# --- 1. WELCOME / LANDING PAGE VIEW ---
if not st.session_state["shop_opened"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 1.2em;'>Quality Nifty 50 stocks at a discount. Buy low, sell high, keep the spread</p>", unsafe_allow_html=True)
    
    # Cloud-ready relative path
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
                    <p style='color: gray; font-size: 0.9em;'>Image showing a staircase layout will display right here.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚪 Open the Shop", width="stretch"):
            st.session_state["shop_opened"] = True
            st.rerun()
            
    st.markdown("<p style='text-align: center; color: #555; font-size: 0.8em; margin-top: 30px;'>Click the steps above to unlock the trading terminal.</p>", unsafe_allow_html=True)

# --- 2. MAIN DASHBOARD VIEW (OPENS AFTER CLICKING) ---
else:
    # --- COMPACT HEADER ---
    st.markdown(
        """
        <h3 style='font-family: "Georgia", serif; color: #1a9641; margin-top: -40px;'>
            Vedhi Finance <span style='font-size: 0.8em; color: #cccccc;'>| 📈 Nifty 50 Strategy</span>
        </h3>
        <hr style='margin-top: 5px; margin-bottom: 15px;'>
        """, 
        unsafe_allow_html=True
    )

    if st.sidebar.button("🔒 Close Terminal / Exit"):
        st.session_state["shop_opened"] = False
        st.rerun()

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

    menu = st.sidebar.radio("Go to:", ["Stock Screener", "Portfolio Tracker", "Sector Heat Map", "Charts", "Live TV"])

    # --- SCREENER LOGIC ---
    if menu == "Stock Screener":
        st.subheader("🔍 Strategy Screener")
        
        scr_tab1, scr_tab2, scr_tab3 = st.tabs(["📈 Nifty 50 Stocks", "🪙 Gold & Silver", "📊 ETFs Screener"])
        
        # TAB 1: NIFTY 50
        with scr_tab1:
            st.subheader("Nifty 50 Momentum Strategy")
            if st.button("Run Nifty Screener", key="run_nifty"):
                buy_signals = []
                with st.spinner("Scanning Nifty 50 stocks... This may take a minute."):
                    for ticker in NIFTY50_TICKERS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            if len(df) < 20: continue
                            
                            df['EMA_20'] = ta.ema(df['Close'], length=20)
                            df['EMA_50'] = ta.ema(df['Close'], length=50)
                            df['RSI_14'] = ta.rsi(df['Close'], length=14)
                            df['Avg_Vol_20'] = df['Volume'].rolling(window=20).mean()
                            
                            prev_row = df.iloc[-2]  
                            latest_row = df.iloc[-1] 
                            
                            prev_open, prev_close = float(prev_row['Open']), float(prev_row['Close'])
                            current_close, current_vol = float(latest_row['Close']), float(latest_row['Volume'])
                            avg_vol = float(latest_row['Avg_Vol_20'])
                            ema_20, rsi_14 = float(latest_row['EMA_20']), float(latest_row['RSI_14'])
                            
                            if current_close < ema_20 and rsi_14 < 40 and (prev_close > prev_open) and (current_vol > avg_vol):
                                buy_signals.append({
                                    "Ticker": ticker.replace(".NS", ""),
                                    "Price": round(current_close, 2),
                                    "20 EMA": round(ema_20, 2),
                                    "RSI": round(rsi_14, 2),
                                    "Volume": f"{int(current_vol):,}",
                                    "Avg Vol (20d)": f"{int(avg_vol):,}"
                                })
                        except:
                            continue
                            
                if buy_signals:
                    st.success(f"Found {len(buy_signals)} stocks matching criteria!")
                    st.dataframe(pd.DataFrame(buy_signals), width="stretch")
                else:
                    st.warning("No stocks currently meet the criteria.")
        
        # TAB 2: GOLD & SILVER
        with scr_tab2:
            st.subheader("🪙 Precious Metals Setup")
            METAL_TICKERS = ["GOLDBEES.NS", "SILVERBEES.NS"]
            if st.button("Scan Gold & Silver", key="run_metals"):
                metal_signals = []
                with st.spinner("Analyzing structures..."):
                    for ticker in METAL_TICKERS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            df['EMA_50'] = ta.ema(df['Close'], length=50)
                            latest = df.iloc[-1]
                            
                            close_p = float(latest['Close'])
                            ema50 = float(latest['EMA_50'])
                            
                            if close_p > ema50: status = "🟢 Above 50 EMA"
                            else: status = "🔴 Below 50 EMA"
                                
                            metal_signals.append({
                                "Asset": "Gold" if "GOLD" in ticker else "Silver",
                                "Ticker": ticker.replace(".NS", ""),
                                "Live Price": round(close_p, 2),
                                "50 EMA": round(ema50, 2),
                                "Status": status
                            })
                        except: continue
                if metal_signals:
                    st.dataframe(pd.DataFrame(metal_signals), width="stretch")

        # TAB 3: ETFS
        with scr_tab3:
            st.subheader("📊 Elite ETF Scanner")
            TARGET_ETFS = ["PSUBNKBEES.NS", "BANKBEES.NS", "JUNIORBEES.NS"] 
            if st.button("Run ETF Screener", key="run_etfs"):
                etf_signals = []
                with st.spinner("Scanning ETFs..."):
                    for ticker in TARGET_ETFS:
                        try:
                            df = yf.Ticker(ticker).history(period="6mo")
                            df['EMA_20'] = ta.ema(df['Close'], length=20)
                            df['RSI_14'] = ta.rsi(df['Close'], length=14)
                            
                            latest = df.iloc[-1]
                            close, ema20, rsi = float(latest['Close']), float(latest['EMA_20']), float(latest['RSI_14'])
                            
                            action = "Watching"
                            if close < ema20 and rsi <= 40: action = "🔥 DOUBLE SIGNAL"
                            elif close < ema20: action = "📉 Pullback Zone"
                            elif rsi <= 40: action = "🔄 RSI Reversal"
                                    
                            etf_signals.append({
                                "ETF Name": ticker.replace(".NS", ""),
                                "Live Price": round(close, 2),
                                "20 EMA": round(ema20, 2),
                                "RSI (14)": round(rsi, 2),
                                "Status": action
                            })
                        except: continue
                if etf_signals:
                    st.dataframe(pd.DataFrame(etf_signals), width="stretch")

    # --- PORTFOLIO TRACKER LOGIC ---
    elif menu == "Portfolio Tracker":
        st.subheader("💼 Interactive Portfolio Tracker")
        
        HOLDINGS_FILE = "portfolio_holdings.csv"
        HISTORY_FILE = "portfolio_history.csv"
        
        if os.path.exists(HOLDINGS_FILE): holdings_df = pd.read_csv(HOLDINGS_FILE)
        else: holdings_df = pd.DataFrame(columns=["Ticker", "Buy Price", "Quantity", "Buy Date"])
            
        if os.path.exists(HISTORY_FILE): history_df = pd.read_csv(HISTORY_FILE)
        else: history_df = pd.DataFrame(columns=["Ticker", "Buy Price", "Sell Price", "Quantity", "Brokerage", "Profit/Loss", "Holding Days", "Date Sold"])

        tab_buy, tab_sell = st.tabs(["➕ Buy a Stock", "➖ Sell a Stock"])
        
        with tab_buy:
            st.subheader("Record New Purchase")
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
            st.subheader("Record a Sale")
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
                with st.spinner("Fetching live prices..."):
                    live_holdings = []
                    total_invested, total_current_val = 0, 0
                    today = pd.to_datetime("today").date()
                    
                    for index, row in holdings_df.iterrows():
                        ticker = row["Ticker"]
                        ns_ticker = ticker + ".NS" if not ticker.endswith(".NS") else ticker
                        try:
                            stock_data = yf.Ticker(ns_ticker).history(period="5d")
                            current_price = stock_data['Close'].iloc[-1]
                        except: current_price = row["Buy Price"]
                            
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
                            "Live Price": round(current_price, 2), "Invested (₹)": round(invested, 2),
                            "Current Value (₹)": round(current_val, 2), "Unrealized P&L (₹)": round(pnl, 2),
                            "P&L (%)": f"{round((pnl/invested)*100, 2) if invested else 0}%"
                        })
                        
                styled_holdings_df = pd.DataFrame(live_holdings).style.map(color_pnl_column, subset=["Unrealized P&L (₹)"]).format(precision=2)
                st.dataframe(styled_holdings_df, width="stretch")
                
                total_pnl = total_current_val - total_invested
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Invested", f"₹{total_invested:,.2f}")
                col2.metric("Current Value", f"₹{total_current_val:,.2f}")
                col3.metric("Total Unrealized P&L", f"₹{total_pnl:,.2f}", delta=f"{(total_pnl/total_invested)*100:.2f}%" if total_invested else "0%")
            else:
                st.info("Your portfolio is currently empty.")
                
        with display_history:
            if not history_df.empty:
                edited_history = st.data_editor(history_df, num_rows="dynamic", width="stretch", key="history_editor")
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
        st.subheader("🗺️ Nifty 50 Sector Heat Map")
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
                fig = px.treemap(df_heat, path=["Sector", "Stock"], values="Size", color="Change (%)", color_continuous_scale=[[0.0, "#d7191c"], [0.5, "#262626"], [1.0, "#1a9641"]], color_continuous_midpoint=0, custom_data=["Price", "Change (%)"])
                fig.update_traces(texttemplate="<b>%{label}</b><br>%{customdata[1]}%", hovertemplate="<b>%{label}</b><br>Price: ₹%{customdata[0]:,}<br>Change: %{customdata[1]}%")
                fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=650, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, width="stretch")

    # --- TECHNICAL CHARTS LOGIC ---
    elif menu == "Charts":
        st.header("📈 Technical Analysis Charts")
        clean_tickers = [t.replace(".NS", "") for t in NIFTY50_TICKERS]
        chart_options = ["NIFTY 50 INDEX"] + clean_tickers
        selected_asset = st.selectbox("Select Asset to Analyze", chart_options)
        actual_ticker = "^NSEI" if selected_asset == "NIFTY 50 INDEX" else f"{selected_asset}.NS"
            
        with st.spinner(f"Loading chart data for {selected_asset}..."):
            df = yf.Ticker(actual_ticker).history(period="6mo")
            if not df.empty:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).fillna(0)
                loss = (-delta.where(delta < 0, 0)).fillna(0)
                avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                df['RSI'] = 100 - (100 / (1 + avg_gain / avg_loss))
                df['RSI_SMA'] = df['RSI'].rolling(window=14).mean()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Price", f"₹{df['Close'].iloc[-1]:,.2f}")
                col2.metric("Current RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.4])
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00b4d8', width=2)), row=2, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI_SMA'], line=dict(color='red', width=1.5)), row=2, col=1)
                fig.update_layout(height=750, template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20), xaxis_rangeslider_visible=False, showlegend=False)
            st.plotly_chart(fig, width="stretch")

    # --- LIVE TV LOGIC ---
    elif menu == "Live TV":
        st.header("📺 Live Market News")
        st.markdown("Watch live broadcasts directly inside your dashboard while you analyze your trades.")
        st.info("💡 **Pro Tip:** The dashboard is now hardcoded to automatically load **CNBC Awaaz** Live. You can still paste a different YouTube link below if you want to watch something else!")
        
        default_link = "https://www.youtube.com/@cnbcawaaz/live"
        video_url = st.text_input("YouTube Live Link:", value=default_link)
        
        if video_url:
            with st.spinner("Connecting to live stream..."):
                try:
                    st.video(video_url)
                except Exception as e:
                    st.error("Could not load the video. Make sure it is a valid YouTube link.")
