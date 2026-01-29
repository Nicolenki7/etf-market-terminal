import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO DUNE ANALYTICS ---
st.set_page_config(page_title="ETF Alpha Terminal", layout="wide", page_icon="⚡")

# CSS Avanzado para "Dune Analytics Style"
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #0d1117; }
    
    /* Métricas (KPIs) */
    div[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace; font-size: 24px; color: #ffffff; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #8b949e; }
    
    /* Contenedores tipo Tarjeta */
    div.css-1r6slb0, div.stDataFrame {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
    }
    
    /* Títulos */
    h1, h2, h3 { color: #e6edf3; font-family: 'Inter', sans-serif; }
    h4 { color: #7d8590; font-weight: 400; }
    
    /* Tablas */
    .stDataFrame { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INGENIERÍA DE DATOS (EXTRACCIÓN Y TRANSFORMACIÓN) ---
@st.cache_data(ttl=60)
def load_and_process_data():
    # Conexión vía API (Plan C - Resiliente)
    url = f"{st.secrets['supabase_url']}/rest/v1/raw_etf_market_data?select=*"
    headers = {
        "apikey": st.secrets["supabase_key"],
        "Authorization": f"Bearer {st.secrets['supabase_key']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return pd.DataFrame()
            
        df = pd.DataFrame(response.json())
        
        if df.empty:
            return df

        # Conversión de Tipos
        cols_num = ['price', 'day_high', 'day_low', 'day_open', 'prev_close', 'change_pct']
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- FEATURE ENGINEERING (Creación de nuevas métricas de negocio) ---
        # 1. Spread de Volatilidad Relativa (%)
        df['volatility_spread'] = ((df['day_high'] - df['day_low']) / df['day_low']) * 100
        
        # 2. Gap de Apertura (% diferencia entre cierre ayer y apertura hoy)
        df['gap_pct'] = ((df['day_open'] - df['prev_close']) / df['prev_close']) * 100
        
        # 3. Categorización de Mercado (Etiquetas de Negocio)
        def categorize_trend(row):
            if row['change_pct'] > 1.5: return '🚀 Bull Run'
            if row['change_pct'] < -1.5: return '🩸 Bearish'
            return '💤 Neutral'
        
        df['Trend_Status'] = df.apply(categorize_trend, axis=1)
        
        return df
        
    except Exception as e:
        st.error(f"Error en el pipeline de datos: {e}")
        return pd.DataFrame()

# --- 3. DASHBOARD ESTRATÉGICO ---

df = load_and_process_data()

# Encabezado
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("⚡ ETF Market Intelligence")
    st.markdown("##### Real-Time Competitive Analysis & Strategy Finder")
with col_header_2:
    if not df.empty:
        st.markdown(f"**Last Sync:** `{pd.Timestamp.now().strftime('%H:%M:%S UTC')}`")
        st.markdown(f"**API Status:** 🟢 Stable")

st.markdown("---")

if not df.empty:
    # --- SECCIÓN A: MARKET ANALYSIS (MACRO VIEW) ---
    # KPIs Globales para entender "la salud" del mercado hoy
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    bulls = len(df[df['change_pct'] > 0])
    bears = len(df[df['change_pct'] < 0])
    market_sentiment = "Bullish" if bulls > bears else "Bearish"
    sentiment_color = "#00E396" if bulls > bears else "#FF4560"

    kpi1.metric("Market Sentiment", market_sentiment, f"{bulls} vs {bears} assets")
    kpi2.metric("Avg. Volatility", f"{df['volatility_spread'].mean():.2f}%", help="Promedio de movimiento Intradía")
    kpi3.metric("Capital Flow Leader", df.sort_values('price', ascending=False).iloc[0]['symbol'])
    kpi4.metric("Assets Tracked", len(df), "via n8n pipeline")

    # --- SECCIÓN B: STRATEGY DEVELOPMENT (VISUALIZACIÓN) ---
    st.markdown("### 🛠️ Strategy Development & Patterns")
    
    col_chart_1, col_chart_2 = st.columns([2, 1])
    
    with col_chart_1:
        st.markdown("**Risk vs. Reward Landscape**")
        # Scatter plot para encontrar oportunidades: Alta Volatilidad + Cambio de Precio
        fig_scatter = px.scatter(
            df, 
            x="volatility_spread", 
            y="change_pct", 
            size="price", 
            color="Trend_Status",
            hover_name="symbol",
            color_discrete_map={'🚀 Bull Run': '#00E396', '🩸 Bearish': '#FF4560', '💤 Neutral': '#775DD0'},
            template="plotly_dark",
            labels={"volatility_spread": "Intraday Volatility (%)", "change_pct": "24h Price Change (%)"}
        )
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_chart_2:
        st.markdown("**Market Distribution**")
        # Pie chart de tendencias
        fig_pie = px.pie(df, names='Trend_Status', color='Trend_Status', 
                         color_discrete_map={'🚀 Bull Run': '#00E396', '🩸 Bearish': '#FF4560', '💤 Neutral': '#775DD0'},
                         hole=0.4, template="plotly_dark")
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- SECCIÓN C: COMPETITIVE INTELLIGENCE (TABLAS VIVAS) ---
    st.markdown("### 🧠 Competitive Intelligence")
    
    tab1, tab2, tab3 = st.tabs(["🔥 High Volatility (Day Trading)", "📉 Oversold (Buy the Dip)", "📂 Full Data"])
    
    with tab1:
        st.markdown("Activos con mayor movimiento intradía (Oportunidades de corto plazo)")
        # Filtramos los top 10 más volátiles
        top_vol = df.nlargest(10, 'volatility_spread')[['symbol', 'price', 'change_pct', 'volatility_spread', 'gap_pct']]
        st.dataframe(
            top_vol.style.format({"price": "${:.2f}", "change_pct": "{:.2f}%", "volatility_spread": "{:.2f}%", "gap_pct": "{:.2f}%"})
            .background_gradient(subset=['volatility_spread'], cmap='Purples'),
            use_container_width=True
        )

    with tab2:
        st.markdown("Activos con caídas fuertes (Posible rebote técnico)")
        # Filtramos los top 10 perdedores
        top_loss = df.nsmallest(10, 'change_pct')[['symbol', 'price', 'change_pct', 'prev_close', 'day_low']]
        st.dataframe(
            top_loss.style.format({"price": "${:.2f}", "change_pct": "{:.2f}%", "prev_close": "${:.2f}"})
            .text_gradient(subset=['change_pct'], cmap='RdYlGn', vmin=-5, vmax=0),
            use_container_width=True
        )

    with tab3:
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Esperando datos del pipeline... (n8n)")
