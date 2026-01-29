import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ETF Alpha Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DATOS ---
def get_engine():
    # Acceso a los secrets
    user = st.secrets["db_user"]
    pwd = st.secrets["db_password"]
    host = st.secrets["db_host"]
    port = st.secrets["db_port"]
    db = st.secrets["db_name"]
    
    # URL de conexión directa
    db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    
    # (timeout) para ayudar a la red
    return create_engine(
        db_url, 
        connect_args={'connect_timeout': 10}
    )

@st.cache_data(ttl=300)
def load_data():
    engine = get_engine()
    query = "SELECT *, (day_high - day_low) as vol_calc FROM raw_etf_market_data"
    return pd.read_sql(query, engine)

# --- DASHBOARD ---
st.title("⚡ ETF ALPHA TERMINAL")
st.write("---")

try:
    df = load_data()
    
    # Limpieza básica
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df = df[df['price'] > 0]

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Activos en BD", len(df))
    c2.metric("Precio Promedio", f"${df['price'].mean():.2f}")
    c3.metric("Max Volatilidad", df['symbol'].iloc[df['vol_calc'].idxmax()])

    # Gráfico de barras
    st.subheader("Top 15 ETFs por Precio")
    fig = px.bar(df.nlargest(15, 'price'), x='symbol', y='price', template='plotly_dark', color='price')
    st.plotly_chart(fig, use_container_width=True)

    # Explorador
    st.subheader("Explorador de Datos (Supabase Live)")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("🚨 Falló la conexión con la base de datos.")
    st.code(str(e))
    st.info("Si el error persiste, es probable que Streamlit Cloud no soporte la conexión IPv6 de Supabase Free.")
