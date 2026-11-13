"""Construye docs/report.html del terminal de ETFs a partir de los cierres mensuales.

Uso: python src/build_report.py
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from report import escribir, num

ROOT = pathlib.Path(__file__).resolve().parents[1]
d = (pd.read_csv(ROOT / "data" / "etf_monthly.csv")
     .drop_duplicates(subset=["fecha", "ticker"], keep="last")
     .sort_values(["ticker", "fecha"]))
d["ret"] = d.groupby("ticker").close.pct_change() * 100
d["anio"] = d.fecha.str[:4]

filas, tabla = [], []
for t, g in d.groupby("ticker"):
    g = g.dropna(subset=["close"])
    acum = (g.close.iloc[-1] / g.close.iloc[0] - 1) * 100
    pico = g.close.cummax()
    dd = float(((g.close - pico) / pico).min() * 100)
    r = g.ret.dropna()
    vol = float(r.std() * (12 ** 0.5))
    sharpe = float(r.mean() / r.std() * (12 ** 0.5)) if r.std() else 0.0
    filas.append({"a": "todos", "g": "acumulado", "k": t, "v": round(acum, 1), "u": "%"})
    filas.append({"a": "todos", "g": "drawdown", "k": t, "v": round(dd, 1), "u": "%"})
    filas.append({"a": "todos", "g": "volatilidad", "k": t, "v": round(vol, 1), "u": "%"})
    for anio, gy in g.dropna(subset=["ret"]).groupby("anio"):
        anual = ((1 + gy.ret / 100).prod() - 1) * 100
        filas.append({"a": "todos", "g": "anual", "k": f"{t} {anio}", "v": round(float(anual), 1), "u": "%"})
    tabla.append([t, num(g.close.iloc[-1], 2), f"{num(acum, 1)} %", f"{num(dd, 1)} %",
                  f"{num(vol, 1)} %", num(sharpe, 2)])
tabla.sort(key=lambda r: float(r[2].replace(" %", "").replace(",", ".")), reverse=True)

ventana = f"{d.fecha.min()} → {d.fecha.max()}"
peor = min(tabla, key=lambda x: float(x[3].replace(" %", "").replace(",", ".")))

escribir(
    ROOT / "docs" / "report.html",
    eyebrow="ETFs · precios de cierre mensuales",
    titulo="ETFs: cuánto rinde cada uno y cuánto duele en el peor momento",
    pregunta=("Cinco ETFs, tres años de cierres mensuales y una pregunta que el retorno solo no "
              "responde: dos fondos pueden acabar el período en el mismo sitio habiendo sufrido "
              "caídas muy distintas por el camino. El drawdown y la volatilidad son la otra mitad "
              "de la historia."),
    kpis=[("Ventana", ventana, "cierres mensuales"),
          ("ETFs", num(d.ticker.nunique()), "SPY, QQQ, IVV, IEMG, GLD"),
          ("Mejor acumulado", tabla[0][0], f"{tabla[0][2]} en el período"),
          ("Peor drawdown", peor[0], peor[3])],
    filtros=None,
    graficos=[
        {"id": "a", "grupo": "acumulado", "titulo": "Retorno acumulado en la ventana",
         "subtitulo": "% desde el primer cierre hasta el último", "unidad": "%"},
        {"id": "m", "grupo": "anual", "titulo": "Retorno por año",
         "subtitulo": "cada año completo de la ventana, compuesto mes a mes", "unidad": "%"},
        {"id": "d", "grupo": "drawdown", "titulo": "Drawdown máximo",
         "subtitulo": "la peor caída desde un máximo previo, en %", "unidad": "%"},
        {"id": "v", "grupo": "volatilidad", "titulo": "Volatilidad anualizada",
         "subtitulo": "desviación típica de los retornos mensuales, anualizada", "unidad": "%"},
    ],
    filas=filas,
    tabla={"titulo": "El cuadro completo", "subtitulo": "ordenado por retorno acumulado",
           "cabeceras": ["ETF", "Último cierre", "Acumulado", "Drawdown", "Volatilidad", "Sharpe"],
           "filas": tabla},
    metodo=["El CSV se versiona en data/etf_monthly.csv y lo regenera src/fetch_data.py desde el endpoint público de Yahoo.",
            "Retorno acumulado = último cierre / primer cierre - 1, sobre cierres mensuales, sin dividendos.",
            "Drawdown = mínimo de (cierre - máximo previo) / máximo previo dentro de la ventana.",
            "Sharpe = media de retornos mensuales / desviación típica × √12; sin tasa libre de riesgo."],
    limitaciones=["Son cierres mensuales: no hay máximos ni mínimos intradía, así que el drawdown real es mayor.",
                  "No incluye dividendos; en IVV y SPY eso subestima el retorno entre 1 y 2 puntos al año.",
                  "Yahoo es una fuente de conveniencia, no un proveedor oficial de mercado.",
                  "Cinco ETFs y tres años: no alcanza para concluir nada sobre estrategias."],
    fuente="data/etf_monthly.csv (185 filas, 5 tickers)",
    metodo_sub="Todo sale de cierres mensuales versionados; no hay métricas simuladas.",
    lim_sub="Los límites de trabajar con cierres mensuales.")
print("docs/report.html:", (ROOT / "docs" / "report.html").stat().st_size, "bytes")
