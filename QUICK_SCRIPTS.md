# Quick Scripts Reference

Fast reference for common tasks. Copy and paste commands directly.

---

## 🚀 Most Used Scripts

### Backtest a Strategy (Fastest)
```bash
python examples/quick_backtest.py
```

### Paper Trading Test
```bash
python scripts/test_deployed_bots.py
```

### Live Trading Dashboard
```bash
python scripts/dashboard.py
```

### Check Data
```bash
python scripts/check_data.py
```

---

## 📊 By Task

### "I want to backtest"
```bash
# Quick backtest
python examples/quick_backtest.py

# SuperTrend backtest
python examples/backtest_supertrend_v2.py

# ICT backtest
python examples/backtest_ict_v2.py
```

### "I want to paper trade"
```bash
# Test deployed bots (recommended)
python scripts/test_deployed_bots.py

# Simple paper trading test
python -m pytest tests/integration/test_paper_trading_simple.py
```

### "I want to analyze results"
```bash
# Quick analysis
python scripts/quick_backtest_analysis.py

# Simple analysis
python scripts/simple_backtest_analysis.py

# Debug signals
python scripts/debug_signals.py
```

### "I want to create a strategy"
```bash
# Interactive strategy creator
python scripts/create_strategy.py

# Validate templates
python scripts/validate_templates.py
```

### "I want to test everything"
```bash
# Test all use cases
python scripts/test_all_use_cases.py

# Test strategy examples
python scripts/test_strategy_examples.py

# Test plugin examples
python scripts/test_plugin_examples.py

# Run full test suite
python -m pytest tests/
```

### "I want to go live"
```bash
# 1. First backtest thoroughly
python examples/backtest_supertrend_v2.py

# 2. Then paper trade for 1 month
python scripts/test_deployed_bots.py

# 3. Monitor with dashboard
python scripts/dashboard.py

# 4. When ready, go live
python scripts/live_trade_ict_audusd.py
```

---

## 🎯 By Skill Level

### Beginner
```bash
# Start here - simple backtest
python examples/quick_backtest.py

# Try conservative strategy
python examples/use_cases/use_case_1_conservative.py

# Monitor with dashboard
python scripts/dashboard.py
```

### Intermediate
```bash
# Create your own strategy
python scripts/create_strategy.py

# Test it
python scripts/test_generated_strategy.py

# Analyze performance
python scripts/quick_backtest_analysis.py
```

### Advanced
```bash
# Test all scenarios
python scripts/test_all_use_cases.py

# Migrate to cloud
python scripts/migrate_to_supabase.py

# Generate documentation
python scripts/generate_uml.py
```

---

## 🔧 Development

### Run Tests
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Feature tests only
python -m pytest tests/features/

# All tests with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Diagnostics
```bash
# Diagnose ICT signals
python tests/diagnostics/diagnose_ict_signal.py

# Verify crypto orders
python tests/diagnostics/verify_crypto_dual_orders.py
```

---

## 💾 Database

### Supabase
```bash
# Test connection
python scripts/test_supabase.py

# Migrate data
python scripts/migrate_to_supabase.py
```

---

## 📝 Common Workflows

### Full Backtest Workflow
```bash
# 1. Check data
python scripts/check_data.py

# 2. Run backtest
python examples/backtest_supertrend_v2.py

# 3. Analyze results
python scripts/quick_backtest_analysis.py

# 4. Debug if needed
python scripts/debug_signals.py
```

### Paper Trading Workflow
```bash
# 1. Backtest first
python examples/quick_backtest.py

# 2. Test deployed bots
python scripts/test_deployed_bots.py

# 3. Monitor dashboard
python scripts/dashboard.py

# 4. Check data regularly
python scripts/check_data.py
```

### Strategy Development Workflow
```bash
# 1. Create strategy
python scripts/create_strategy.py

# 2. Validate template
python scripts/validate_templates.py

# 3. Test strategy
python scripts/test_generated_strategy.py

# 4. Backtest
python examples/quick_backtest.py
```

---

## 🐛 Troubleshooting

### "Script won't run"
```bash
# Check Python environment
python --version

# Activate venv
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "No data available"
```bash
# Check data
python scripts/check_data.py

# Debug
python scripts/debug_signals.py
```

### "MT5 connection error"
```bash
# 1. Check MT5 is running
# 2. Check you're logged in
# 3. Test with simple script
python -m pytest tests/integration/test_simple_integration.py
```

### "Import errors"
```bash
# Make sure you're in project root
cd c:\github\ML-SuperTrend-MT5

# Activate environment
venv\Scripts\activate

# Reinstall
pip install -e .
```

---

## 📁 File Locations

### Scripts
```
scripts/               # Main utility scripts
examples/              # Example implementations
tests/                 # Test files
```

### Results
```
reports/               # Backtest reports (Excel)
logs/                  # Log files
data/                  # Historical data
```

### Config
```
config/config.json     # Main configuration
config/supabase.json   # Database config
```

---

## ⚡ One-Liners

```bash
# Quick backtest
python examples/quick_backtest.py

# Paper trade
python scripts/test_deployed_bots.py

# Dashboard
python scripts/dashboard.py

# Check data
python scripts/check_data.py

# Debug
python scripts/debug_signals.py

# Test all
python -m pytest tests/

# Create strategy
python scripts/create_strategy.py
```

---

## 📞 Need Help?

1. **Check**: `SCRIPTS_INDEX.md` - Full script documentation
2. **Read**: `docs/01-getting-started/QUICKSTART.md` - Quick start guide
3. **Test**: `python scripts/test_all_use_cases.py` - Verify setup
4. **Debug**: `python scripts/debug_signals.py` - Find issues

---

**Tip**: Bookmark this file for quick reference! 📌
