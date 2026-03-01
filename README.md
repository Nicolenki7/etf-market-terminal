# 🏛️ Alpha Terminal — Institutional ETF Analytics Platform

**Real-Time Market Intelligence | Technical Analysis | Peer Correlation | Risk Metrics**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Overview

Institutional-grade ETF analytics dashboard providing real-time market intelligence with advanced financial metrics, technical indicators, and peer correlation analysis. Built for portfolio managers and analysts who need actionable insights for allocation decisions.

Transforms raw market data into professional-grade analytics including RSI, Sharpe Ratio, Max Drawdown, and benchmark alpha tracking.

---

## 💼 Business Impact

- **Overbought/Oversold Detection**: RSI analysis identifies potential reversal points
- **Risk-Adjusted Returns**: Sharpe Ratio and Drawdown metrics for portfolio optimization
- **Peer Analysis**: Correlation matrices reveal asset relationships and diversification opportunities
- **Benchmark Tracking**: Alpha measurement vs S&P 500 for performance attribution

---

## 🛠️ Technical Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend** | Streamlit (Python) |
| **Visualization** | Plotly Express, Plotly Graph Objects |
| **Data Processing** | Pandas, NumPy |
| **Data Source** | Supabase (REST API) |
| **Authentication** | Streamlit Secrets Management |
| **Deployment** | Streamlit Cloud / Docker |

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

## 🚀 Key Features

### Real-Time Market Metrics
| Metric | Description | Business Value |
| :--- | :--- | :--- |
| **RSI (14-period)** | Relative Strength Index | Identifies overbought (>70) / oversold (<30) conditions |
| **Max Drawdown** | Peak-to-trough decline % | Risk assessment and capital preservation |
| **Sharpe Ratio** | Risk-adjusted return metric | Portfolio optimization and alpha generation |
| **Alpha Tracking** | Performance vs S&P 500 | Benchmark-relative performance measurement |

### Advanced Visualizations
- **Candlestick OHLCV Charts**: Price action with volume overlay
- **Sentiment Analysis Donut**: Bullish vs Bearish asset distribution
- **Risk/Reward Scatter**: TER vs Sharpe Ratio positioning
- **Correlation Matrix**: Peer-to-peer asset correlation heatmap
- **Benchmark Comparison**: Alpha tracking with interactive overlays

### Institutional Alerts
Automatic notifications for:
- RSI > 70 (Overbought — potential reversal)
- RSI < 30 (Oversold — potential buying opportunity)

---

## 📊 Results & Metrics

| Feature | Implementation |
| :--- | :--- |
| **RSI Calculation** | 14-period rolling window |
| **Drawdown Tracking** | Cumulative max with real-time updates |
| **Correlation Analysis** | Pairwise Pearson correlation matrix |
| **UI Theme** | GitHub Dark Dimmed (professional) |

---

## 📁 Project Structure

```
etf-market-terminal/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── secrets.toml.example   # Configuration template
└── README.md                   # Project documentation
```

---

## 🔧 Setup & Installation

```bash
# Clone the repository
git clone https://github.com/Nicolenki7/etf-market-terminal.git
cd etf-market-terminal

# Install dependencies
pip install -r requirements.txt

# Configure Supabase credentials
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Supabase credentials

# Run the application
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

## 📈 Usage

### 1. Select ETF
Choose from available ETF symbols (SPY, QQQ, IWM, etc.)

### 2. View Metrics Dashboard
- **Price Charts**: OHLCV candlestick with volume
- **Technical Indicators**: RSI, moving averages
- **Risk Metrics**: Drawdown, Sharpe Ratio
- **Peer Comparison**: Correlation with other ETFs

### 3. Analyze Alerts
Monitor overbought/oversold conditions for trading opportunities

---

## 🎯 Key Learnings

- **Institutional UI matters**: Dark theme reduces eye strain for professional use
- **Real-time calculations**: RSI and drawdown require efficient rolling window operations
- **Correlation insights**: Peer analysis reveals hidden portfolio risks
- **Alert thresholds**: RSI 70/30 levels provide actionable signals

---

## 📝 Data Schema

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

## 🔮 Future Enhancements

- [ ] Real-time WebSocket data streaming
- [ ] Portfolio backtesting engine
- [ ] Alert system (email/Slack notifications)
- [ ] Multi-timeframe analysis (1D, 1W, 1M, 1Y)
- [ ] Factor analysis (Value, Growth, Momentum, Quality)
- [ ] Export to Excel/PDF reports

---

## 🔗 Links

| Resource | URL |
| :--- | :--- |
| **Repository** | https://github.com/Nicolenki7/etf-market-terminal |
| **Live Demo** | (Deploy on Streamlit Cloud) |

---

## 📝 Resumen en Español

**Alpha Terminal** es una plataforma de análisis institucional de ETFs que proporciona métricas financieras avanzadas en tiempo real. Incluye cálculo de RSI (14 períodos), Drawdown máximo, Ratio Sharpe, y análisis de correlación entre activos. El dashboard está construido con Streamlit y Plotly, con un tema oscuro profesional. Ideal para gestores de portafolio y analistas que necesitan visibilidad inmediata sobre condiciones de sobrecompra/sobreventa, rendimiento ajustado al riesgo, y posicionamiento relativo vs benchmark.

---

## 📄 License

MIT License — Feel free to fork, modify, and use for personal or commercial projects.

---

## 👤 Author

**Nicolás Zalazar** | Senior Data Engineer & Microsoft Fabric Specialist

- GitHub: [@Nicolenki7](https://github.com/Nicolenki7)
- LinkedIn: [nicolas-zalazar-63340923a](https://www.linkedin.com/in/nicolas-zalazar-63340923a)
- Portfolio: [nicolenki7.github.io/Portfolio](https://nicolenki7.github.io/Portfolio/)
- Email: zalazarn046@gmail.com

---

*Last Updated: March 2026*
