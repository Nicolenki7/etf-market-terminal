# 🏛️ Alpha Terminal — Institutional ETF Analytics Platform

**Real-time market intelligence dashboard for ETF analysis with advanced financial metrics, technical indicators, and peer correlation analysis.**

---

## 📖 Business Context

Institutional investors and portfolio managers need **real-time visibility** into ETF performance, risk metrics, and market sentiment to make informed allocation decisions. Alpha Terminal provides a unified dashboard that transforms raw market data into actionable intelligence.

### Key Business Questions Answered:
- **Which ETFs are showing overbought/oversold conditions?** (RSI analysis)
- **What is the risk-adjusted return profile?** (Sharpe Ratio, Drawdown)
- **How do assets correlate with each other?** (Peer correlation matrix)
- **Is an ETF outperforming or underperforming its benchmark?** (Alpha tracking)

---

## 🎯 Features

### 📊 Real-Time Market Metrics
| Metric | Description | Business Value |
| :--- | :--- | :--- |
| **RSI (14-period)** | Relative Strength Index calculation | Identifies overbought (>70) / oversold (<30) conditions |
| **Max Drawdown** | Peak-to-trough decline percentage | Risk assessment and capital preservation analysis |
| **Sharpe Ratio** | Risk-adjusted return metric | Portfolio optimization and alpha generation |
| **Alpha Tracking** | Performance vs S&P 500 proxy | Benchmark-relative performance measurement |

### 📈 Advanced Visualizations
- **Candlestick OHLCV Charts** — Price action with volume overlay
- **Sentiment Analysis Donut** — Bullish vs Bearish asset distribution
- **Risk/Reward Scatter** — TER vs Sharpe Ratio positioning
- **Correlation Matrix** — Peer-to-peer asset correlation heatmap
- **Benchmark Comparison** — Alpha tracking with interactive overlays

### 🚨 Institutional Alerts
Automatic notifications for:
- RSI > 70 (Overbought — potential reversal)
- RSI < 30 (Oversold — potential buying opportunity)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Alpha Terminal                          │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Streamlit (Interactive Dashboard)                │
│  Visualization: Plotly (Dark Theme, Institutional UI)       │
├─────────────────────────────────────────────────────────────┤
│  Data Engine: Python + Pandas                               │
│  - RSI Calculation (14-period rolling window)               │
│  - Drawdown Analysis (cumulative max tracking)              │
│  - Sharpe Ratio Simulation                                  │
├─────────────────────────────────────────────────────────────┤
│  Data Source: Supabase (Real-time REST API)                 │
│  - raw_etf_market_data table                                │
│  - Fields: price, day_high, day_low, day_open, prev_close   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit (Python) |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Data Processing** | Pandas, NumPy |
| **Data Source** | Supabase (REST API) |
| **Authentication** | Streamlit Secrets Management |
| **Deployment** | Streamlit Cloud / Docker (planned) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account with `raw_etf_market_data` table
- Streamlit installed

### Installation

```bash
# Clone repository
git clone https://github.com/Nicolenki7/etf-market-terminal.git
cd etf-market-terminal

# Install dependencies
pip install -r requirements.txt

# Configure secrets (create .streamlit/secrets.toml)
# [supabase]
# supabase_url = "your_supabase_url"
# supabase_key = "your_supabase_key"

# Run application
streamlit run app.py
```

### Configuration

Create `.streamlit/secrets.toml`:
```toml
[supabase]
supabase_url = "https://your-project.supabase.co"
supabase_key = "your-anon-or-service-role-key"
```

---

## 📊 Data Schema

### `raw_etf_market_data` Table

| Column | Type | Description |
| :--- | :--- | :--- |
| `symbol` | TEXT | ETF ticker symbol (e.g., SPY, QQQ) |
| `price` | FLOAT | Current market price |
| `day_high` | FLOAT | Daily high |
| `day_low` | FLOAT | Daily low |
| `day_open` | FLOAT | Daily open price |
| `prev_close` | FLOAT | Previous close |
| `change_pct` | FLOAT | Percentage change |
| `ingested_at` | TIMESTAMP | Data ingestion timestamp |

---

## 📈 Calculated Metrics

### RSI (Relative Strength Index)
```python
def calc_rsi(series, periods=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
```

### Max Drawdown
```python
df['rolling_max'] = df.groupby('symbol')['price'].transform(lambda x: x.cummax())
df['drawdown'] = ((df['price'] - df['rolling_max']) / df['rolling_max']) * 100
```

---

## 🎨 UI Theme

Institutional-grade dark theme optimized for professional environments:
- **Background:** `#0d1117` (GitHub Dark Dimmed)
- **Cards:** `#161b22` with `#30363d` borders
- **Accents:** `#58a6ff` (GitHub Blue)
- **Bullish:** `#3fb950` (Green)
- **Bearish:** `#f85149` (Red)

---

## 🔮 Future Enhancements

- [ ] Real-time WebSocket data streaming
- [ ] Portfolio backtesting engine
- [ ] Alert system (email/Slack notifications)
- [ ] Multi-timeframe analysis (1D, 1W, 1M, 1Y)
- [ ] Factor analysis (Value, Growth, Momentum, Quality)
- [ ] Export to Excel/PDF reports

---

## 📝 Spanish Summary (Resumen en Español)

**Alpha Terminal** es una plataforma de análisis institucional de ETFs que proporciona métricas financieras avanzadas en tiempo real. Incluye cálculo de RSI (14 períodos), Drawdown máximo, Ratio Sharpe, y análisis de correlación entre activos. El dashboard está construido con Streamlit y Plotly, con un tema oscuro profesional. Los datos se obtienen de Supabase mediante API REST. Ideal para gestores de portafolio y analistas que necesitan visibilidad inmediata sobre condiciones de sobrecompra/sobreventa, rendimiento ajustado al riesgo, y posicionamiento relativo vs benchmark.

---

## 📫 Author

**Nicolas Zalazar** | Data Engineer & Microsoft Fabric Specialist  
📧 zalazarn046@gmail.com | 🔗 [LinkedIn](https://www.linkedin.com/in/nicolas-zalazar-63340923a)

---

## 📄 License

MIT License — Feel free to fork, modify, and use for personal or commercial projects.

---

*Last Updated: February 2026*
