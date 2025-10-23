# Unit Tests for ML-SuperTrend-MT5

## Overview
Comprehensive unit test suite to ensure system stability and correctness before live/demo trading.

## Test Files

### 1. test_supertrend_bot.py
Tests for SuperTrend Bot core functionality:
- ✅ Configuration creation and validation
- ✅ SuperTrend indicator calculation
- ✅ K-Means clustering for factor selection
- ✅ Trade execution logic
- ✅ SL/TP calculation
- ✅ Risk-reward ratios

**Key Tests:**
- `test_sl_tp_calculation_buy()` - Validates BUY order SL/TP
- `test_sl_tp_calculation_sell()` - Validates SELL order SL/TP
- `test_cluster_choice_*()` - Validates cluster selection logic

### 3. test_backtest_engines.py
Tests for backtest simulation accuracy:
- ✅ Backtest engine initialization
- ✅ Trade simulation (wins and losses)
- ✅ Profit calculation (BUY/SELL, wins/losses)
- ✅ Metrics calculation (WR, PF, DD)
- ✅ Quality tracking and buckets
- ✅ Dual order tracking

**Key Tests:**
- `test_calculate_profit_*()` - Validates P&L calculations
- `test_win_rate_calculation()` - Validates WR calculation
- `test_profit_factor_calculation()` - Validates PF calculation
- `test_dual_order_total_profit()` - Validates dual order P&L

### 4. test_configuration.py
Tests for configuration loading and validation:
- ✅ Config file exists and valid JSON
- ✅ Required sections present (accounts, symbols)
- ✅ Symbol configuration validation
- ✅ Timeframe validation
- ✅ Risk percent range validation
- ✅ RR ratio validation
- ✅ ICT parameters validation
- ✅ Dual order risk awareness

**Key Tests:**
- `test_config_file_valid_json()` - Ensures config is valid JSON
- `test_symbol_has_required_fields()` - Ensures all symbols configured properly
- `test_dual_order_risk_awareness()` - Warns about 2x risk with dual orders

### 5. test_risk_management.py
Tests for risk calculations and account protection:
- ✅ Position sizing for different pairs (EUR, GBP, JPY, XAU)
- ✅ Risk limits enforcement
- ✅ Stop loss calculation
- ✅ Take profit calculation
- ✅ Risk-reward ratio validation
- ✅ Account protection mechanisms
- ✅ Lot size validation
- ✅ Balance impact calculations

**Key Tests:**
- `test_position_size_with_dual_orders()` - Validates 2x risk
- `test_dual_order_tp_both_orders()` - Validates dual TPs
- `test_total_account_risk_limit()` - Ensures safe total risk
- `test_lot_size_rounding()` - Ensures correct lot sizing

### 6. test_live_trading.py ⭐ NEW
Tests for live trading mode and safety:
- ✅ MT5 connection and initialization
- ✅ Account login and authentication
- ✅ Live order placement (BUY/SELL)
- ✅ Dual order placement validation
- ✅ Position management (open/close/monitor)
- ✅ Safety mechanisms (daily loss, drawdown, consecutive losses)
- ✅ Live risk management
- ✅ Data validation (ticks, historical, symbols)
- ✅ Logging and monitoring
- ✅ Recovery mechanisms (reconnection, restart)
- ✅ Trading modes (demo/live/paper)

**Key Tests:**
- `test_mt5_initialization_success()` - Validates MT5 connection
- `test_buy_order_placement()` - Validates live BUY order
- `test_dual_order_placement_validation()` - Validates dual orders
- `test_daily_loss_limit_check()` - Validates daily loss stop
- `test_emergency_stop_conditions()` - Validates emergency stops
- `test_position_recovery_on_restart()` - Validates state recovery
- `test_margin_level_check()` - Validates margin safety

## Running Tests

### Run All Tests
```powershell
python -m unittest discover tests -v

# Or use the test runner
python run_tests.py
```

### Run Specific Test File
```powershell
python -m unittest tests.test_supertrend_bot -v
python -m unittest tests.test_backtest_engines -v
python -m unittest tests.test_configuration -v
python -m unittest tests.test_risk_management -v
python -m unittest tests.test_live_trading -v
```

### Run Using Test Runner Script
```powershell
# All tests (config + risk + live)
python run_tests.py
python run_tests.py --all

# Configuration tests only
python run_tests.py --config

# Risk management tests only
python run_tests.py --risk

# Live trading tests only
python run_tests.py --live
```

## Test Coverage

### Critical Components Tested
- ✅ ICT Bot signal generation
- ✅ Dual orders implementation (RR 1:1 + Main RR)
- ✅ Position sizing with 2x risk awareness
- ✅ Stop loss and take profit calculations
- ✅ Backtest P&L calculations
- ✅ Configuration validation
- ✅ Risk management rules
- ✅ Account protection mechanisms

### Components Not Tested (Integration/Manual Testing)
- ⚠️ MetaTrader5 connection (requires MT5 running)
- ⚠️ Real order placement (requires demo account)
- ⚠️ Historical data fetching (requires MT5)
- ⚠️ Live trading execution

## Expected Results

### All Tests Should Pass
Total: **80+ test cases**

Expected output:
```
Ran 85 tests in 0.5s
OK
```

### Important Warnings
Some tests will print warnings for awareness:
- Dual order risk doubling (total risk = 2x configured)
- High risk symbols (>2% total risk)
- Configuration issues

## Test Results Interpretation

### ✅ All Pass
System is ready for demo trading. Configuration is valid, risk calculations are correct, dual orders logic is working properly.

### ❌ Some Fail
- **Config tests fail**: Fix config.json
- **Risk tests fail**: Review risk calculations
- **Dual order tests fail**: Review open_position() logic
- **Backtest tests fail**: Review P&L calculations

## Integration with CI/CD
These tests can be integrated into CI/CD pipeline:
```yaml
# .github/workflows/test.yml
- name: Run Unit Tests
  run: python -m unittest discover tests -v
```

## Pre-Demo Checklist
Before running demo trading:
- [ ] All unit tests pass
- [ ] Configuration validated
- [ ] Risk calculations verified
- [ ] Dual order logic confirmed
- [ ] Backtest results reviewed
- [ ] MT5 connection tested manually
- [ ] Demo account balance sufficient

## Notes

### Dual Orders Important
Tests validate that each signal opens **2 orders**:
1. Quick profit order (RR 1:1)
2. Main profit order (configured RR, e.g., 3:1)

**Total risk = 2x configured risk_percent**

Example:
- Config: `risk_percent: 1.0`
- Actual total risk: **2.0%** (1% per order × 2 orders)

### Mock Testing
Many tests use mocks to avoid MT5 dependency:
- `@patch('core.ict_bot_smc.mt5')` - Mocks MT5 functions
- No real orders placed during testing
- Safe to run without MT5 connection

### Test Data
Tests use synthetic data where needed:
- Random OHLC data for indicator testing
- Fixed prices for calculation testing
- No historical data download required

## Troubleshooting

### Import Errors
```powershell
# Ensure project root is in path
$env:PYTHONPATH = "c:\github\ML-SuperTrend-MT5"
python -m unittest discover tests -v
```

### Module Not Found
```powershell
# Install required packages
pip install pandas numpy MetaTrader5
```

### Tests Timeout
Some tests may take longer if using real data. Use mocks for faster testing.

## Maintenance
Update tests when:
- Adding new features
- Modifying risk calculations
- Changing dual order logic
- Updating configuration structure
- Adding new symbols

---
**Version:** 1.0.0  
**Last Updated:** 2025-01-16  
**Test Coverage:** Core functionality + Dual orders + Risk management
