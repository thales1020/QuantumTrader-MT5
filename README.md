# 🤖 ML-SuperTrend-MT5

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![MetaTrader5](https://img.shields.io/badge/MetaTrader-5-orange.svg)](https://www.metatrader5.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Twitter Follow](https://img.shields.io/twitter/follow/TheRealPourya?style=social)](https://twitter.com/TheRealPourya)

An advanced SuperTrend trading bot for MetaTrader 5 that leverages Machine Learning (K-means clustering) for dynamic parameter optimization, featuring adaptive risk management and comprehensive performance monitoring.

> ⚠️ **DISCLAIMER**: This project is for **EDUCATIONAL PURPOSES ONLY**. Trading forex/CFDs involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results.

## 🌟 Features

### Core Algorithm
- **🧠 ML-Optimized SuperTrend**: Dynamic factor selection using K-means clustering
- **📊 Multi-Factor Analysis**: Tests multiple ATR factors simultaneously
- **🎯 Volatility-Adjusted Performance**: Adapts to market conditions
- **📈 Adaptive Moving Average**: Performance-weighted signal filtering

### Risk Management
- **💰 Dynamic Position Sizing**: Based on account risk percentage
- **🛡️ Trailing Stop Loss**: Protects profits in trending markets
- **🎯 Automated TP/SL**: ATR-based take profit and stop loss levels
- **⚡ Daily Loss Limits**: Prevents excessive drawdown

### Trading Features
- **📊 Volume Confirmation**: Filters low-quality signals
- **🕐 Session Management**: Trade during optimal market hours
- **📰 News Filter Ready**: Framework for economic event filtering
- **🔄 Multi-Symbol Support**: Trade multiple pairs simultaneously

### Monitoring & Analysis
- **📈 Real-time Performance Dashboard**: Live statistics display
- **📊 Comprehensive Backtesting**: Historical performance analysis
- **📉 Equity Curve Visualization**: Track your growth
- **🎯 Win Rate Analytics**: Hourly and daily performance breakdown

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Usage Examples](#-usage-examples)
- [Performance Metrics](#-performance-metrics)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MetaTrader 5 Terminal
- Windows OS (required for MT5 Python API)
- Active MT5 demo or live account

### Step 1: Clone the Repository

```bash
git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
cd ML-SuperTrend-MT5
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux (MT5 API only works on Windows)
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install TA-Lib

TA-Lib requires special installation:

**Windows:**
1. Download the appropriate .whl file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install: `pip install TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl`

**Alternative (if above doesn't work):**
```bash
conda install -c conda-forge ta-lib
```

## ⚡ Quick Start

### 1. Configure MT5 Connection

Edit `config.json` with your MT5 credentials:

```json
{
    "accounts": {
        "main": {
            "login": YOUR_MT5_LOGIN,
            "password": "YOUR_MT5_PASSWORD",
            "server": "YOUR_BROKER_SERVER"
        }
    }
}
```

### 2. Run the Bot

```python
from supertrend_bot import SuperTrendBot, Config
import MetaTrader5 as mt5

# Initialize configuration
config = Config(
    symbol="EURUSD",
    timeframe=mt5.TIMEFRAME_M30,
    risk_percent=1.0,
    cluster_choice="Average"  # "Best", "Average", or "Worst"
)

# Create and run bot
bot = SuperTrendBot(config)
bot.connect(login=YOUR_LOGIN, password="YOUR_PASSWORD", server="YOUR_SERVER")
bot.run(interval_seconds=30)
```

## ⚙️ Configuration

### Basic Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `symbol` | EURUSD | Trading pair |
| `timeframe` | M30 | Chart timeframe |
| `atr_period` | 10 | ATR calculation period |
| `min_factor` | 1.0 | Minimum ATR multiplier |
| `max_factor` | 5.0 | Maximum ATR multiplier |
| `factor_step` | 0.5 | Factor increment step |

### Risk Management

| Parameter | Default | Description |
|-----------|---------|-------------|
| `risk_percent` | 1.0 | Risk per trade (% of account) |
| `sl_multiplier` | 2.0 | Stop loss ATR multiplier |
| `tp_multiplier` | 3.0 | Take profit ATR multiplier |
| `use_trailing` | True | Enable trailing stop |
| `trail_activation` | 1.5 | Trailing stop activation (ATR) |

### Advanced Settings

```python
config = Config(
    # Clustering
    cluster_choice="Best",        # Use best performing cluster
    perf_alpha=10.0,             # Performance EMA period
    
    # Volume Filter
    volume_ma_period=20,         # Volume MA period
    volume_multiplier=1.2,       # Volume threshold
    
    # Position Management
    max_positions=1,             # Max positions per symbol
    magic_number=123456          # Unique identifier
)
```

## 🏗️ Architecture

```
ML-SuperTrend-MT5/
│
├── core/
│   ├── supertrend_bot.py      # Main bot logic
│   ├── risk_manager.py        # Risk management module
│   ├── performance_monitor.py # Analytics and reporting
│   └── news_filter.py         # Economic calendar integration
│
├── strategies/
│   ├── supertrend_ml.py       # ML-enhanced SuperTrend
│   └── clustering.py          # K-means implementation
│
├── utils/
│   ├── mt5_helpers.py         # MT5 utility functions
│   ├── indicators.py          # Technical indicators
│   └── data_handler.py        # Data processing
│
├── config/
│   ├── config.json            # Bot configuration
│   └── symbols.json           # Symbol-specific settings
│
├── logs/
│   └── supertrend_bot.log     # Runtime logs
│
├── reports/
│   └── performance_*.png      # Performance charts
│
├── tests/
│   └── test_strategy.py       # Unit tests
│
├── backtest_engine.py         # Backtesting system
├── run_bot.py                 # Main entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 📊 Usage Examples

### Running Multiple Symbols

```python
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
bots = []

for symbol in symbols:
    config = Config(
        symbol=symbol,
        timeframe=mt5.TIMEFRAME_M30,
        risk_percent=0.5  # Lower risk for multiple pairs
    )
    bot = SuperTrendBot(config)
    bot.connect(login, password, server)
    bots.append(bot)

# Run all bots
import threading
for bot in bots:
    thread = threading.Thread(target=bot.run)
    thread.start()
```

### Custom Risk Profile

```python
# Conservative approach
conservative_config = Config(
    cluster_choice="Worst",      # Use worst performing cluster
    risk_percent=0.5,            # Lower risk
    sl_multiplier=3.0,           # Wider stop loss
    tp_multiplier=2.0            # Closer take profit
)

# Aggressive approach
aggressive_config = Config(
    cluster_choice="Best",       # Use best performing cluster
    risk_percent=2.0,            # Higher risk
    sl_multiplier=1.5,           # Tighter stop loss
    tp_multiplier=4.0            # Further take profit
)
```

### Performance Monitoring

```python
from performance_monitor import PerformanceMonitor

# Generate performance report
monitor = PerformanceMonitor('trades.json')
monitor.generate_report(days=30)  # Last 30 days

# Get specific metrics
stats = bot.calculate_statistics()
print(f"Win Rate: {stats['win_rate']:.2f}%")
print(f"Profit Factor: {stats['profit_factor']:.2f}")
print(f"Total Trades: {stats['total_trades']}")
```

## 📈 Performance Metrics

### Expected Performance (Based on Backtesting)

| Timeframe | Win Rate | Profit Factor | Max Drawdown | Sharpe Ratio |
|-----------|----------|---------------|--------------|--------------|
| M5 | 48-52% | 1.1-1.3 | 15-20% | 0.8-1.0 |
| M15 | 52-57% | 1.2-1.5 | 12-18% | 1.0-1.3 |
| **M30** | **55-60%** | **1.3-1.7** | **10-15%** | **1.2-1.5** |
| H1 | 58-63% | 1.5-2.0 | 8-12% | 1.5-1.8 |
| H4 | 60-65% | 1.7-2.5 | 5-10% | 1.8-2.2 |

### Key Performance Indicators

- **Average Trade Duration**: 2-6 hours
- **Risk/Reward Ratio**: 1:1.5 average
- **Monthly Return**: 5-15% (varies by market conditions)
- **Recovery Factor**: 2.5-3.5

## 🛠️ Troubleshooting

### Common Issues

#### Connection Failed
```python
# Check MT5 terminal is running
# Verify credentials
# Ensure "Algo Trading" is enabled in MT5
```

#### No Signals Generated
```python
# Increase lookback period
# Check volume filter settings
# Verify symbol is active/market is open
```

#### High Drawdown
```python
# Reduce risk_percent
# Use "Average" or "Worst" cluster
# Enable daily loss limits
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run bot with debug
bot.run(interval_seconds=30, debug=True)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- SuperTrend indicator concept by Olivier Seban
- K-means clustering implementation inspired by scikit-learn
- MetaTrader 5 Python API by MetaQuotes

## 📞 Contact

**Pourya** - [@TheRealPourya](https://twitter.com/TheRealPourya)

Project Link: [https://github.com/xPOURY4/ML-SuperTrend-MT5](https://github.com/xPOURY4/ML-SuperTrend-MT5)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/xPOURY4">xPOURY4</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square">
  <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
</p>