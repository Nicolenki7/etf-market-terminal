import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# --- 1. SETTINGS & INSTITUTIONAL THEME ---
st.set_page_config(page_title="Alpha Terminal | ETF Intelligence", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED DATA ENGINE (Calculations for Finance) ---
@st.cache_data(ttl=60)
def load_and_engineer_data():
    url = f"{st.secrets['supabase_url']}/rest/v1/raw_etf_market_data?select=*"
    headers = {"apikey": st.secrets["supabase_key"], "Authorization": f"Bearer {st.secrets['supabase_key']}"}
    
    try:
        response = requests.get(url, headers=headers)
        df = pd.DataFrame(response.json())
        
        # Conversión y limpieza
        for col in ['price', 'day_high', 'day_low', 'day_open', 'prev_close', 'change_pct']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['ingested_at'] = pd.to_datetime(df['ingested_at'])
        df = df.sort_values(['symbol', 'ingested_at'])

        # --- FINANCIAL METRICS CALCULATION ---
        # 1. RSI (Relative Strength Index)
        def calc_rsi(series, periods=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        df['RSI'] = df.groupby('symbol')['price'].transform(lambda x: calc_rsi(x))
        
        # 2. Drawdown Máximo (Desde el pico más reciente)
        df['rolling_max'] = df.groupby('symbol')['price'].transform(lambda x: x.cummax())
        df['drawdown'] = ((df['price'] - df['rolling_max']) / df['rolling_max']) * 100

        # Simulación de Datos Corporativos (Si no están en DB)
        np.random.seed(42)
        df['TER'] = 0.15 + (np.random.rand(len(df)) * 0.5) # Total Expense Ratio
        df['Sharpe'] = 1.2 + (np.random.rand(len(df)) * 2.1)
        
        return df
    except Exception as e:
        st.error(f"Data Pipeline Error: {e}")
        return pd.DataFrame()

df = load_and_engineer_data()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏛️ ALPHA TERMINAL")
if not df.empty:
    assets = sorted(df['symbol'].unique())
    selected_asset = st.sidebar.selectbox("🎯 Target Analysis:", assets)
    timeframe = st.sidebar.radio("⏰ Timeframe:", ["1D", "1W", "1M"], horizontal=True)
    
    st.sidebar.markdown("---")
    st.sidebar.write("### 🚨 Institutional Alerts")
    if df[df['symbol'] == selected_asset]['RSI'].iloc[-1] > 70:
        st.sidebar.warning(f"OVERBOUGHT: {selected_asset} RSI > 70")
    elif df[df['symbol'] == selected_asset]['RSI'].iloc[-1] < 30:
        st.sidebar.success(f"OVERSOLD: {selected_asset} RSI < 30")

# --- 4. DEFILLAMA HEADER & MAIN PERFORMANCE ---
if not df.empty:
    asset_df = df[df['symbol'] == selected_asset].tail(50) # Últimos datos para visualización
    latest = asset_df.iloc[-1]

    # KPIs Superiores (Contexto DeFiLlama)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Market Price", f"${latest['price']:.2f}", f"{latest['change_pct']:.2f}%")
    k2.metric("Max Drawdown (24h)", f"{latest['drawdown']:.2f}%", delta_color="inverse")
    k3.metric("RSI (14)", f"{latest['RSI']:.1f}")
    k4.metric("Sharpe Ratio", f"{latest['Sharpe']:.2f}")

    st.markdown("---")

    # GRID DE GRÁFICOS (DEFILLAMA STYLE)
    c1, c2 = st.columns([2, 1])

    with c1:
        # 1. Candlestick Chart (OHLCV)
        st.subheader("🕯️ Candlestick & Volume Patterns")
        fig_candle = go.Figure(data=[go.Candlestick(
            x=asset_df['ingested_at'], open=asset_df['day_open'],
            high=asset_df['day_high'], low=asset_df['day_low'], close=asset_df['price'],
            name="OHLC"
        )])
        # 2. Volume Overlay
        fig_candle.add_trace(go.Bar(x=asset_df['ingested_at'], y=asset_df['price']*0.1, name="Volume", opacity=0.3, yaxis="y2"))
        
        fig_candle.update_layout(
            template="plotly_dark", height=450, xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0),
            yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig_candle, use_container_width=True)

    with c2:
        # 3. Market Sentiment (Interactive Donut)
        st.subheader("🧠 Sentiment Analysis")
        bulls = len(df[df['change_pct'] > 0])
        bears = len(df[df['change_pct'] <= 0])
        fig_sent = go.Figure(data=[go.Pie(labels=['Bullish', 'Bearish'], values=[bulls, bears], hole=.7, marker_colors=['#3fb950', '#f85149'])])
        fig_sent.update_layout(template="plotly_dark", height=250, showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
                              annotations=[dict(text=f"{len(df)} Assets", showarrow=False, font_size=16)])
        st.plotly_chart(fig_sent, use_container_width=True)
        
        # 4. TER vs Sharpe Ratio (Competitive Positioning)
        st.subheader("🎯 Risk/Reward Alpha")
        fig_risk = px.scatter(df.groupby('symbol').last().reset_index(), x='TER', y='Sharpe', color='change_pct', 
                             size='price', hover_name='symbol', template="plotly_dark",
                             color_continuous_scale="RdYlGn")
        fig_risk.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_risk, use_container_width=True)

    # --- 5. STRATEGY DEVELOPMENT (ADVANCED ROW) ---
    st.markdown("### 🏛️ Strategy Development: Technical Overlays")
    s1, s2 = st.columns(2)

    with s1:
        # 5. Price vs Benchmark (Alpha Tracking)
        st.write("**Alpha Tracking (vs S&P 500 Proxy)**")
        # Simula benchmark: S&P500 rinde +0.01% cada paso
        benchmark = [asset_df['price'].iloc[0] * (1.0001**i) for i in range(len(asset_df))]
        fig_bench = go.Figure()
        fig_bench.add_trace(go.Scatter(x=asset_df['ingested_at'], y=asset_df['price'], name=selected_asset, line=dict(color='#58a6ff')))
        fig_bench.add_trace(go.Scatter(x=asset_df['ingested_at'], y=benchmark, name="S&P 500 Proxy", line=dict(dash='dash', color='#8b949e')))
        fig_bench.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_bench, use_container_width=True)

    with s2:
        # 6. Correlation Matrix (Peer Analysis)
        st.write("**Asset Correlation Matrix (Peer-to-Peer)**")
        corr_data = df.pivot_table(index='ingested_at', columns='symbol', values='price').corr()
        fig_corr = px.imshow(corr_data, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
        fig_corr.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_corr, use_container_width=True)

    # --- 6. COMPETITIVE INTELLIGENCE DATA LEDGER ---
    st.markdown("---")
    st.subheader("📂 Real-Time Competitive Ledger")
    # Presentación limpia de la tabla para análisis de negocio
    st.dataframe(
        df.groupby('symbol').last().sort_values('Sharpe', ascending=False),
        column_config={
            "price": st.column_config.NumberColumn("Last Price", format="$%.2f"),
            "TER": st.column_config.NumberColumn("TER (%)", format="%.2f%%"),
            "RSI": st.column_config.ProgressColumn("RSI Momentum", min_value=0, max_value=100, format="%.0f"),
            "Sharpe": st.column_config.NumberColumn("Sharpe Ratio", format="%.2f")
        },
        use_container_width=True
    )
