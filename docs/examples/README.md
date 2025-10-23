# Educational Examples

This folder contains **educational examples** demonstrating various trading concepts and patterns. These files are **NOT integrated** with the production bots and are provided for learning purposes only.

## 📚 Files

### 1. `news_filter.py`
**Purpose:** Demonstrates news filtering to avoid trading during high-impact economic events.

**Features:**
- Economic calendar integration (placeholder)
- Symbol-specific news impact detection
- Configurable time windows (before/after events)

**Status:** ⚠️ Example only - requires API integration

**Usage:**
```python
from news_filter import NewsFilter

news_filter = NewsFilter(api_key="YOUR_API_KEY")
if not news_filter.is_news_time("EURUSD"):
    # Safe to trade
    pass
```

---

### 2. `risk_manager.py`
**Purpose:** Demonstrates advanced risk management techniques.

**Features:**
- Daily loss limits (% based)
- Correlation checks between currency pairs
- Kelly Criterion position sizing

**Status:** ⚠️ Example only - not used in production bots

**Usage:**
```python
from risk_manager import RiskManager

risk_mgr = RiskManager(max_daily_loss_percent=3.0)
if risk_mgr.check_daily_loss_limit(account_balance):
    # Can continue trading
    pass
```

---

### 3. `usage_examples.py`
**Purpose:** Complete usage examples for the ML-SuperTrend-MT5 project.

**Contains 10 Examples:**
1. Basic bot setup
2. Multi-symbol trading
3. Conservative strategy
4. Aggressive strategy
5. Custom risk management
6. Performance analysis
7. News filter integration
8. Backtesting
9. Parameter optimization
10. Live monitoring dashboard

**Status:** ⚠️ Educational - uses old SuperTrend bot for demonstration

**Run:**
```powershell
python docs\examples\usage_examples.py
```

---

## 🎯 Why These Are Examples

These modules demonstrate **trading concepts** that could be integrated into production bots, but they are currently:

- ❌ **Not imported** by active trading bots
- ❌ **Not tested** in production environment
- ❌ **Missing dependencies** (API keys, full implementations)
- ✅ **Useful for learning** trading system architecture
- ✅ **Show best practices** for risk management and filtering

---

## 🚀 Production Bots

For **actual trading** with the ICT strategy, use:

- **ICT Bot:** `core/ict_bot.py` (original custom implementation)
- **ICT Bot SMC:** `core/ict_bot_smc.py` (enhanced with signal quality scoring)
- **Backtest Engine:** `engines/ict_backtest_engine_smc.py`
- **Run Scripts:** `run_ict_bot.py`, `run_ict_bot_smc.py`

See `ICT_README.md` and `ICT_SMC_README.md` for production documentation.

---

## 📝 Notes

- These examples use the **old SuperTrend bot** architecture for demonstration
- Production ICT bots have **built-in risk management** (not these modules)
- To integrate these concepts, you would need to:
  1. Add API keys and real implementations
  2. Import into production bot code
  3. Test thoroughly in demo environment
  4. Validate in backtest before live trading

---

**Last Updated:** October 17, 2025  
**Project:** ML-SuperTrend-MT5  
**License:** See LICENSE file in root directory
