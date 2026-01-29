import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ETF Alpha Terminal", layout="wide", initial_sidebar_state="collapsed")

# CSS para el look "Dark Terminal"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    h1, h2, h3 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CONEXIÓN ---
def get_engine():
    # Extraemos los datos de los secrets de Streamlit
    user = st.secrets["db_user"]
    pwd = st.secrets["db_password"]
    host = st.secrets["db_host"]
    port = st.secrets["db_port"]
    db = st.secrets["db_name"]
    # Construcción de la URL de conexión directa
    return create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    # tabla
    query = "SELECT *, (day_high - day_low) as vol_calc FROM raw_etf_market_data WHERE price > 0"
    df = pd.read_sql(query, engine)
    return df

# --- CUERPO DEL DASHBOARD ---
st.title("⚡ ETF ALPHA TERMINAL")
st.markdown(f"**Market Status:** 🟢 Live | **Port:** 5432")
st.write("---")

try:
    df = load_data()

    # KPIs Principales
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total Assets", len(df))
    with k2:
        st.metric("Avg Price", f"${df['price'].mean():.2f}")
    with k3:
        top_vol = df.nlargest(1, 'vol_calc')
        st.metric("Top Volatility", top_vol['symbol'].values[0], f"${top_vol['vol_calc'].values[0]:.2f}")

    # Gráficos
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Distribución de Precios")
        fig = px.histogram(df, x="price", nbins=50, color_discrete_sequence=['#00ffcc'], template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("Top 10 Volátiles")
        fig_bar = px.bar(df.nlargest(10, 'vol_calc'), x='vol_calc', y='symbol', orientation='h', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Explorador de Datos
    st.subheader("Market Explorer")
    st.dataframe(df.sort_values('price', ascending=False), use_container_width=True)

except Exception as e:
    st.error("⚠️ Error de conexión detectado:")
    st.code(str(e))
    st.info("Revisá que los Secrets en Streamlit coincidan exactamente con los de Supabase.")
