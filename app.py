import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ETF Alpha Terminal", layout="wide")

# --- MOTOR DE DATOS VIA API ---
@st.cache_data(ttl=60) # Actualiza cada 1 minuto para que esté "vivo"
def load_data_api():
    # URL y la Key de los secrets
    url = f"{st.secrets['supabase_url']}/rest/v1/raw_etf_market_data?select=*"
    headers = {
        "apikey": st.secrets["supabase_key"],
        "Authorization": f"Bearer {st.secrets['supabase_key']}"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Error API: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de red: {e}")
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("⚡ ETF ALPHA TERMINAL")
st.markdown(f"**Status:** 🟢 Live Connection")

df = load_data_api()

if not df.empty:
    # strings a números
    for col in ['price', 'day_high', 'day_low']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # KPIs Rápidos
    c1, c2 = st.columns(2)
    c1.metric("Activos Registrados", len(df))
    c2.metric("Precio Promedio", f"${df['price'].mean():.2f}")

    # Tabla
    st.subheader("Vaciado de Mercado en Tiempo Real")
    st.dataframe(df.sort_values('price', ascending=False), use_container_width=True)
else:
    st.warning("Conectado, pero la tabla está vacía. Verificá que n8n esté enviando datos.")
