"""Alpha Terminal — panel de ETFs sobre precios versionados.

Antes leía de Supabase con `st.secrets`; esa credencial ya no existe y el panel
quedaba inservible. Ahora lee data/etf_monthly.csv, que se versiona en el repo y
lo regenera src/fetch_data.py desde el endpoint público de Yahoo.

Todas las métricas se calculan con los cierres: no hay TER, ni Sharpe simulado,
ni benchmark inventado. Si un dato no está en la fuente, no se muestra.

Uso: streamlit run app.py
"""
import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATOS = pathlib.Path(__file__).resolve().parent / "data" / "etf_monthly.csv"

st.set_page_config(page_title="Alpha Terminal | ETF Intelligence", layout="wide", page_icon="🏛️")
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def cargar():
    """Lee el CSV versionado y agrega las métricas que se derivan de él."""
    df = pd.read_csv(DATOS).sort_values(["ticker", "fecha"])
    df["ret"] = df.groupby("ticker")["close"].pct_change()
    df["pico"] = df.groupby("ticker")["close"].transform("cummax")
    df["drawdown"] = (df["close"] / df["pico"] - 1) * 100
    return df


def rsi(serie, periodos=14):
    """RSI clásico de Wilder sobre la serie de cierres disponibles."""
    delta = serie.diff()
    sube = delta.where(delta > 0, 0).rolling(periodos).mean()
    baja = -delta.where(delta < 0, 0).rolling(periodos).mean()
    rs = sube / baja.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


df = cargar()

if df.empty:
    st.error(f"No encuentro {DATOS}. Ejecuta `python src/fetch_data.py` para regenerarlo.")
    st.stop()

st.sidebar.title("🏛️ ALPHA TERMINAL")
activo = st.sidebar.selectbox("🎯 Target Analysis:", sorted(df["ticker"].unique()))
ventana = st.sidebar.radio("⏰ Ventana:", ["12m", "24m", "todo"], horizontal=True)
meses = {"12m": 12, "24m": 24, "todo": 10_000}[ventana]

g = df[df.ticker == activo].tail(meses + 1).copy()
g["rsi"] = rsi(g["close"])

ultimo = g.iloc[-1]
ret_acum = (ultimo["close"] / g["close"].iloc[0] - 1) * 100
vol = float(g["ret"].std() * np.sqrt(12) * 100)

st.sidebar.markdown("---")
st.sidebar.write("### 🚨 Señales (RSI 14)")
if pd.notna(ultimo["rsi"]):
    if ultimo["rsi"] > 70:
        st.sidebar.warning(f"SOBRECOMPRA: {activo} RSI {ultimo['rsi']:.0f}")
    elif ultimo["rsi"] < 30:
        st.sidebar.success(f"SOBREVENTA: {activo} RSI {ultimo['rsi']:.0f}")
    else:
        st.sidebar.info(f"Zona neutra: RSI {ultimo['rsi']:.0f}")
else:
    st.sidebar.info("Sin historia suficiente para el RSI en esta ventana.")

st.title(f"{activo} · cierre {ultimo['fecha']}")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Último cierre", f"${ultimo['close']:.2f}", f"{ultimo['ret']*100:+.2f}% mes")
k2.metric("Retorno en ventana", f"{ret_acum:+.1f}%", f"{meses if meses < 10_000 else 'toda la serie'} meses")
k3.metric("Drawdown actual", f"{ultimo['drawdown']:.1f}%", delta_color="inverse")
k4.metric("Volatilidad anual", f"{vol:.1f}%")

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("🕯️ Precio de cierre y drawdown")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["fecha"], y=g["close"], name="Cierre", line=dict(color="#58a6ff")))
    fig.add_trace(go.Scatter(x=g["fecha"], y=g["drawdown"], name="Drawdown %",
                             line=dict(color="#f85149"), yaxis="y2"))
    fig.update_layout(template="plotly_dark", height=420, xaxis_rangeslider_visible=False,
                      yaxis2=dict(title="Drawdown %", overlaying="y", side="right", showgrid=False),
                      margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🧠 Cierres al alza")
    ultimos = df.groupby("ticker").last()
    alza = int((ultimos["ret"] > 0).sum())
    fig_s = go.Figure(data=[go.Pie(labels=["Al alza", "A la baja"], values=[alza, len(ultimos) - alza],
                                   hole=.7, marker_colors=["#3fb950", "#f85149"])])
    fig_s.update_layout(template="plotly_dark", height=230, showlegend=False,
                        margin=dict(l=0, r=0, t=0, b=0),
                        annotations=[dict(text=f"{len(ultimos)} ETFs", showarrow=False, font_size=14)])
    st.plotly_chart(fig_s, use_container_width=True)

st.subheader("📊 Retorno por año")
anual = df.copy()
anual["anio"] = anual["fecha"].str[:4]
anual = anual.dropna(subset=["ret"]).groupby(["ticker", "anio"])["ret"].apply(lambda s: ((1 + s).prod() - 1) * 100)
tabla_anual = anual.unstack("anio").round(1)
st.dataframe(tabla_anual, use_container_width=True)

st.subheader("🔗 Correlación de retornos mensuales")
piv = df.pivot_table(index="fecha", columns="ticker", values="ret")
fig_corr = px.imshow(piv.corr(), text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")
fig_corr.update_layout(height=380, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_corr, use_container_width=True)

st.subheader("📂 Ledger competitivo")
ledger = df.groupby("ticker").agg(
    ultimo_cierre=("close", "last"),
    retorno_acum=("close", lambda s: (s.iloc[-1] / s.iloc[0] - 1) * 100),
    drawdown_max=("drawdown", "min"),
    volatilidad=("ret", lambda s: s.std() * np.sqrt(12) * 100),
).round(2).sort_values("retorno_acum", ascending=False)
st.dataframe(ledger, use_container_width=True)
st.caption("Fuente: data/etf_monthly.csv · cierres mensuales, sin dividendos. Sin Supabase y sin métricas simuladas.")
