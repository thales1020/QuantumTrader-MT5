<div align="center">

# 🚀 QuantumTrader-MT5

**Next-Generation Algorithmic Trading Platform for MetaTrader 5**

*Powered by Machine Learning | ICT/SMC Strategies | Fully Customizable*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![MetaTrader5](https://img.shields.io/badge/MetaTrader-5-orange.svg)](https://www.metatrader5.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-thales1020-blue)](https://github.com/thales1020)
[![Version](https://img.shields.io/badge/Version-2.0.0-success.svg)](https://github.com/thales1020/QuantumTrader-MT5/releases)

</div>

---

QuantumTrader-MT5 is a professional algorithmic trading platform that combines cutting-edge Machine Learning with advanced trading strategies (SuperTrend, ICT, SMC) to deliver institutional-grade automated trading for MetaTrader 5.

> 📜 **ATTRIBUTION**: This project was inspired by open-source MT5-SuperTrend community implementations and has been substantially developed (95%+ original code) by Trần Trọng Hiếu with ML optimization, ICT strategies, dual orders, and advanced architecture. See [ATTRIBUTION.md](docs/ATTRIBUTION.md) for full details.

> ⚠️ **DISCLAIMER**: This project is for **EDUCATIONAL PURPOSES ONLY**. Trading forex/CFDs involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results.

## 🎉 What's New - Dual Orders Strategy

**Latest Update**: All trading bots now support **Dual Orders** feature!

Each trading signal now opens **2 positions** instead of 1:
- 🎯 **Order 1**: Quick profit at **RR 1:1** (Risk:Reward = 1:1)
- 🚀 **Order 2**: Main profit at configured RR ratio (e.g., RR 2:1, RR 3:1)

**Benefits**:
- ✅ Secure quick profits while maintaining exposure to larger moves
- ✅ Better win rate optimization (RR 1:1 has ~60-70% success rate)
- ✅ Reduced psychological pressure ("I should have held longer")

**⚠️ Important**: Total risk per signal is now **2 × risk_percent**. Adjust your configuration accordingly!

See [docs/DUAL_ORDERS_IMPLEMENTATION.md](docs/DUAL_ORDERS_IMPLEMENTATION.md) for full details.

---

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
- **🎯 Dual Orders Strategy**: Each signal opens 2 orders (RR 1:1 + Main RR) for profit optimization
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
- [License](#-license)

## 📚 Documentation

All documentation has been organized in the [`docs/`](docs/) folder:

### Getting Started
- 📖 [Quick Start Guide](docs/QUICKSTART.md) - Get up and running in minutes
- ❓ [FAQ](docs/FAQ.md) - Frequently asked questions
- 🤝 [Contributing](docs/CONTRIBUTING.md) - How to contribute to the project
- 📜 [Attribution & Credits](docs/ATTRIBUTION.md) - **Project history and original author credits**

### Strategy Guides
- 🎯 [ICT Bot](docs/ICT_README.md) - Inner Circle Trader strategy
- ₿ [Crypto Trading Guide](docs/CRYPTO_TRADING_GUIDE.md) - BTC, ETH trading specifics

### Customization & Architecture
- 🔧 [Customization Guide](docs/CUSTOMIZATION_GUIDE.md) - Make the project your own
- 🏗️ [Project Scope](docs/PROJECT_SCOPE.md) - Vision and boundaries

### Features & Implementation
- 🎯 [Dual Orders Implementation](docs/DUAL_ORDERS_IMPLEMENTATION.md) - RR 1:1 + Main RR strategy
- 🔧 [Dual Orders Changes](docs/DUAL_ORDERS_CHANGES.md) - Technical changelog
- 🎯 [Breakeven SL Feature](docs/BREAKEVEN_SL_FEATURE.md) - Automatic risk-free trades

### Performance & Optimization
- 📈 [Performance Guide](docs/PERFORMANCE.md) - Optimization and metrics
- ⚡ [Optimization Summary](docs/OPTIMIZATION_SUMMARY.md) - Performance improvements
- 📝 [Changelog](docs/CHANGELOG.md) - Version history

> 💡 **Tip**: Start with [QUICKSTART.md](docs/QUICKSTART.md) for a quick introduction!

## �🚀 Installation

### Prerequisites

- Python 3.8 or higher
- MetaTrader 5 Terminal
- Windows OS (required for MT5 Python API)
- Active MT5 demo or live account

### Option 1: Quick Install from PyPI (Recommended for Users)

```bash
pip install ml-supertrend-mt5
```

### Option 2: Development Install from GitHub (Recommended for Developers)

**For developers, contributors, and advanced users who want the latest features:**

#### Step 1: Clone the Repository

```bash
git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
cd ML-SuperTrend-MT5
```

#### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux (MT5 API only works on Windows)
python -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Install in Development Mode

```bash
pip install -e .
```

### TA-Lib Installation (Required for both options)

TA-Lib requires special installation:

**Windows:**
1. Download the appropriate .whl file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install: `pip install TA_Lib‑0.4.24‑cp38‑cp38‑win_amd64.whl`

**Alternative (if above doesn't work):**
```bash
conda install -c conda-forge ta-lib
```

### Installation Verification

Test your installation:

```bash
# Command line interface
ml-supertrend --help

# Python import test
python -c "from ml_supertrend_mt5 import SuperTrendBot; print('✅ Installation successful!')"
```

### 🔄 PyPI vs GitHub Installation

| Feature | PyPI Installation | GitHub Installation |
|---------|------------------|-------------------|
| **Target Users** | End users, traders | Developers, contributors |
| **Installation** | `pip install ml-supertrend-mt5` | `git clone` + `pip install -e .` |
| **Updates** | `pip install --upgrade ml-supertrend-mt5` | `git pull` |
| **Stability** | ✅ Stable releases only | ⚠️ Latest development code |
| **Command Line** | ✅ `ml-supertrend` command | ✅ `python run_bot.py` |
| **Import Style** | `from ml_supertrend_mt5 import ...` | `from core.supertrend_bot import ...` |
| **Customization** | ⚠️ Limited | ✅ Full source code access |
| **Contributing** | ❌ Not applicable | ✅ Can submit PRs |
| **Size** | 📦 Smaller download | 📁 Full repository |

**Recommendation:**
- **Use PyPI** if you want to use the bot as-is for trading
- **Use GitHub** if you want to modify, contribute, or need latest features

## ⚡ Quick Start

### Method 1: Command Line Interface (Easiest)

```bash
# Install the package
pip install ml-supertrend-mt5

# Run with default settings
ml-supertrend --symbol EURUSD --account demo

# Run with custom parameters
ml-supertrend --symbol GBPUSD --account live --interval 60 --dry-run
```

### Method 2: Python Script

#### 1. Configure MT5 Connection

Create a `config.json` file with your MT5 credentials:

```json
{
    "accounts": {
        "demo": {
            "login": YOUR_DEMO_LOGIN,
            "password": "YOUR_DEMO_PASSWORD",
            "server": "YOUR_BROKER_SERVER"
        },
        "live": {
            "login": YOUR_LIVE_LOGIN,
            "password": "YOUR_LIVE_PASSWORD",
            "server": "YOUR_BROKER_SERVER"
        }
    },
    "symbols": {
        "EURUSD": {
            "enabled": true,
            "timeframe": "M30",
            "min_factor": 1.0,
            "max_factor": 5.0,
            "factor_step": 0.5,
            "cluster_choice": "Best",
            "volume_multiplier": 1.2,
            "sl_multiplier": 2.0,
            "tp_multiplier": 3.0,
            "risk_percent": 1.0
        }
    },
    "global_settings": {
        "atr_period": 10,
        "performance_alpha": 10.0,
        "volume_ma_period": 20,
        "use_trailing_stop": true,
        "trail_activation_atr": 1.5,
        "max_positions_per_symbol": 1
    }
}
```

#### 2. Run the Bot

```python
from ml_supertrend_mt5 import SuperTrendBot, Config
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

### Method 3: Development Mode (GitHub Installation)

```python
# For developers using GitHub installation
from core.supertrend_bot import SuperTrendBot, Config
from core.performance_monitor import PerformanceMonitor

# Same usage as above
```

### 🖥️ Command Line Options

```bash
ml-supertrend [OPTIONS]

Options:
  --account [demo|live]     Account type to use (default: demo)
  --symbol TEXT            Trading symbol (default: EURUSD)
  --config TEXT            Configuration file path (default: config.json)
  --interval INTEGER       Update interval in seconds (default: 30)
  --dry-run               Run in simulation mode without placing real trades
  --backtest              Run backtest instead of live trading
  --monitor               Show performance monitor after running
  --log-level [DEBUG|INFO|WARNING|ERROR]  Logging level (default: INFO)
  --help                  Show this message and exit

Examples:
  ml-supertrend --symbol GBPUSD --account demo --interval 60
  ml-supertrend --symbol EURUSD --account live --dry-run --log-level DEBUG
  ml-supertrend --backtest --symbol USDJPY --monitor
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

#### Command Line (Multiple terminals)
```bash
# Terminal 1
ml-supertrend --symbol EURUSD --account demo --interval 30

# Terminal 2  
ml-supertrend --symbol GBPUSD --account demo --interval 30

# Terminal 3
ml-supertrend --symbol USDJPY --account demo --interval 30
```

#### Python Script
```python
from ml_supertrend_mt5 import SuperTrendBot, Config
import MetaTrader5 as mt5

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

#### Command Line
```bash
# Conservative approach
ml-supertrend --symbol EURUSD --account demo --dry-run

# Aggressive approach  
ml-supertrend --symbol EURUSD --account demo --interval 15
```

#### Python Script
```python
from ml_supertrend_mt5 import SuperTrendBot, Config

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

#### Command Line
```bash
# Run with performance monitoring
ml-supertrend --symbol EURUSD --account demo --monitor

# View performance after running
ml-supertrend --monitor
```

#### Python Script
```python
from ml_supertrend_mt5 import PerformanceMonitor

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

#### Command Line
```bash
# Run with debug logging
ml-supertrend --symbol EURUSD --account demo --log-level DEBUG

# Dry run mode for testing
ml-supertrend --symbol EURUSD --account demo --dry-run
```

#### Python Script
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
- Open-source MT5-SuperTrend community for inspiration

## �‍💻 Author

**Trần Trọng Hiếu**

- 🌐 Personal GitHub: [@thales1020](https://github.com/thales1020)
- 📂 This Project: [ML-SuperTrend-MT5](https://github.com/xPOURY4/ML-SuperTrend-MT5)
- 🐦 Twitter: [@TheRealPourya](https://twitter.com/TheRealPourya)

## �📞 Contact

For questions, suggestions, or collaboration:

- **GitHub Issues**: [Open an issue](https://github.com/xPOURY4/ML-SuperTrend-MT5/issues)
- **GitHub Profile**: [@thales1020](https://github.com/thales1020)
- **Twitter**: [@TheRealPourya](https://twitter.com/TheRealPourya)

Project Link: [https://github.com/xPOURY4/ML-SuperTrend-MT5](https://github.com/xPOURY4/ML-SuperTrend-MT5)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/thales1020">Trần Trọng Hiếu</a> (thales1020)
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square">
  <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
</p>
