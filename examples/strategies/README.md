# Strategy Examples

This directory contains comprehensive strategy examples demonstrating different trading approaches and techniques.

## 📚 Available Examples

### 1. Multi-Timeframe Strategy
**File:** `multi_timeframe.py`  
**Difficulty:** ⭐⭐ Intermediate  
**Concepts:** Multiple timeframe analysis, trend confirmation

Demonstrates how to:
- Use higher timeframe (H1) for trend direction
- Use lower timeframe (M15) for entry signals
- Combine EMA for trend with RSI for entries
- Implement time-based data caching

**Key Learning Points:**
- Multi-timeframe analysis techniques
- Caching higher timeframe data
- Trend-following with precision entries

```python
config = {
    'symbol': 'EURUSD',
    'lower_timeframe': mt5.TIMEFRAME_M15,
    'higher_timeframe': mt5.TIMEFRAME_H1,
    'rsi_period': 14,
    'ema_period': 200,
}
bot = MultiTimeframeStrategy(config)
```

---

### 2. Portfolio Strategy
**File:** `portfolio.py`  
**Difficulty:** ⭐⭐⭐ Advanced  
**Concepts:** Multi-symbol trading, portfolio risk management, correlation analysis

Demonstrates how to:
- Trade multiple symbols simultaneously
- Manage total portfolio risk
- Calculate correlation between symbols
- Implement performance-based rebalancing
- Select best opportunities across portfolio

**Key Learning Points:**
- Portfolio construction and management
- Cross-symbol risk allocation
- Correlation-aware position sizing
- Dynamic weight adjustment

```python
config = {
    'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
    'total_risk_percent': 3.0,
    'max_positions': 3,
}
portfolio = PortfolioStrategy(config)
```

---

### 3. Custom Indicators Strategy
**File:** `custom_indicators.py`  
**Difficulty:** ⭐⭐⭐ Advanced  
**Concepts:** Custom indicator development, confluence trading

Demonstrates how to:
- Implement Ichimoku Cloud from scratch
- Calculate Pivot Points
- Build VWAP indicator
- Combine multiple indicators for confluence

**Key Learning Points:**
- Creating custom technical indicators
- Indicator combination logic
- Multi-indicator confirmation systems
- Advanced technical analysis

```python
config = {
    'symbol': 'EURUSD',
    'tenkan_period': 9,
    'kijun_period': 26,
    'senkou_b_period': 52,
}
bot = CustomIndicatorStrategy(config)
```

---

## 🎯 Usage

### Running an Example

1. **Import the strategy:**
   ```python
   from examples.strategies.multi_timeframe import MultiTimeframeStrategy
   ```

2. **Create configuration:**
   ```python
   config = {
       'symbol': 'EURUSD',
       'timeframe': 'M15',
       'risk_percent': 1.0,
       # ... strategy-specific parameters
   }
   ```

3. **Initialize and run:**
   ```python
   bot = MultiTimeframeStrategy(config)
   bot.run()  # Live trading
   # or
   bot.backtest(start_date='2024-01-01', end_date='2024-12-31')
   ```

### Testing Examples

Run the test suite to verify all examples work:

```bash
python scripts/test_strategy_examples.py
```

---

## 📖 Learning Path

### Beginner Level
Start with simpler examples from `examples/use_cases/`:
1. `use_case_1_conservative.py` - Conservative trading
2. `use_case_2_scalping.py` - Scalping approach
3. `use_case_3_risk_management.py` - Risk management

### Intermediate Level
Move to multi-timeframe analysis:
1. `multi_timeframe.py` - Trend + Entry timeframes
2. Study how higher/lower timeframes interact
3. Learn data caching techniques

### Advanced Level
Explore portfolio and custom indicators:
1. `portfolio.py` - Multi-symbol strategies
2. `custom_indicators.py` - Build your own indicators
3. Combine concepts from multiple examples

---

## 🔧 Customization

### Modify Existing Examples

All examples are designed to be easily customizable:

1. **Change parameters** in config dict
2. **Add new indicators** in `calculate_indicators()`
3. **Modify entry logic** in `generate_signal()`
4. **Adjust risk management** in `calculate_position_size()`

### Create Your Own

Use these examples as templates:

```python
from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry

@StrategyRegistry.register("my_strategy")
class MyStrategy(BaseTradingBot):
    def __init__(self, config):
        super().__init__(config)
        # Your initialization
    
    def calculate_indicators(self, df):
        # Your indicators
        return df
    
    def generate_signal(self, df):
        # Your logic
        return signal
```

---

## 📊 Comparison

| Strategy | Symbols | Timeframes | Indicators | Complexity | Best For |
|----------|---------|------------|------------|------------|----------|
| Multi-TF | 1 | 2 (H1+M15) | EMA, RSI | Medium | Trend following |
| Portfolio | 3-10 | 1 | EMA Crossover | High | Diversification |
| Custom | 1 | 1 | Ichimoku, Pivots, VWAP | High | Confluence trading |

---

## 🚀 Next Steps

After mastering these examples:

1. **Combine Techniques** - Use multi-timeframe in portfolio strategy
2. **Add Plugins** - Integrate with plugin system (see `examples/plugins/`)
3. **Use Templates** - Generate strategies faster (see `examples/templates/`)
4. **Backtest** - Validate your ideas with historical data
5. **Deploy** - Move to live trading with proper risk management

---

## 📚 Related Documentation

- [Strategy Templates](../../docs/STRATEGY_TEMPLATES.md) - Generate strategies from templates
- [Plugin System](../../docs/PLUGIN_QUICK_START.md) - Extend functionality with plugins
- [Customization Guide](../../docs/CUSTOMIZATION_GUIDE.md) - Complete customization reference
- [Use Cases](../use_cases/README.md) - Simpler examples for beginners

---

## ✅ Testing

All examples have been tested and verified:

```
✅ Multi-Timeframe Strategy - Import, instantiation, get_strategy_info()
✅ Portfolio Strategy - Import, instantiation, get_strategy_info()
✅ Custom Indicators Strategy - Import, instantiation, get_strategy_info()

Test Suite: 3/3 tests passed (100%)
```

---

## 💡 Tips

1. **Start Simple** - Master one concept before combining
2. **Backtest First** - Always validate before live trading
3. **Understand Risk** - Each example includes risk management
4. **Read Code** - Comments explain the 'why' not just the 'what'
5. **Experiment** - Modify parameters and observe results

---

## 🤝 Contributing

Have a useful strategy example? Contributions welcome!

1. Follow the existing code structure
2. Include comprehensive docstrings
3. Add usage example in main block
4. Test thoroughly before submitting

---

**Created**: November 4, 2025  
**Author**: QuantumTrader-MT5 Team  
**Version**: 1.0.0
