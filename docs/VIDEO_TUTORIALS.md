# Video Tutorial Guide

Complete video tutorial outlines for QuantumTrader-MT5 customization features.

---

## 📹 Tutorial Series Overview

This guide provides detailed outlines for creating video tutorials covering all aspects of the QuantumTrader-MT5 customization framework. Each tutorial is designed to be practical, hands-on, and beginner-friendly.

**Target Audience:** Python traders with basic programming knowledge  
**Prerequisites:** QuantumTrader-MT5 installed, MT5 terminal set up  
**Total Series Duration:** ~60 minutes

---

## 🎬 Tutorial 1: Create Your First Strategy in 5 Minutes

**Duration:** 5 minutes  
**Difficulty:** ⭐ Beginner  
**Goal:** Generate and run a working strategy using the template system

### Script Outline

**00:00-00:30 - Introduction**
- Welcome to QuantumTrader-MT5
- What we'll build: Simple EMA crossover strategy
- Why templates matter: 96% time savings

**00:30-01:30 - Template Overview**
- Quick tour of 5 available templates
- When to use each template type
- Our choice: Trend Following template

**01:30-03:00 - Generation Process**
```bash
# Demo command
python scripts/generate_strategy.py
```
- Interactive prompts walkthrough
- Choosing template (Trend Following)
- Setting strategy name (EMA Crossover)
- Selecting indicators (EMA)
- Configuring parameters

**03:00-04:00 - Generated Code Review**
- Open generated file: `strategies/ema_crossover.py`
- Highlight key sections:
  - Config class with all parameters
  - `calculate_indicators()` method
  - `generate_signal()` logic
  - Built-in risk management

**04:00-04:45 - First Run**
```bash
# Run the strategy
python strategies/ema_crossover.py
```
- Show connection to MT5
- Display live signal generation
- Explain output logs

**04:45-05:00 - Next Steps**
- Customization preview
- Link to Tutorial 2
- Challenge: Generate your own strategy

### Key Takeaways
1. Template generation takes < 1 minute
2. Generated code is production-ready
3. No need to write boilerplate code
4. Focus on strategy logic, not infrastructure

### Demo Assets Needed
- Screen recording software
- MT5 terminal with demo account
- Terminal with project open
- Example EURUSD chart

---

## 🎬 Tutorial 2: Plugin System Deep Dive

**Duration:** 10 minutes  
**Difficulty:** ⭐⭐ Intermediate  
**Goal:** Understand hooks and create a custom plugin

### Script Outline

**00:00-01:00 - Introduction**
- What are plugins?
- Why use plugins vs. modifying core code?
- Real-world use cases

**01:00-03:00 - Plugin Architecture**
- The 7 event hooks explained:
  1. `before_trade` - Pre-execution validation
  2. `after_trade` - Post-execution logging
  3. `on_position_close` - Trade completion handling
  4. `daily_start` - Daily initialization
  5. `daily_end` - Daily reporting
  6. `on_error` - Error handling
  7. `on_shutdown` - Cleanup
- Hook execution flow diagram
- Context parameters available

**03:00-05:00 - Example 1: Risk Manager Plugin**
```python
# Show examples/plugins/advanced_risk_manager.py
```
- Code walkthrough:
  - Daily loss limit checking
  - Volatility-based position sizing
  - Streak adjustments
- How `before_trade` hook prevents bad trades

**05:00-07:00 - Example 2: Trade Analytics Plugin**
```python
# Show examples/plugins/trade_analytics.py
```
- Code walkthrough:
  - Recording trade data
  - Calculating metrics (win rate, profit factor)
  - Generating reports
- How `on_position_close` captures results

**07:00-08:30 - Creating Custom Plugin**
```python
# Live coding: Simple logger plugin
from core.plugin_system import BasePlugin

class SimpleLogger(BasePlugin):
    def get_name(self) -> str:
        return "SimpleLogger"
    
    def after_trade(self, context):
        print(f"Trade opened: {context['symbol']} {context['position_type']}")
    
    def on_position_close(self, context):
        profit = context.get('profit', 0)
        emoji = "✅" if profit > 0 else "❌"
        print(f"{emoji} Trade closed: ${profit:.2f}")
```

**08:30-09:30 - Integration**
```python
# Add plugin to strategy
from examples.plugins.simple_logger import SimpleLogger

bot = MyStrategy(config)
bot.add_plugin(SimpleLogger())
bot.run()
```
- Show plugin in action
- Demonstrate hot-reload capability

**09:30-10:00 - Best Practices & Tips**
- Keep plugins focused (single responsibility)
- Use context parameters efficiently
- Handle errors gracefully
- Test plugins independently
- Link to plugin examples

### Key Takeaways
1. Plugins extend functionality without modifying core
2. 7 hooks cover complete trade lifecycle
3. Easy to create custom plugins
4. Combine multiple plugins for powerful systems

### Demo Assets Needed
- Plugin architecture diagram
- Example plugin code files
- Working strategy with plugins
- Terminal for live coding

---

## 🎬 Tutorial 3: Custom Indicators & Multi-Timeframe Analysis

**Duration:** 15 minutes  
**Difficulty:** ⭐⭐⭐ Advanced  
**Goal:** Build indicators not in TA-Lib and use multiple timeframes

### Script Outline

**00:00-01:00 - Introduction**
- Why custom indicators?
- When TA-Lib isn't enough
- Our example: Ichimoku + Multi-timeframe

**01:00-04:00 - Part 1: Custom Ichimoku Implementation**
```python
# Show examples/strategies/custom_indicators.py
def calculate_ichimoku(self, df):
    # Tenkan-sen (Conversion Line)
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2
    
    # Kijun-sen (Base Line)
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2
    
    # More components...
    return df
```
- Mathematical explanation
- Pandas rolling calculations
- Why this approach works

**04:00-07:00 - Part 2: Multi-Timeframe Strategy**
```python
# Show examples/strategies/multi_timeframe.py
class MultiTimeframeStrategy(BaseStrategy):
    def fetch_higher_timeframe_data(self):
        # Get H1 data for trend
        df_h1 = self.get_data(timeframe=mt5.TIMEFRAME_H1)
        return df_h1
    
    def get_current_trend(self):
        df_h1 = self.fetch_higher_timeframe_data()
        ema_200 = df_h1['close'].rolling(200).mean()
        current_price = df_h1['close'].iloc[-1]
        
        if current_price > ema_200.iloc[-1]:
            return "UPTREND"
        else:
            return "DOWNTREND"
```
- Higher timeframe for trend (H1)
- Lower timeframe for entries (M15)
- Data caching to reduce API calls

**07:00-10:00 - Part 3: Combining Everything**
```python
def generate_signal(self):
    # Get trend from H1
    trend = self.get_current_trend()
    
    # Get Ichimoku from current timeframe
    df = self.calculate_ichimoku(self.df)
    
    # Buy signal: Uptrend + Tenkan above Kijun + Price above cloud
    if (trend == "UPTREND" and 
        df['tenkan_sen'].iloc[-1] > df['kijun_sen'].iloc[-1] and
        df['close'].iloc[-1] > df['senkou_span_a'].iloc[-1]):
        return "BUY"
    
    # Sell signal logic...
    return None
```

**10:00-12:00 - Testing & Visualization**
- Run backtest with custom indicator
- Plot Ichimoku cloud with matplotlib
- Analyze results on different timeframes

**12:00-14:00 - More Custom Indicators**

**Pivot Points:**
```python
def calculate_pivot_points(self, df):
    pivot = (df['high'] + df['low'] + df['close']) / 3
    r1 = 2 * pivot - df['low']
    s1 = 2 * pivot - df['high']
    return pivot, r1, s1
```

**VWAP (Volume Weighted Average Price):**
```python
def calculate_vwap(self, df):
    df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    return df
```

**14:00-15:00 - Best Practices & Performance**
- Cache calculations to avoid recomputation
- Use vectorized Pandas operations
- Profile code for bottlenecks
- Balance complexity vs. performance

### Key Takeaways
1. Can implement any indicator with Pandas
2. Multi-timeframe analysis improves accuracy
3. Combine indicators for confluence
4. Always backtest custom indicators

### Demo Assets Needed
- Ichimoku chart example
- Multi-timeframe MT5 charts
- Backtest results with custom indicators
- Performance profiling tools

---

## 🎬 Tutorial 4: Backtesting & Optimization Workflow

**Duration:** 10 minutes  
**Difficulty:** ⭐⭐ Intermediate  
**Goal:** Validate strategies with historical data and optimize parameters

### Script Outline

**00:00-01:00 - Introduction**
- Why backtest?
- Common pitfalls (overfitting, look-ahead bias)
- Our approach: Robust testing

**01:00-03:00 - Setting Up Backtest**
```python
# Show backtest script
from engines.backtest_engine import BacktestEngine

config = {
    'symbol': 'EURUSD',
    'timeframe': mt5.TIMEFRAME_M30,
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2024, 10, 1),
    'initial_balance': 10000
}

engine = BacktestEngine(config)
results = engine.run(strategy)
```

**03:00-05:00 - Analyzing Results**
```python
# Show results analysis
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

# Plot equity curve
engine.plot_equity_curve()
```
- Interpreting metrics
- What makes a good strategy?
- Red flags to watch for

**05:00-07:00 - Parameter Optimization**
```python
# Grid search example
from itertools import product

ema_fast_range = range(10, 30, 5)
ema_slow_range = range(50, 150, 25)
rr_range = [1.5, 2.0, 2.5, 3.0]

best_result = None
best_sharpe = -999

for fast, slow, rr in product(ema_fast_range, ema_slow_range, rr_range):
    config.update({
        'ema_fast': fast,
        'ema_slow': slow,
        'rr_ratio': rr
    })
    
    results = engine.run(strategy)
    
    if results['sharpe_ratio'] > best_sharpe:
        best_sharpe = results['sharpe_ratio']
        best_result = (fast, slow, rr)

print(f"Best parameters: Fast={best_result[0]}, Slow={best_result[1]}, RR={best_result[2]}")
```

**07:00-08:30 - Walk-Forward Analysis**
```python
# Prevent overfitting
periods = [
    ('2024-01-01', '2024-03-31', '2024-04-01', '2024-04-30'),  # Train, Test
    ('2024-04-01', '2024-06-30', '2024-07-01', '2024-07-31'),
    ('2024-07-01', '2024-09-30', '2024-10-01', '2024-10-31'),
]

for train_start, train_end, test_start, test_end in periods:
    # Optimize on training period
    # Test on out-of-sample period
    # Compare results
```

**08:30-09:30 - Monte Carlo Simulation**
```python
# Assess robustness
import numpy as np

def monte_carlo_simulation(trades, num_simulations=1000):
    results = []
    
    for _ in range(num_simulations):
        # Shuffle trade order
        shuffled = np.random.permutation(trades)
        equity_curve = calculate_equity_curve(shuffled)
        max_dd = calculate_max_drawdown(equity_curve)
        results.append(max_dd)
    
    # 95% confidence interval
    percentile_5 = np.percentile(results, 5)
    percentile_95 = np.percentile(results, 95)
    
    print(f"95% CI for max drawdown: {percentile_5:.2f}% to {percentile_95:.2f}%")
```

**09:30-10:00 - Best Practices**
- Use long enough test periods (1+ years)
- Test on multiple market conditions
- Keep some data for final validation
- Document all assumptions
- Be realistic about slippage/commissions

### Key Takeaways
1. Backtest before risking real money
2. Optimize systematically, not randomly
3. Validate with walk-forward analysis
4. Use Monte Carlo for robustness check

### Demo Assets Needed
- Backtest results spreadsheet
- Equity curve charts
- Optimization heatmaps
- Walk-forward results comparison

---

## 🎬 Tutorial 5: Complete Workflow - Idea to Production

**Duration:** 20 minutes  
**Difficulty:** ⭐⭐⭐ Advanced  
**Goal:** Build complete trading system from scratch

### Script Outline

**Based on:** `examples/integration/COMPLETE_WORKFLOW.md`

**00:00-01:00 - Introduction**
- Our goal: EMA + RSI strategy in production
- The 7-step workflow
- Time estimate: 2.5 hours total

**01:00-03:00 - Step 1: Generate Template (1 min)**
```bash
python scripts/generate_strategy.py

# Interactive:
# Template: Trend Following
# Name: EMA RSI Strategy
# Indicators: EMA, RSI
```
- Show generated code
- Verify it compiles and runs

**03:00-06:00 - Step 2: Customize Logic (15 min)**
```python
# Edit strategies/ema_rsi_strategy.py

def calculate_indicators(self):
    # Original EMA logic
    self.df['ema_fast'] = self.df['close'].ewm(span=12).mean()
    self.df['ema_slow'] = self.df['close'].ewm(span=26).mean()
    
    # ADD: RSI filter
    delta = self.df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    self.df['rsi'] = 100 - (100 / (1 + rs))

def generate_signal(self):
    # Original EMA crossover
    ema_cross = (self.df['ema_fast'].iloc[-1] > self.df['ema_slow'].iloc[-1])
    
    # ADD: RSI filter (only buy when oversold, sell when overbought)
    rsi = self.df['rsi'].iloc[-1]
    
    if ema_cross and rsi < 30:
        return "BUY"
    elif not ema_cross and rsi > 70:
        return "SELL"
    
    return None
```
- Show before/after code
- Explain the improvement

**06:00-09:00 - Step 3: Add Risk Management Plugin (10 min)**
```python
# Add to ema_rsi_strategy.py
from examples.plugins.advanced_risk_manager import AdvancedRiskManager

# In main block:
bot = EMARSIStrategy(config)
bot.add_plugin(AdvancedRiskManager({
    'max_daily_loss_percent': 2.0,
    'max_drawdown_percent': 10.0,
    'base_risk_percent': 1.0
}))
```
- Show risk manager in action
- Demonstrate trade rejection when limits hit

**09:00-11:00 - Step 4: Add Analytics Plugin (10 min)**
```python
from examples.plugins.trade_analytics import TradeAnalytics

bot.add_plugin(TradeAnalytics({
    'export_path': 'reports/ema_rsi_analytics.json'
}))
```
- Run strategy for a while
- Check generated report
- Analyze best trading hours

**11:00-14:00 - Step 5: Backtest (30 min)**
```python
# Create scripts/backtest_ema_rsi.py
from engines.backtest_engine import BacktestEngine
from strategies.ema_rsi_strategy import EMARSIStrategy

config = {
    'symbol': 'EURUSD',
    'timeframe': mt5.TIMEFRAME_M30,
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2024, 10, 1),
    'initial_balance': 10000,
    'ema_fast': 12,
    'ema_slow': 26,
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70
}

engine = BacktestEngine(config)
strategy = EMARSIStrategy(config)
results = engine.run(strategy)

print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Total Profit: ${results['total_profit']:.2f}")
```
- Show results
- Identify areas for improvement

**14:00-17:00 - Step 6: Optimize (60 min)**
```python
# Create scripts/optimize_ema_rsi.py
from itertools import product

ema_fast_range = range(8, 20, 2)
ema_slow_range = range(20, 40, 4)
rsi_oversold_range = range(20, 40, 5)
rsi_overbought_range = range(60, 80, 5)

best_sharpe = -999
best_params = None

for fast, slow, os, ob in product(
    ema_fast_range, ema_slow_range, 
    rsi_oversold_range, rsi_overbought_range
):
    if fast >= slow:
        continue
    
    config.update({
        'ema_fast': fast,
        'ema_slow': slow,
        'rsi_oversold': os,
        'rsi_overbought': ob
    })
    
    results = engine.run(strategy)
    
    if results['sharpe_ratio'] > best_sharpe:
        best_sharpe = results['sharpe_ratio']
        best_params = (fast, slow, os, ob)
        print(f"New best: EMA({fast},{slow}) RSI({os},{ob}) - Sharpe: {best_sharpe:.2f}")

print(f"\nOptimal Parameters:")
print(f"EMA Fast: {best_params[0]}")
print(f"EMA Slow: {best_params[1]}")
print(f"RSI Oversold: {best_params[2]}")
print(f"RSI Overbought: {best_params[3]}")
```
- Show optimization progress
- Visualize parameter heatmap
- Select best parameters

**17:00-19:30 - Step 7: Deploy to Production (20 min)**

**7.1 - Update Config**
```json
{
    "accounts": {
        "live": {
            "login": YOUR_LIVE_LOGIN,
            "password": "YOUR_PASSWORD",
            "server": "YOUR_BROKER"
        }
    },
    "symbols": {
        "EURUSD": {
            "enabled": true,
            "timeframe": "M30",
            "ema_fast": 12,
            "ema_slow": 28,
            "rsi_oversold": 25,
            "rsi_overbought": 75,
            "risk_percent": 0.5
        }
    }
}
```

**7.2 - Create Production Runner**
```python
# run_ema_rsi_prod.py
import logging
from strategies.ema_rsi_strategy import EMARSIStrategy
from examples.plugins.advanced_risk_manager import AdvancedRiskManager
from examples.plugins.trade_analytics import TradeAnalytics
from examples.plugins.telegram_notifier import TelegramNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ema_rsi_prod.log'),
        logging.StreamHandler()
    ]
)

# Load config
config = Config.from_file('config/config.json')

# Create strategy
bot = EMARSIStrategy(config)

# Add production plugins
bot.add_plugin(AdvancedRiskManager({
    'max_daily_loss_percent': 2.0,
    'max_drawdown_percent': 10.0
}))

bot.add_plugin(TradeAnalytics({
    'export_path': 'reports/production_analytics.json'
}))

bot.add_plugin(TelegramNotifier({
    'bot_token': 'YOUR_BOT_TOKEN',
    'chat_id': 'YOUR_CHAT_ID'
}))

# Connect and run
bot.connect(account='live')
bot.run(interval_seconds=60)
```

**7.3 - Safety Checks**
```python
# Pre-deployment checklist
def pre_deployment_check():
    checks = [
        ("Config file exists", os.path.exists('config/config.json')),
        ("Backtest results positive", results['profit_factor'] > 1.5),
        ("Risk limits set", config.get('max_daily_loss_percent') is not None),
        ("Logging configured", logging.getLogger().hasHandlers()),
        ("Plugins loaded", len(bot.plugins) >= 2),
    ]
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    all_passed = all(c[1] for c in checks)
    return all_passed

if pre_deployment_check():
    print("All checks passed! Starting production...")
    bot.run()
else:
    print("Deployment checks failed. Please review.")
```

**19:30-20:00 - Monitoring & Wrap-up**
- Show live monitoring dashboard
- Check Telegram notifications
- Review daily analytics report
- Final tips for live trading

### Key Takeaways
1. Complete workflow takes ~2.5 hours vs. 2-3 days from scratch
2. Templates provide solid foundation
3. Plugins enable modular functionality
4. Backtest and optimize before risking money
5. Monitor closely after deployment

### Demo Assets Needed
- Full working strategy code
- Backtest results charts
- Optimization heatmaps
- Telegram notification screenshots
- Live trading dashboard
- Analytics reports

---

## 🎥 Production Tips

### Recording Best Practices

**Video Quality:**
- Resolution: 1080p minimum (1920x1080)
- Frame rate: 30 FPS
- Codec: H.264
- Audio: Clear microphone, minimal background noise

**Screen Recording:**
- Use OBS Studio or Camtasia
- Record full screen or specific window
- Highlight cursor for clarity
- Use zoom for important code sections

**Editing:**
- Add intro/outro (5-10 seconds)
- Include chapter markers
- Speed up repetitive parts (code typing)
- Add captions for accessibility

**Code Visibility:**
- Large font size (16-18pt minimum)
- High contrast theme (dark background, light text)
- Hide sensitive information (API keys, account numbers)
- Use syntax highlighting

### Tutorial Structure Template

```
1. Introduction (10%)
   - What we'll build
   - Prerequisites
   - Expected outcome

2. Theory/Concept (20%)
   - Why this matters
   - Key concepts
   - Architecture overview

3. Hands-on Demo (50%)
   - Live coding
   - Step-by-step implementation
   - Running the code
   - Analyzing results

4. Best Practices (10%)
   - Common mistakes
   - Optimization tips
   - Security considerations

5. Wrap-up (10%)
   - Recap key points
   - Next steps
   - Additional resources
```

---

## 📚 Additional Resources

### Companion Materials

For each tutorial, provide:

1. **Code Repository**
   - Complete working code
   - Commit per tutorial step
   - Branch per tutorial

2. **Written Guide**
   - Tutorial transcript
   - Code snippets
   - Screenshots

3. **Cheat Sheet**
   - Quick reference
   - Common commands
   - Troubleshooting

4. **Practice Exercises**
   - Beginner: Modify parameters
   - Intermediate: Add features
   - Advanced: Build from scratch

### Community Engagement

**YouTube:**
- Enable comments for questions
- Pin links to code repository
- Create playlist for series
- Add to relevant YouTube categories

**GitHub:**
- Link to videos in README
- Create discussions for each tutorial
- Accept pull requests for improvements

**Documentation:**
- Embed videos in docs
- Provide text alternative
- Keep videos up to date

---

## ✅ Tutorial Checklist

Before publishing each tutorial:

- [ ] Script reviewed and tested
- [ ] Code examples working
- [ ] Recording quality checked
- [ ] Audio clear and professional
- [ ] Editing complete
- [ ] Intro/outro added
- [ ] Captions added
- [ ] Thumbnail created
- [ ] Description written
- [ ] Tags added
- [ ] Code repository updated
- [ ] Documentation links added
- [ ] Community posted about
- [ ] Feedback mechanism set up

---

**Total Series Duration:** ~60 minutes  
**Total Tutorials:** 5  
**Difficulty Range:** Beginner to Advanced  
**Target Audience:** Python traders  
**Production Status:** Outlined, ready for recording

**Last Updated:** November 4, 2025
