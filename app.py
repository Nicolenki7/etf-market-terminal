import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. PAGE CONFIGURATION & "" CSS ---
st.set_page_config(
    page_title="ETF Alpha Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Professional CSS: Clean, Card-based, DeFiLlama style
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0f111a; color: #ffffff; }
    
    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 28px !important;
        font-weight: 700;
        color: #ffffff;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #9b9b9b;
    }
    
    /* Containers (Simulating DeFiLlama Cards) */
    .css-1r6slb0, .stDataFrame, .stPlotlyChart {
        background-color: #1b202b;
        border: 1px solid #2d3342;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Headers */
    h1, h2, h3 { color: #fdfdfd; font-family: 'Inter', sans-serif; }
    h4, h5 { color: #8899ac; font-weight: 400; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #13161f;
        border-right: 1px solid #2d3342;
    }
    
    /* Input/Select styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1b202b !important;
        color: white !important;
        border: 1px solid #2d3342;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (API) ---
@st.cache_data(ttl=60)
def load_data():
    url = f"{st.secrets['supabase_url']}/rest/v1/raw_etf_market_data?select=*"
    headers = {
        "apikey": st.secrets["supabase_key"],
        "Authorization": f"Bearer {st.secrets['supabase_key']}"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            
            # Numeric conversion
            cols = ['price', 'day_high', 'day_low', 'day_open', 'prev_close', 'change_pct']
            for c in cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            # Date conversion
            if 'ingested_at' in df.columns:
                df['ingested_at'] = pd.to_datetime(df['ingested_at'])
            
            # Feature Engineering
            df['volatility_spread'] = ((df['day_high'] - df['day_low']) / df['day_low']) * 100
            
            return df
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

df = load_data()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.title("⚡ ETF Terminal")
st.sidebar.markdown("---")

if not df.empty:
    # Asset Selector
    unique_assets = df['symbol'].unique().tolist()
    unique_assets.sort()
    
    st.sidebar.subheader("🔎 Asset Search")
    selected_asset = st.sidebar.selectbox(
        "Select ETF to Analyze:", 
        options=unique_assets,
        index=0
    )
    
    st.sidebar.info("Data updates every minute via n8n pipeline.")

# --- 4. MAIN LAYOUT ---

if df.empty:
    st.error("Connection Error or No Data. Please check your Supabase API keys.")
else:
    # Filter data for the selected asset ()
    asset_data = df[df['symbol'] == selected_asset].sort_values('ingested_at')
    latest_record = asset_data.iloc[-1]

    # --- SECTION 1: ASSET DEEP DIVE () ---
    st.title(f"{selected_asset} Analysis")
    st.markdown(f"##### {selected_asset} / USD Market Overview")
    
    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Current Price", f"${latest_record['price']:.2f}", f"{latest_record['change_pct']:.2f}%")
    with m2:
        st.metric("24h Range", f"${latest_record['day_low']:.2f} - ${latest_record['day_high']:.2f}")
    with m3:
        st.metric("Intraday Volatility", f"{latest_record['volatility_spread']:.2f}%")
    with m4:
        st.metric("Signal Status", "🟢 BULLISH" if latest_record['change_pct'] > 0 else "🔴 BEARISH")

    # Main Chart Container (DeFiLlama Style Area Chart)
    st.markdown("### 📈 Price Evolution (Live Feed)")
    
    # If we have history.
    fig_main = go.Figure()
    
    # Price Area
    fig_main.add_trace(go.Scatter(
        x=asset_data['ingested_at'], 
        y=asset_data['price'],
        mode='lines' if len(asset_data) > 1 else 'markers',
        fill='tozeroy',
        name='Price',
        line=dict(color='#00d4ff', width=2),
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))

    fig_main.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#2d3342')
    )
    st.plotly_chart(fig_main, use_container_width=True)

    # --- SECTION 2: MARKET INTELLIGENCE () ---
    st.markdown("---")
    st.subheader("🧠 Competitive Intelligence & Market Scanner")

    # Layout: High Volatility Table (Left) & Market Structure (Right)
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("**🔥 Top Movers (Volatility Radar)**")
        
        # Prepare table data
        scanner_df = df.sort_values('ingested_at').groupby('symbol').tail(1) # Get latest for all
        top_vol = scanner_df.nlargest(10, 'volatility_spread')[['symbol', 'price', 'change_pct', 'volatility_spread']]
        
        # NATIVE STREAMLIT COLUMN CONFIG ()
        st.dataframe(
            top_vol,
            use_container_width=True,
            column_config={
                "symbol": "Asset",
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "change_pct": st.column_config.NumberColumn(
                    "24h Change", 
                    format="%.2f%%", 
                ),
                "volatility_spread": st.column_config.ProgressColumn(
                    "Volatility Impact",
                    format="%.2f%%",
                    min_value=0,
                    max_value=top_vol['volatility_spread'].max(),
                ),
            },
            hide_index=True
        )

    with c2:
        st.markdown("**📊 Market Composition**")
        # Donut Chart
        bulls = len(scanner_df[scanner_df['change_pct'] > 0])
        bears = len(scanner_df[scanner_df['change_pct'] <= 0])
        
        fig_donut = px.pie(
            names=['Bullish Assets', 'Bearish Assets'], 
            values=[bulls, bears],
            hole=0.6,
            color_discrete_sequence=['#00E396', '#FF4560'],
            template="plotly_dark"
        )
        fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
        # Add center text
        fig_donut.add_annotation(text=f"{len(scanner_df)}", showarrow=False, font_size=24, font_color="white")
        fig_donut.add_annotation(text="Total Assets", showarrow=False, dy=20, font_size=12, font_color="#888")
        
        st.plotly_chart(fig_donut, use_container_width=True)

    # --- SECTION 3: FULL DATA EXPLORER ---
    with st.expander("📂 Open Full Data Ledger"):
        st.dataframe(
            scanner_df.sort_values('change_pct', ascending=False),
            use_container_width=True,
            column_config={
                "price": st.column_config.NumberColumn(format="$%.2f"),
                "change_pct": st.column_config.NumberColumn(format="%.2f%%"),
                "day_high": st.column_config.NumberColumn(format="$%.2f"),
                "day_low": st.column_config.NumberColumn(format="$%.2f"),
            }
        )
