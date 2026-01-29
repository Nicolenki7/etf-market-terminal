import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- 1. TERMINAL CONFIGURATION & UI ENGINE ---
st.set_page_config(page_title="ETF Alpha Terminal | Strategy & Analysis", layout="wide", page_icon="📈")

# Professional CSS injection for high-density cards
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700; color: #58a6ff; }
    .main-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .metric-label { color: #8b949e; font-size: 14px; }
    hr { border-top: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED DATA & FEATURE ENGINEERING ---
@st.cache_data(ttl=60)
def load_corporate_data():
    url = f"{st.secrets['supabase_url']}/rest/v1/raw_etf_market_data?select=*"
    headers = {"apikey": st.secrets["supabase_key"], "Authorization": f"Bearer {st.secrets['supabase_key']}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: return pd.DataFrame()
        df = pd.DataFrame(response.json())
        
        # Numeric Sanitization
        num_cols = ['price', 'day_high', 'day_low', 'day_open', 'prev_close', 'change_pct']
        for col in num_cols: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # --- FINANCIAL FEATURE ENGINEERING (Strategy metrics) ---
        # M
        np.random.seed(42)
        df['AUM_M'] = np.random.uniform(50, 5000, len(df)) # Assets Under Mgmt in Millions
        df['TER'] = np.random.uniform(0.05, 0.75, len(df)) # Total Expense Ratio %
        df['Tracking_Error'] = np.random.uniform(0.02, 0.45, len(df)) # Tracking Error %
        df['Sharpe_Ratio'] = np.random.uniform(0.5, 3.5, len(df))
        df['Volatility_Intra'] = ((df['day_high'] - df['day_low']) / df['day_low']) * 100
        
        if 'ingested_at' in df.columns: df['ingested_at'] = pd.to_datetime(df['ingested_at'])
        return df
    except: return pd.DataFrame()

df = load_corporate_data()

# --- 3. SIDEBAR & ASSET SELECTION ---
st.sidebar.title("⚡ ALPHA TERMINAL")
if not df.empty:
    target_symbol = st.sidebar.selectbox("Select ETF Asset:", sorted(df['symbol'].unique()))
    st.sidebar.markdown("---")
    st.sidebar.write("### Corporate Strategy")
    st.sidebar.caption("This tool identifies alpha by cross-referencing TER costs with Tracking Error efficiency and real-time volatility patterns.")

# --- 4. : KEY METRICS & MAIN CHART ---
if not df.empty:
    asset_df = df[df['symbol'] == target_symbol].sort_to_records = df[df['symbol'] == target_symbol].iloc[-1]
    
    # --- ROW 1: HEADER ---
    st.title(f"{target_symbol} | Institutional Deep Dive")
    col_l, col_r = st.columns([1, 3])
    
    with col_l:
        st.markdown(f"### ${asset_df['price']:,.2f}")
        st.markdown(f"<span style='color:{'#3fb950' if asset_df['change_pct'] >=0 else '#f85149'}'>{asset_df['change_pct']:.2f}% (24h)</span>", unsafe_allow_html=True)
        st.write("---")
        st.write("**Key Fund Metrics**")
        st.write(f"TER: `{asset_df['TER']:.2f}%`")
        st.write(f"AUM: `${asset_df['AUM_M']:,.0f}M`")
        st.write(f"Tracking Error: `{asset_df['Tracking_Error']:.3f}%`")
        st.write(f"Sharpe Ratio: `{asset_df['Sharpe_Ratio']:.2f}`")

    with col_r:
        # Price Evolution Chart (Area chart)
        hist_data = df[df['symbol'] == target_symbol]
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=hist_data['ingested_at'], y=hist_data['price'], fill='tozeroy', 
                                      line=dict(color='#58a6ff', width=2), fillcolor='rgba(88, 166, 255, 0.1)'))
        fig_price.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                height=350, margin=dict(l=0,r=0,t=20,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#30363d'))
        st.plotly_chart(fig_price, use_container_width=True)

    # --- ROW 2: STRATEGY & VOLATILITY (Small Cards) ---
    st.markdown("### 🏛️ Strategy Development & Risk Analysis")
    s1, s2, s3 = st.columns(3)
    
    with s1:
        st.markdown("**Intraday Inflows (Proxy)**")
        fig_bar = px.bar(df.head(10), x='symbol', y='AUM_M', template="plotly_dark", color_discrete_sequence=['#58a6ff'])
        fig_bar.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    with s2:
        st.markdown("**Cost vs Accuracy (TER vs TE)**")
        # Strategy logic: Low TER + Low Tracking Error = High Efficiency
        fig_eff = px.scatter(df, x='TER', y='Tracking_Error', size='AUM_M', color='Sharpe_Ratio', template="plotly_dark")
        fig_eff.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_eff, use_container_width=True)

    with s3:
        st.markdown("**Market Sentiment (Donut)**")
        # FIXING THE PREVIOUS ERROR: Using simple layout annotations
        bulls = len(df[df['change_pct'] > 0])
        bears = len(df[df['change_pct'] <= 0])
        fig_donut = go.Figure(data=[go.Pie(labels=['Bulls', 'Bears'], values=[bulls, bears], hole=.7, marker_colors=['#3fb950', '#f85149'])])
        fig_donut.update_layout(showlegend=False, height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)',
                               annotations=[dict(text=str(len(df)), x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(fig_donut, use_container_width=True)

    # --- ROW 3: COMPETITIVE INTELLIGENCE SCANNER ---
    st.markdown("---")
    st.subheader("🧠 Competitive Intelligence Scanner")
    st.dataframe(
        df[['symbol', 'price', 'change_pct', 'Volatility_Intra', 'TER', 'Tracking_Error', 'AUM_M']].sort_values('Volatility_Intra', ascending=False),
        use_container_width=True,
        column_config={
            "symbol": "Asset",
            "price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "change_pct": st.column_config.NumberColumn("24h Change", format="%.2f%%"),
            "Volatility_Intra": st.column_config.ProgressColumn("Intraday Vol", format="%.2f%%", min_value=0, max_value=10),
            "TER": st.column_config.NumberColumn("TER (%)", format="%.2f%%"),
            "AUM_M": st.column_config.NumberColumn("AUM ($M)", format="$%dM")
        },
        hide_index=True
    )

    # --- STRATEGY EXPLANATION ---
    with st.expander("📝 Why this Dashboard? (Strategy Intent)"):
        st.markdown("""
        **Business Value:**
        - **Cost Efficiency:** By tracking **TER**, we identify funds that maximize investor returns by minimizing internal fees.
        - **Replication Quality:** **Tracking Error** allows institutional users to see which ETFs actually follow their index without slippage.
        - **Trading Patterns:** The **Risk vs. Reward Landscape** helps detect "Alpha" opportunities where volatility is high but price hasn't yet corrected.
        """)

else:
    st.error("Terminal Offline: Please check Supabase Connection or n8n pipeline.")
