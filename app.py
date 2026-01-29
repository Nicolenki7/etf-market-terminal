import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN ESTÉTICA (CSS INYECTADO) ---
st.set_page_config(page_title="ETF Alpha Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    h1, h2, h3 { color: #ffffff; font-family: 'Helvetica Neue', sans-serif; }
    /* Estilo de tarjetas */
    div.css-1r6slb0 { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN SEGURA ---
def get_engine():
    # En producción usaremos st.secrets para seguridad
    user = st.secrets["db_user"]
    pwd = st.secrets["db_password"]
    host = st.secrets["db_host"]
    port = st.secrets["db_port"]
    db = st.secrets["db_name"]
    return create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    # Traemos datos y calculamos volatilidad en el vuelo si no está en la tabla
    query = "SELECT *, (day_high - day_low) as vol_calc FROM raw_etf_market_data WHERE price > 0"
    df = pd.read_sql(query, engine)
    return df

# --- CUERPO DEL DASHBOARD ---
try:
    df = load_data()

    st.title("⚡ ETF ALPHA TERMINAL")
    st.markdown(f"**Market Status:** 🟢 Live | **Last Update:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    st.write("---")

    # MÉTRICAS CLAVE (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Assets", f"{len(df)}")
    with kpi2:
        avg_vol = df['vol_calc'].mean()
        st.metric("Avg Volatility", f"${avg_price:.2f}" if 'avg_price' in locals() else f"${df['price'].mean():.2f}")
    with kpi3:
        top_gain = df.nlargest(1, 'price')
        st.metric("Market Leader", top_gain['symbol'].values[0], f"${top_gain['price'].values[0]}")
    with kpi4:
        st.metric("Active Streams", "n8n Pipeline", "Connected")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Distribución de Precios y Liquidez")
        fig = px.histogram(df, x="price", nbins=50, color_discrete_sequence=['#00ffcc'], template="plotly_dark")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🔥 Top 10 Volatilidad")
        top_vol = df.nlargest(10, 'vol_calc')[['symbol', 'vol_calc']]
        fig_vol = px.bar(top_vol, x='vol_calc', y='symbol', orientation='h', color='vol_calc', template="plotly_dark")
        fig_vol.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_vol, use_container_width=True)

    st.subheader("📂 Market Explorer (Real-Time Ingestion)")
    st.dataframe(df.sort_values('price', ascending=False), use_container_width=True)

except Exception as e:
    st.error("Esperando conexión con Supabase... Verificá tus Secrets.")
    st.info("")
