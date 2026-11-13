"""Descarga los precios mensuales de cierre que usa el terminal.

Fuente: endpoint público de gráficos de Yahoo Finance (sin clave ni registro).
Se versiona el resultado en data/etf_monthly.csv para que el informe y la app
puedan reconstruirse sin red y para que cualquier cifra sea auditable.

Uso: python src/fetch_data.py [--range 3y]
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import urllib.request

TICKERS = ["SPY", "QQQ", "IVV", "IEMG", "GLD"]
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{t}?range={r}&interval=1mo"


def bajar(ticker, rango, cabecera):
    peticion = urllib.request.Request(URL.format(t=ticker, r=rango), headers=cabecera)
    datos = json.load(urllib.request.urlopen(peticion, timeout=30))
    res = datos["chart"]["result"][0]
    cierres = res["indicators"]["quote"][0]["close"]
    for sello, cierre in zip(res["timestamp"], cierres):
        if cierre is None:
            continue
        fecha = dt.datetime.fromtimestamp(sello, dt.timezone.utc).strftime("%Y-%m")
        yield {"fecha": fecha, "ticker": ticker, "close": round(float(cierre), 2)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", default="3y")
    a = ap.parse_args()
    cab = {"User-Agent": "Mozilla/5.0 (compatible; etf-market-terminal/1.0)"}
    filas = [f for t in TICKERS for f in bajar(t, a.range, cab)]
    unicos = {}
    for f in filas:
        unicos[(f["fecha"], f["ticker"])] = f  # el endpoint repite el mes en curso
    filas = sorted(unicos.values(), key=lambda x: (x["fecha"], x["ticker"]))
    raiz = pathlib.Path(__file__).resolve().parents[1]
    destino = raiz / "data" / "etf_monthly.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha", "ticker", "close"])
        w.writeheader()
        w.writerows(filas)
    print(destino, len(filas), "filas")
