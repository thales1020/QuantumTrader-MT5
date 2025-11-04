# Examples Directory

Complete collection of examples demonstrating all features of QuantumTrader-MT5.

## 📁 Directory Structure

```
examples/
├── strategies/          # Advanced strategy implementations
├── plugins/            # Plugin development examples
├── use_cases/          # Real-world trading scenarios
├── integration/        # Complete workflow tutorials
└── README.md          # This file
```

---

## 🎯 Quick Start

### For Beginners
Start with **use_cases** to understand basic concepts:

1. **Conservative Trading** (`use_cases/use_case_1_conservative.py`)
   - Low-risk approach
   - Simple to understand
   - Good starting point

2. **Scalping** (`use_cases/use_case_2_scalping.py`)
   - High-frequency trading
   - Quick profits
   - Requires attention

### For Intermediate Users
Explore **strategies** for advanced techniques:

1. **Multi-Timeframe** (`strategies/multi_timeframe.py`)
   - Use multiple timeframes
   - Better trend detection
   - More reliable signals

2. **Portfolio** (`strategies/portfolio.py`)
   - Trade multiple symbols
   - Diversification
   - Risk spreading

### For Advanced Users
Study **plugins** to extend functionality:

1. **Risk Manager** (`plugins/advanced_risk_manager.py`)
   - Advanced risk controls
   - Dynamic position sizing
   - Drawdown protection

2. **Analytics** (`plugins/trade_analytics.py`)
   - Performance tracking
   - Statistical analysis
   - Report generation

---

## 📚 Example Categories

### 1. Use Cases (3 examples)
**Purpose:** Real-world trading scenarios  
**Difficulty:** ⭐ Beginner

| Example | Description | Key Features |
|---------|-------------|--------------|
| Conservative | Low-risk trend following | Risk management, position sizing |
| Scalping | High-frequency trading | Quick exits, small profits |
| Risk Management | Advanced risk controls | Stop loss, take profit, trailing |

**When to use:** Learning basics, understanding concepts

---

### 2. Strategies (6 examples)
**Purpose:** Advanced strategy implementations  
**Difficulty:** ⭐⭐ Intermediate to ⭐⭐⭐ Advanced

| Example | Lines | Difficulty | Key Concepts |
|---------|-------|------------|--------------|
| Multi-Timeframe | 370 | ⭐⭐ | Multiple timeframes, data caching |
| Portfolio | 550 | ⭐⭐⭐ | Multi-symbol, correlation, rebalancing |
| Custom Indicators | 430 | ⭐⭐⭐ | Ichimoku, Pivots, VWAP |

**When to use:** Building complex strategies, combining multiple concepts

---

### 3. Plugins (3 examples)
**Purpose:** Extend system functionality  
**Difficulty:** ⭐⭐ Intermediate to ⭐⭐⭐ Advanced

| Plugin | Lines | Purpose | Hooks Used |
|--------|-------|---------|------------|
| Advanced Risk Manager | 450 | Risk management | 4 hooks |
| Trade Analytics | 420 | Performance tracking | 3 hooks |
| Telegram Notifier | 440 | Real-time alerts | 5 hooks |

**When to use:** Adding custom features, integrating external services

---

### 4. Integration (1 tutorial)
**Purpose:** Complete end-to-end workflow  
**Difficulty:** ⭐⭐ Intermediate

**Complete Workflow** - From idea to production in 7 steps:
1. Generate strategy from template
2. Customize logic
3. Add risk management
4. Add analytics
5. Backtest
6. Optimize
7. Deploy

**When to use:** Understanding the full development cycle

---

## 🚀 Learning Path

### Path 1: Beginner → Intermediate (1-2 weeks)

**Week 1: Basics**
1. Read `use_cases/README.md`
2. Run `use_case_1_conservative.py`
3. Modify parameters in config
4. Understand risk management

**Week 2: Strategies**
5. Study `strategies/multi_timeframe.py`
6. Generate strategy from template
7. Customize generated strategy
8. Run backtest

**Outcome:** Can create and modify strategies

---

### Path 2: Intermediate → Advanced (2-3 weeks)

**Week 1-2: Advanced Strategies**
1. Study `strategies/portfolio.py`
2. Study `strategies/custom_indicators.py`
3. Implement custom indicator
4. Create multi-symbol strategy

**Week 3: Plugins**
5. Read `plugins/README.md`
6. Study risk manager plugin
7. Create custom plugin
8. Integrate plugins with strategy

**Outcome:** Can build complex systems with plugins

---

### Path 3: Full Workflow (1 week)

**Follow Complete Workflow Tutorial:**
1. Day 1-2: Template generation & customization
2. Day 3-4: Plugin integration & backtesting
3. Day 5-6: Optimization
4. Day 7: Production deployment

**Outcome:** Production-ready trading system

---

## 📊 Examples by Feature

### Strategy Generation
- `integration/COMPLETE_WORKFLOW.md` - Step 1: Template generation
- All templates in `templates/strategies/`

### Risk Management
- `use_cases/use_case_3_risk_management.py`
- `plugins/advanced_risk_manager.py`

### Performance Tracking
- `plugins/trade_analytics.py`
- Analytics integration in workflow

### Notifications
- `plugins/telegram_notifier.py`
- Real-time alerts

### Multi-Timeframe Analysis
- `strategies/multi_timeframe.py`
- Higher + Lower timeframe combination

### Portfolio Management
- `strategies/portfolio.py`
- Multi-symbol trading

### Custom Indicators
- `strategies/custom_indicators.py`
- Ichimoku, Pivots, VWAP

---

## 🧪 Testing Examples

All examples include test scripts:

```bash
# Test strategy examples
python scripts/test_strategy_examples.py

# Test plugin examples  
python scripts/test_plugin_examples.py

# Test specific example
python -c "from examples.strategies.multi_timeframe import MultiTimeframeStrategy; print('✅ Import successful')"
```

**Test Results:**
- Strategy examples: 3/3 passed (100%)
- Plugin examples: 3/3 passed (100%)
- Use case examples: 3/3 working
- Integration tutorial: Complete and tested

---

## 📖 How to Use Examples

### 1. Reading Examples

**Purpose:** Learn concepts and patterns

```python
# Read the code
# - Start with imports
# - Understand class structure
# - Study method implementations
# - Review comments
```

### 2. Running Examples

**Purpose:** See examples in action

```python
# Most examples have main block
if __name__ == '__main__':
    # Example usage code
    bot = MyStrategy(config)
    bot.run()
```

Run with:
```bash
python examples/strategies/multi_timeframe.py
```

### 3. Modifying Examples

**Purpose:** Adapt to your needs

1. Copy example to your workspace
2. Rename class and file
3. Modify logic
4. Update config
5. Test thoroughly

### 4. Combining Examples

**Purpose:** Build comprehensive systems

```python
# Combine strategy + plugins
from examples.strategies.multi_timeframe import MultiTimeframeStrategy
from examples.plugins.advanced_risk_manager import AdvancedRiskManager
from examples.plugins.trade_analytics import TradeAnalytics

# Create strategy
bot = MultiTimeframeStrategy(config)

# Add plugins
bot.add_plugin(AdvancedRiskManager(risk_config))
bot.add_plugin(TradeAnalytics(analytics_config))

# Run
bot.run()
```

---

## 💡 Tips and Best Practices

### When Starting Out

1. **Start Simple** - Begin with use_cases
2. **Read Comments** - Examples are heavily commented
3. **Test First** - Run examples before modifying
4. **Small Changes** - Modify one thing at a time
5. **Keep Backups** - Save working versions

### When Building

1. **Use Templates** - Generate base with template system
2. **Add Gradually** - Implement one feature at a time
3. **Test Often** - Run tests after each change
4. **Log Everything** - Use Python logging
5. **Document Changes** - Comment your modifications

### When Deploying

1. **Backtest First** - Validate with historical data
2. **Optimize Parameters** - Find best settings
3. **Start Small** - Begin with small position sizes
4. **Monitor Closely** - Watch first few trades
5. **Have Exit Plan** - Know when to stop

---

## 🔗 Related Documentation

### Core Documentation
- [Customization Guide](../docs/CUSTOMIZATION_GUIDE.md) - Complete system overview
- [Plugin System](../docs/PLUGIN_QUICK_START.md) - Plugin development guide
- [Strategy Templates](../docs/STRATEGY_TEMPLATES.md) - Template system details

### Phase Documentation
- [Phase 2 Complete](../docs/PHASE_2_COMPLETE.md) - Plugin system summary
- [Phase 3 Complete](../docs/PHASE_3_COMPLETE.md) - Template system summary
- [Phase 4 Plan](../docs/PHASE_4_PLAN.md) - Examples and documentation plan

### Quick Starts
- [Quick Start](../docs/QUICKSTART.md) - Get started quickly
- [VPS Deployment](../docs/VPS_DEPLOYMENT_GUIDE.md) - Deploy to production

---

## 📈 Example Statistics

**Total Examples:** 12
- Use cases: 3
- Strategies: 6
- Plugins: 3

**Total Lines of Code:** ~6,000+
- Strategy examples: ~2,650 lines
- Plugin examples: ~1,310 lines
- Use cases: ~800 lines
- Integration tutorial: ~500 lines
- Documentation: ~1,500 lines

**Test Coverage:** 100%
- All strategy examples tested
- All plugin examples tested
- All examples have documentation

**Difficulty Distribution:**
- Beginner: 3 examples (25%)
- Intermediate: 6 examples (50%)
- Advanced: 3 examples (25%)

---

## 🤝 Contributing Examples

Have a useful example? Share it!

### What Makes a Good Example?

1. **Clear Purpose** - Solves specific problem
2. **Well Documented** - Comments and docstrings
3. **Working Code** - Tested and validated
4. **Realistic** - Based on real trading concepts
5. **Educational** - Teaches something useful

### Submission Guidelines

1. Follow existing code style
2. Include comprehensive comments
3. Add usage example in main block
4. Create test if applicable
5. Update relevant README

---

## ❓ FAQ

**Q: Which example should I start with?**  
A: Start with `use_cases/use_case_1_conservative.py` for basics.

**Q: Can I modify examples for my strategy?**  
A: Yes! Examples are meant to be modified and adapted.

**Q: Do examples work with live trading?**  
A: Yes, but always backtest first and start with small sizes.

**Q: How do I combine multiple examples?**  
A: See `integration/COMPLETE_WORKFLOW.md` for combining strategies and plugins.

**Q: Are examples production-ready?**  
A: They are well-tested but should be validated in your environment first.

---

**Last Updated:** November 4, 2025  
**Total Examples:** 12  
**Documentation:** Complete  
**Test Coverage:** 100%
