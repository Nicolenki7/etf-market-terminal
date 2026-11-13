# 🏛️ Alpha Terminal — ETF Analytics Platform

**Monthly closes in, real indicators out: RSI, drawdown, volatility, peer correlation**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📊 Interactive report

**[Open the interactive report →](https://nicolenki7.github.io/etf-market-terminal/report.html)** — accumulated return, max drawdown, annualised volatility and Sharpe per ETF, rebuilt from `data/etf_monthly.csv`.

---

## 📋 Overview

A Streamlit terminal that reads **committed monthly closes** and computes technical and risk indicators from them. No database, no API key, no credentials: the data is a versioned CSV, so a clone reproduces every number the app shows.

Five ETFs — SPY, QQQ, IVV, IEMG, GLD — over **185 monthly rows, 2023-12 → 2026-11**.

---

## 🛠️ Technical Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | Streamlit (Python) |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Data Processing** | Pandas, NumPy |
| **Data Source** | `data/etf_monthly.csv`, refreshed from the public Yahoo Finance chart endpoint |
| **Credentials** | None required |

---

## 🏗️ Architecture

```
Yahoo chart endpoint (public, no key)
        │  src/fetch_data.py  — deduplicates the current month
        ▼
 data/etf_monthly.csv   (185 rows: date, symbol, close)
        │
        ├── app.py              Streamlit terminal: RSI, drawdown, volatility, correlation
        └── src/build_report.py → docs/report.html  (standalone, filterable)
```

---

## 🚀 Key Features

| Metric | How it is computed |
| :--- | :--- |
| **RSI (14-period)** | Rolling window over the monthly closes |
| **Max Drawdown** | Peak-to-trough decline on the close series |
| **Volatility** | Annualised standard deviation of monthly returns |
| **Peer Correlation** | Pairwise Pearson correlation of monthly returns |
| **Charting** | Line and OHLC views from the committed closes |

Everything above is arithmetic on the CSV. There is **no simulated figure** anywhere in the app: when a metric needs a field the source does not provide (expense ratios, for instance), it is omitted rather than invented.

---

## 📁 Project Structure

```
etf-market-terminal/
├── app.py                  # Streamlit terminal
├── data/etf_monthly.csv    # 185 monthly closes, 5 ETFs
├── src/
│   ├── fetch_data.py       # refresh the CSV from the Yahoo chart endpoint
│   ├── build_report.py     # build docs/report.html from the CSV
│   └── report.py           # shared report generator (CSS + JS + helpers)
├── docs/report.html        # published report (GitHub Pages)
└── requirements.txt
```

---

## 🔧 Setup & Installation

```bash
git clone https://github.com/Nicolenki7/etf-market-terminal.git
cd etf-market-terminal

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py            # the terminal
python src/fetch_data.py        # optional: refresh data/etf_monthly.csv
python src/build_report.py      # optional: rebuild docs/report.html
```

No `.streamlit/secrets.toml` is needed. If the CSV is missing, the app says so and prints the command to regenerate it instead of showing empty charts.

---

## 📈 Usage

1. Pick an ETF in the sidebar.
2. Read its price series, RSI and drawdown.
3. Compare it against its peers with the correlation matrix.

---

## 📝 Data Schema

`data/etf_monthly.csv`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | TEXT | Month, `YYYY-MM` |
| `symbol` | TEXT | ETF ticker (SPY, QQQ, IVV, IEMG, GLD) |
| `close` | FLOAT | Month-end close in USD |

---

## 🚧 Limitations

- **Monthly granularity.** Weekly or intraday signals cannot be built from this file.
- **Closes only.** No volume, no intra-month high/low, so no true candlestick reconstruction.
- **No expense ratios** in the source, so TER-based comparison is absent on purpose.
- Five tickers is a fixed universe, not the ETF market.
- The current month is incomplete until it closes; `fetch_data.py` deduplicates it so the series does not bend.

---

## 📝 Resumen en Español

Terminal de ETFs en Streamlit que lee **cierres mensuales versionados** (`data/etf_monthly.csv`, 185 filas, 5 ETFs, 2023-12 a 2026-11) descargados del endpoint público de Yahoo. Calcula RSI, drawdown, volatilidad anualizada y correlación entre pares con aritmética sobre el CSV: sin base de datos, sin claves y sin métricas simuladas. El informe interactivo se regenera con `src/build_report.py` a partir del mismo archivo.

---

## 📄 License

MIT License — feel free to fork, modify, and use for personal or commercial projects.

---

## 👤 Author

**Nicolás Zalazar** | Data Analyst · Aspiring Data Engineer · Mallorca, Spain

- GitHub: [@Nicolenki7](https://github.com/Nicolenki7)
- LinkedIn: [nicolas-zalazar-63340923a](https://www.linkedin.com/in/nicolas-zalazar-63340923a)
- Portfolio: [nicolenki7.github.io/Portfolio](https://nicolenki7.github.io/Portfolio/)
- Email: zalazarn046@gmail.com
