# Complete Trading Bot Workflow

**From Idea to Production in 7 Steps**

This comprehensive tutorial demonstrates the complete workflow of creating, testing, and deploying a trading bot using QuantumTrader-MT5.

**Scenario:** Create an EMA crossover strategy with RSI filter, add risk management, track performance, and deploy to production.

---

## 📋 Table of Contents

1. [Generate Strategy from Template](#step-1-generate-strategy-from-template)
2. [Customize Strategy Logic](#step-2-customize-strategy-logic)
3. [Add Plugin for Risk Management](#step-3-add-plugin-for-risk-management)
4. [Add Analytics Plugin](#step-4-add-analytics-plugin)
5. [Backtest Strategy](#step-5-backtest-strategy)
6. [Optimize Parameters](#step-6-optimize-parameters)
7. [Deploy to Production](#step-7-deploy-to-production)

---

## Step 1: Generate Strategy from Template

**Goal:** Create initial strategy using the strategy template generator.

### 1.1 List Available Templates

```bash
python scripts/create_strategy.py --list
```

**Output:**
```
📋 Available Templates:

  1. ma_crossover (⭐ Beginner)
     Moving average crossover strategy
     
  2. rsi_mean_reversion (⭐ Beginner)
     RSI-based mean reversion
     
  # ... more templates
```

### 1.2 Generate Strategy

We'll use the MA Crossover template:

```bash
python scripts/create_strategy.py \
  --template ma_crossover \
  --name "EMA RSI Strategy" \
  --id ema_rsi_strategy \
  --param MA_TYPE=EMA \
  --param FAST_PERIOD=20 \
  --param SLOW_PERIOD=50 \
  --param TP_MULTIPLIER=2.0 \
  --param SL_MULTIPLIER=1.0 \
  --generate-config
```

**Output:**
```
✅ Strategy created: strategies/ema_rsi_strategy.py
✅ Config created: config/ema_rsi_strategy.json
```

### 1.3 Review Generated Files

**strategies/ema_rsi_strategy.py** - Complete strategy class
**config/ema_rsi_strategy.json** - Configuration file

✅ **Checkpoint:** Strategy skeleton created

---

## Step 2: Customize Strategy Logic

**Goal:** Add RSI filter to improve entry quality.

### 2.1 Open Generated Strategy

File: `strategies/ema_rsi_strategy.py`

### 2.2 Add RSI to Indicators

Find the `calculate_indicators()` method and add RSI:

```python
def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate EMA and RSI indicators"""
    # Existing EMAs
    df['ema_fast'] = talib.EMA(df['close'], timeperiod=self.fast_period)
    df['ema_slow'] = talib.EMA(df['close'], timeperiod=self.slow_period)
    
    # Add RSI filter
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    
    # ATR for stop loss/take profit
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    
    return df
```

### 2.3 Modify Signal Generation

Update `generate_signal()` to include RSI filter:

```python
def generate_signal(self, df: pd.DataFrame) -> int:
    """Generate signal with EMA crossover + RSI filter"""
    if len(df) < 2:
        return 0
    
    # EMA values
    ema_fast_current = df['ema_fast'].iloc[-1]
    ema_slow_current = df['ema_slow'].iloc[-1]
    ema_fast_prev = df['ema_fast'].iloc[-2]
    ema_slow_prev = df['ema_slow'].iloc[-2]
    
    # RSI value
    rsi_current = df['rsi'].iloc[-1]
    
    # BUY: EMA crossover UP + RSI not overbought
    if (ema_fast_prev <= ema_slow_prev and 
        ema_fast_current > ema_slow_current and
        rsi_current < 70):  # RSI filter
        
        self.logger.info(f"BUY signal: EMA crossover + RSI {rsi_current:.2f}")
        return 1
    
    # SELL: EMA crossover DOWN + RSI not oversold
    if (ema_fast_prev >= ema_slow_prev and 
        ema_fast_current < ema_slow_current and
        rsi_current > 30):  # RSI filter
        
        self.logger.info(f"SELL signal: EMA crossover + RSI {rsi_current:.2f}")
        return -1
    
    return 0
```

### 2.4 Update Config

File: `config/ema_rsi_strategy.json`

Add RSI parameters:

```json
{
  "strategy_id": "ema_rsi_strategy",
  "enabled": true,
  "symbol": "EURUSD",
  "timeframe": "H1",
  "risk_percent": 1.0,
  
  "fast_period": 20,
  "slow_period": 50,
  "ma_type": "EMA",
  "rsi_period": 14,
  "rsi_overbought": 70,
  "rsi_oversold": 30,
  
  "tp_multiplier": 2.0,
  "sl_multiplier": 1.0
}
```

✅ **Checkpoint:** Strategy logic customized with RSI filter

---

## Step 3: Add Plugin for Risk Management

**Goal:** Integrate advanced risk management plugin.

### 3.1 Import Risk Manager Plugin

In `strategies/ema_rsi_strategy.py`, add at the top:

```python
from examples.plugins.advanced_risk_manager import AdvancedRiskManager
```

### 3.2 Initialize Plugin in __init__

```python
def __init__(self, config: Dict):
    super().__init__(config)
    
    # ... existing initialization ...
    
    # Add risk manager plugin
    risk_config = {
        'max_daily_loss_percent': 2.0,
        'max_drawdown_percent': 10.0,
        'volatility_multiplier': 1.5,
        'avoid_news_hours': True,
        'scale_on_streak': True,
    }
    
    self.risk_manager = AdvancedRiskManager(risk_config)
    self.add_plugin(self.risk_manager)
    
    self.logger.info("Risk manager plugin added")
```

### 3.3 Test Risk Manager

```python
# Test file: test_risk_integration.py
from strategies.ema_rsi_strategy import EmaRsiStrategy

config = {
    'symbol': 'EURUSD',
    'timeframe': 'H1',
    'risk_percent': 1.0,
}

bot = EmaRsiStrategy(config)
print(f"Plugins loaded: {len(bot.plugins)}")
print(f"Risk manager active: {'AdvancedRiskManager' in [p.get_name() for p in bot.plugins]}")
```

✅ **Checkpoint:** Risk management integrated

---

## Step 4: Add Analytics Plugin

**Goal:** Track performance with analytics plugin.

### 4.1 Import Analytics Plugin

```python
from examples.plugins.trade_analytics import TradeAnalytics
```

### 4.2 Initialize Analytics

```python
def __init__(self, config: Dict):
    super().__init__(config)
    
    # ... existing code ...
    
    # Add analytics plugin
    analytics_config = {
        'track_time_performance': True,
        'track_symbol_performance': True,
        'export_daily_report': True,
        'report_path': './reports/',
    }
    
    self.analytics = TradeAnalytics(analytics_config)
    self.add_plugin(self.analytics)
    
    self.logger.info("Analytics plugin added")
```

### 4.3 Add Report Generation Method

```python
def get_performance_report(self) -> Dict:
    """Get performance report from analytics plugin"""
    if self.analytics:
        return self.analytics.generate_summary_report()
    return {}
```

✅ **Checkpoint:** Analytics tracking enabled

---

## Step 5: Backtest Strategy

**Goal:** Validate strategy with historical data.

### 5.1 Create Backtest Script

File: `scripts/backtest_ema_rsi.py`

```python
"""
Backtest EMA RSI Strategy

Run historical backtest to validate strategy performance.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.ema_rsi_strategy import EmaRsiStrategy
from datetime import datetime

# Configuration
config = {
    'symbol': 'EURUSD',
    'timeframe': 'H1',
    'risk_percent': 1.0,
    'fast_period': 20,
    'slow_period': 50,
    'ma_type': 'EMA',
}

# Initialize strategy
bot = EmaRsiStrategy(config)

# Run backtest
print("\n" + "=" * 60)
print("BACKTESTING EMA RSI STRATEGY")
print("=" * 60)
print(f"Symbol: {config['symbol']}")
print(f"Timeframe: {config['timeframe']}")
print(f"Period: 2024-01-01 to 2024-12-31")
print("=" * 60 + "\n")

# Backtest
results = bot.backtest(
    start_date='2024-01-01',
    end_date='2024-12-31',
    initial_balance=10000
)

# Display results
print("\nBacktest Results:")
print("-" * 60)
print(f"Total Trades: {results.get('total_trades', 0)}")
print(f"Win Rate: {results.get('win_rate', 0):.2f}%")
print(f"Profit Factor: {results.get('profit_factor', 0):.2f}")
print(f"Total Profit: ${results.get('total_profit', 0):.2f}")
print(f"Max Drawdown: {results.get('max_drawdown', 0):.2f}%")
print("=" * 60 + "\n")

# Get performance report from analytics
if bot.analytics:
    report = bot.get_performance_report()
    
    print("\nDetailed Analytics:")
    print("-" * 60)
    print(f"Average Win: ${report['metrics']['average_win']:.2f}")
    print(f"Average Loss: ${report['metrics']['average_loss']:.2f}")
    print(f"Expectancy: ${report['metrics']['expectancy']:.2f}")
    print("\nBest Trading Hours:")
    for hour_data in report.get('best_hours', []):
        print(f"  Hour {hour_data['hour']:02d}:00 - "
              f"{hour_data['trades']} trades, "
              f"${hour_data['profit']:.2f} profit")
    print("=" * 60 + "\n")
```

### 5.2 Run Backtest

```bash
python scripts/backtest_ema_rsi.py
```

### 5.3 Analyze Results

Review:
- Win rate (target: > 50%)
- Profit factor (target: > 1.5)
- Max drawdown (target: < 15%)
- Best trading hours
- Risk-adjusted returns

✅ **Checkpoint:** Strategy validated with backtest

---

## Step 6: Optimize Parameters

**Goal:** Find optimal EMA periods and risk parameters.

### 6.1 Create Optimization Script

File: `scripts/optimize_ema_rsi.py`

```python
"""
Parameter Optimization for EMA RSI Strategy

Test different combinations of EMA periods to find optimal settings.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from strategies.ema_rsi_strategy import EmaRsiStrategy
import pandas as pd

# Parameter ranges to test
fast_periods = [10, 15, 20, 25, 30]
slow_periods = [40, 50, 60, 70, 80]

# Store results
results = []

print("\n" + "=" * 60)
print("OPTIMIZING EMA RSI STRATEGY")
print("=" * 60)

total_tests = len(fast_periods) * len(slow_periods)
current_test = 0

for fast in fast_periods:
    for slow in slow_periods:
        if fast >= slow:
            continue
        
        current_test += 1
        print(f"\nTest {current_test}/{total_tests}: EMA {fast}/{slow}")
        
        config = {
            'symbol': 'EURUSD',
            'timeframe': 'H1',
            'fast_period': fast,
            'slow_period': slow,
            'risk_percent': 1.0,
        }
        
        bot = EmaRsiStrategy(config)
        
        # Run backtest
        backtest_results = bot.backtest(
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_balance=10000
        )
        
        # Store results
        results.append({
            'fast_period': fast,
            'slow_period': slow,
            'total_trades': backtest_results.get('total_trades', 0),
            'win_rate': backtest_results.get('win_rate', 0),
            'profit_factor': backtest_results.get('profit_factor', 0),
            'total_profit': backtest_results.get('total_profit', 0),
            'max_drawdown': backtest_results.get('max_drawdown', 0),
        })

# Convert to DataFrame and sort by profit factor
df_results = pd.DataFrame(results)
df_results = df_results.sort_values('profit_factor', ascending=False)

# Display top 5 results
print("\n" + "=" * 60)
print("TOP 5 PARAMETER COMBINATIONS")
print("=" * 60)

for idx, row in df_results.head(5).iterrows():
    print(f"\n#{idx + 1}")
    print(f"  EMA Periods: {row['fast_period']}/{row['slow_period']}")
    print(f"  Trades: {row['total_trades']}")
    print(f"  Win Rate: {row['win_rate']:.2f}%")
    print(f"  Profit Factor: {row['profit_factor']:.2f}")
    print(f"  Total Profit: ${row['total_profit']:.2f}")
    print(f"  Max Drawdown: {row['max_drawdown']:.2f}%")

# Save results to CSV
df_results.to_csv('optimization_results.csv', index=False)
print("\n✅ Results saved to optimization_results.csv")
print("=" * 60 + "\n")
```

### 6.2 Run Optimization

```bash
python scripts/optimize_ema_rsi.py
```

### 6.3 Update Config with Best Parameters

Update `config/ema_rsi_strategy.json` with optimal values found.

✅ **Checkpoint:** Parameters optimized for best performance

---

## Step 7: Deploy to Production

**Goal:** Deploy strategy to live trading or VPS.

### 7.1 Create Production Config

File: `config/ema_rsi_strategy_prod.json`

```json
{
  "strategy_id": "ema_rsi_strategy",
  "enabled": true,
  "symbol": "EURUSD",
  "timeframe": "H1",
  "environment": "production",
  
  "risk_percent": 0.5,
  "fast_period": 20,
  "slow_period": 50,
  
  "max_daily_loss_percent": 1.5,
  "max_positions": 1,
  
  "telegram_notifications": true,
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  
  "magic_number": 100100
}
```

### 7.2 Create Production Runner

File: `run_ema_rsi_prod.py`

```python
"""
Production Runner for EMA RSI Strategy

Run strategy in live trading mode with full risk management.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from strategies.ema_rsi_strategy import EmaRsiStrategy
from examples.plugins.telegram_notifier import TelegramNotifier
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ema_rsi_prod.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load production config
with open('config/ema_rsi_strategy_prod.json', 'r') as f:
    config = json.load(f)

# Initialize strategy
logger.info("Initializing EMA RSI Strategy for production")
bot = EmaRsiStrategy(config)

# Add Telegram notifications if configured
if config.get('telegram_notifications'):
    telegram_config = {
        'bot_token': config.get('telegram_bot_token'),
        'chat_id': config.get('telegram_chat_id'),
        'notify_trades': True,
        'notify_daily': True,
        'notify_risk_warnings': True,
    }
    
    notifier = TelegramNotifier(telegram_config)
    bot.add_plugin(notifier)
    logger.info("Telegram notifications enabled")

# Safety checks
logger.info("Running pre-flight safety checks...")
logger.info(f"  Environment: {config.get('environment')}")
logger.info(f"  Risk per trade: {config.get('risk_percent')}%")
logger.info(f"  Max daily loss: {config.get('max_daily_loss_percent')}%")
logger.info(f"  Plugins active: {len(bot.plugins)}")

# Confirm before starting
print("\n" + "=" * 60)
print("PRODUCTION TRADING MODE")
print("=" * 60)
print(f"Strategy: {bot.get_strategy_info()['name']}")
print(f"Symbol: {config['symbol']}")
print(f"Risk: {config['risk_percent']}% per trade")
print(f"Plugins: {', '.join(p.get_name() for p in bot.plugins)}")
print("=" * 60)

confirmation = input("\nStart live trading? (yes/no): ")

if confirmation.lower() == 'yes':
    logger.info("Starting live trading...")
    print("\n✅ Bot started. Press Ctrl+C to stop.\n")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
        print("\n\n✅ Bot stopped safely.")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"\n❌ Error: {e}")
else:
    logger.info("Production start cancelled by user")
    print("\n❌ Cancelled")
```

### 7.3 Deploy to VPS (Optional)

See [VPS_DEPLOYMENT_GUIDE.md](../../docs/VPS_DEPLOYMENT_GUIDE.md) for:
- VPS setup
- MT5 installation
- Bot deployment
- Monitoring setup

### 7.4 Start Production

```bash
python run_ema_rsi_prod.py
```

✅ **Checkpoint:** Strategy deployed to production

---

## 🎉 Workflow Complete!

You've successfully:

✅ Generated strategy from template  
✅ Customized with RSI filter  
✅ Added risk management plugin  
✅ Added analytics plugin  
✅ Backtested strategy  
✅ Optimized parameters  
✅ Deployed to production  

---

## 📊 Summary

**Time Investment:**
- Template generation: 1 minute
- Customization: 15 minutes
- Plugin integration: 10 minutes
- Backtesting: 30 minutes
- Optimization: 1 hour
- Deployment: 20 minutes

**Total:** ~2.5 hours (vs. 2-3 days from scratch!)

**What You Built:**
- Complete trading strategy (300+ lines)
- Risk management system
- Performance analytics
- Production-ready deployment

---

## 🚀 Next Steps

1. **Monitor Performance** - Use analytics plugin reports
2. **Iterate** - Adjust parameters based on live results
3. **Scale** - Add more symbols or timeframes
4. **Enhance** - Add more sophisticated filters
5. **Diversify** - Create portfolio of strategies

---

## 📚 Related Resources

- [Strategy Templates](../../docs/STRATEGY_TEMPLATES.md)
- [Plugin System](../../docs/PLUGIN_QUICK_START.md)
- [Backtesting Guide](../../docs/BACKTEST_VALIDATION_RESULTS.md)
- [VPS Deployment](../../docs/VPS_DEPLOYMENT_GUIDE.md)

---

**Created**: November 4, 2025  
**Author**: QuantumTrader-MT5 Team  
**Version**: 1.0.0
