# QuantumTrader-MT5 - Executable Scripts Index

Complete list of all runnable scripts in this project, organized by category.

---

## 🚀 Quick Start Scripts

### Backtesting
```bash
# Quick backtest with SuperTrend strategy
python examples/quick_backtest.py

# Backtest SuperTrend v2 (optimized)
python examples/backtest_supertrend_v2.py

# Backtest ICT strategy v2
python examples/backtest_ict_v2.py

# Working backtest example
python examples/working_backtest.py
```

### Live Trading
```bash
# Live trade ICT strategy on AUDUSD
python scripts/live_trade_ict_audusd.py

# Test deployed bots (paper trading)
python scripts/test_deployed_bots.py

# Backtest deployed bots
python scripts/backtest_deployed_bots.py
```

---

## 📊 Analysis & Monitoring

### Data Analysis
```bash
# Check data availability
python scripts/check_data.py

# Debug trading signals
python scripts/debug_signals.py

# Quick backtest analysis
python scripts/quick_backtest_analysis.py

# Simple backtest analysis
python scripts/simple_backtest_analysis.py
```

### Dashboard & Monitoring
```bash
# Launch trading dashboard
python scripts/dashboard.py
```

---

## 🔧 Development Tools

### Strategy Creation
```bash
# Interactive strategy creator
python scripts/create_strategy.py

# Test generated strategy
python scripts/test_generated_strategy.py

# Validate strategy templates
python scripts/validate_templates.py
```

### Testing Scripts
```bash
# Test all use cases
python scripts/test_all_use_cases.py

# Test strategy examples
python scripts/test_strategy_examples.py

# Test plugin examples
python scripts/test_plugin_examples.py

# Test plugin usage
python examples/plugin_usage.py
```

---

## 🗄️ Database & Migration

### Supabase Integration
```bash
# Test Supabase connection
python scripts/test_supabase.py

# Migrate data to Supabase
python scripts/migrate_to_supabase.py
```

---

## 📐 UML & Documentation

### Generate UML Diagrams
```bash
# Generate UML diagrams
python scripts/generate_uml.py
```

---

## 🎯 Use Case Examples

### Conservative Trading
```bash
python examples/use_cases/use_case_1_conservative.py
```
- Low risk approach
- Good for beginners
- Slow but steady gains

### Scalping
```bash
python examples/use_cases/use_case_2_scalping.py
```
- High frequency trading
- Quick profits
- Requires active monitoring

### Trend Following
```bash
python examples/use_cases/use_case_3_trend_following.py
```
- Ride major trends
- Medium-term positions
- Good risk/reward ratio

### Range Trading
```bash
python examples/use_cases/use_case_4_range_trading.py
```
- Trade sideways markets
- Buy low, sell high
- Works in consolidation

### Breakout Trading
```bash
python examples/use_cases/use_case_5_breakout.py
```
- Catch explosive moves
- Higher risk, higher reward
- Momentum-based

---

## 🧪 Testing Suite

### Unit Tests
```bash
# Test configuration
python -m pytest tests/unit/test_configuration.py

# Test symbol handling
python -m pytest tests/unit/test_symbol.py

# Test breakeven logic
python tests/test_breakeven.py

# Test risk management
python -m pytest tests/unit/test_risk_management.py
```

### Integration Tests
```bash
# Test ICT bot with MT5
python -m pytest tests/integration/test_ict_mt5.py

# Test SuperTrend with MT5
python -m pytest tests/integration/test_supertrend_real_mt5.py

# Test live trading
python -m pytest tests/integration/test_live_trading.py

# Test backtest engines
python -m pytest tests/integration/test_backtest_engines.py

# Test backtest system
python -m pytest tests/integration/test_backtest_system.py

# Test memory leak fix
python -m pytest tests/integration/test_memory_leak.py

# Test paper trading fixes
python -m pytest tests/integration/test_paper_trading_fixes.py

# Simple paper trading test
python -m pytest tests/integration/test_paper_trading_simple.py

# Simple integration test
python -m pytest tests/integration/test_simple_integration.py
```

### Feature Tests
```bash
# Test crypto trading
python -m pytest tests/features/test_crypto_trading.py

# Test crypto orders
python -m pytest tests/features/test_crypto_orders.py

# Test crypto imports
python -m pytest tests/features/test_crypto_import.py

# Test buy orders
python -m pytest tests/features/test_buy_order.py

# Test plugin system
python -m pytest tests/features/test_plugin_system.py

# Test plugin integration
python -m pytest tests/features/test_plugin_integration.py

# Test template system
python -m pytest tests/features/test_template_system.py
```

### Diagnostic Tools
```bash
# Diagnose ICT signals
python tests/diagnostics/diagnose_ict_signal.py

# Verify crypto dual orders
python tests/diagnostics/verify_crypto_dual_orders.py
```

---

## 🔍 Advanced Examples

### Strategy Examples
```bash
# Multi-timeframe strategy
python examples/strategies/multi_timeframe.py

# Portfolio management
python examples/strategies/portfolio.py

# Advanced SuperTrend
python examples/strategies/advanced_supertrend.py

# ICT Smart Money Concepts
python examples/strategies/ict_smc.py
```

### Plugin Examples
```bash
# Advanced risk manager
python examples/plugins/advanced_risk_manager.py

# Custom indicators
python examples/plugins/custom_indicators.py

# Trade notifier
python examples/plugins/trade_notifier.py
```

### Integration Workflows
```bash
# Full backtesting workflow
python examples/integration/full_backtest_workflow.py

# Live trading setup
python examples/integration/live_trading_setup.py

# Multi-bot deployment
python examples/integration/multi_bot_deployment.py
```

---

## 🛠️ Utility Scripts

### Data Management
```bash
# Check data integrity
python scripts/utils/check_data_integrity.py

# Clean old data
python scripts/utils/clean_old_data.py

# Export data
python scripts/utils/export_data.py
```

### Code Quality
```bash
# Remove emojis from code
python scripts/remove_emojis_v3.py
```

---

## ⚙️ Configuration

Before running scripts, ensure:

1. **MT5 installed and logged in** (for live/demo trading)
2. **config.json configured** (copy from `config/config.example.json`)
3. **Virtual environment activated**:
   ```bash
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
4. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📋 Script Categories Summary

| Category | Count | Purpose |
|----------|-------|---------|
| **Backtesting** | 4 | Test strategies on historical data |
| **Live Trading** | 3 | Execute trades on real/demo accounts |
| **Analysis** | 4 | Analyze data and signals |
| **Dashboard** | 1 | Monitor trading activity |
| **Strategy Tools** | 3 | Create and validate strategies |
| **Testing** | 3 | Test examples and use cases |
| **Database** | 2 | Supabase integration |
| **Documentation** | 1 | Generate UML diagrams |
| **Use Cases** | 5 | Real-world trading scenarios |
| **Unit Tests** | 4 | Test individual components |
| **Integration Tests** | 9 | Test system workflows |
| **Feature Tests** | 7 | Test specific capabilities |
| **Diagnostics** | 2 | Troubleshooting tools |
| **Strategy Examples** | 4+ | Advanced implementations |
| **Plugin Examples** | 3+ | Extension examples |
| **Integration Examples** | 3+ | Complete workflows |

**Total Executable Scripts: 60+**

---

## 🎓 Learning Path

### Beginner (Week 1-2)
1. Run `examples/quick_backtest.py` - Understand backtesting
2. Try `examples/use_cases/use_case_1_conservative.py` - Simple strategy
3. Test with `scripts/test_deployed_bots.py` - Paper trading
4. Monitor with `scripts/dashboard.py` - Real-time tracking

### Intermediate (Week 3-4)
1. Create strategy with `scripts/create_strategy.py`
2. Test with `scripts/test_strategy_examples.py`
3. Try multi-timeframe: `examples/strategies/multi_timeframe.py`
4. Run diagnostics: `tests/diagnostics/diagnose_ict_signal.py`

### Advanced (Month 2+)
1. Build plugins: `examples/plugins/advanced_risk_manager.py`
2. Full workflow: `examples/integration/full_backtest_workflow.py`
3. Deploy multiple bots: `examples/integration/multi_bot_deployment.py`
4. Migrate to cloud: `scripts/migrate_to_supabase.py`

---

## 💡 Pro Tips

1. **Always backtest first** - Use `examples/quick_backtest.py` before live trading
2. **Start with paper trading** - Use `scripts/test_deployed_bots.py` to practice
3. **Monitor actively** - Keep `scripts/dashboard.py` running
4. **Check data quality** - Run `scripts/check_data.py` regularly
5. **Use diagnostics** - When signals look wrong, use `scripts/debug_signals.py`
6. **Test changes** - Run `scripts/test_all_use_cases.py` after modifications
7. **Validate templates** - Use `scripts/validate_templates.py` for custom strategies

---

## 🚨 Important Notes

### Before Live Trading
- ✅ Test on demo account for at least 1 month
- ✅ Backtest with at least 6 months of data
- ✅ Verify risk management settings
- ✅ Understand maximum drawdown
- ✅ Have emergency stop plan

### Performance Expectations
- Conservative: 5-15% annual return
- Moderate: 15-30% annual return
- Aggressive: 30-50% annual return
- **Risk scales with returns**

### Common Issues
- **MT5 not connected**: Check MT5 terminal is running
- **No data**: Run `scripts/check_data.py` to verify
- **Import errors**: Activate virtual environment
- **Strategy not working**: Use `scripts/debug_signals.py`

---

## 📞 Support

- **Documentation**: Check `docs/` folder
- **Examples**: All in `examples/` folder
- **Issues**: GitHub Issues
- **Quick Start**: `docs/01-getting-started/QUICKSTART.md`

---

**Last Updated**: November 5, 2025  
**Version**: 2.0  
**Total Scripts**: 60+
