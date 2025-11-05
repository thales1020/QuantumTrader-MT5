# Tests Directory

Comprehensive test suite for ML-SuperTrend-MT5 trading system.

## Directory Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests with MT5 and system tests
├── features/       # Feature-specific tests (crypto, plugins, templates)
├── diagnostics/    # Diagnostic and troubleshooting tools
├── helpers.py      # Shared test helper functions
└── README.md       # This file
```

## Test Categories

### 📦 Unit Tests (`unit/`)
Test individual components in isolation:
- Configuration management
- Symbol handling
- Risk management
- Breakeven logic
- Paper trading broker API

[→ See unit/README.md for details](unit/README.md)

### 🔗 Integration Tests (`integration/`)
Test components working together:
- MT5 connectivity and trading
- Backtest system integration
- Live trading workflows
- Order execution pipelines

[→ See integration/README.md for details](integration/README.md)

### ⭐ Feature Tests (`features/`)
Test specific features and capabilities:
- Cryptocurrency trading
- Plugin system
- Strategy templates
- Test helpers

[→ See features/README.md for details](features/README.md)

### 🔍 Diagnostics (`diagnostics/`)
Tools for troubleshooting and verification:
- ICT signal diagnostics
- Crypto dual order verification
- Manual testing utilities

[→ See diagnostics/README.md for details](diagnostics/README.md)

## Quick Start

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Feature tests only
pytest tests/features/
```

### Run with Coverage
```bash
# All tests with coverage
pytest tests/ --cov=core --cov=engines --cov-report=html

# View coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

## Test Organization Principles

### Unit Tests
- ✅ Fast execution (< 1 second each)
- ✅ No external dependencies (MT5, network)
- ✅ Test one thing at a time
- ✅ Use mocks for external services

### Integration Tests
- ⚠️ Slower execution (seconds to minutes)
- ⚠️ May require MT5 running
- ⚠️ Test multiple components together
- ⚠️ Use real or simulated MT5 data

### Feature Tests
- ✅ Moderate speed
- ✅ Test complete features
- ✅ Independent of MT5 (mostly)
- ✅ Focus on user-facing functionality

## Test Helpers

Common test utilities are in `helpers.py`:
- `create_test_broker()` - Create paper trading broker for tests
- `submit_and_fill_order()` - Submit and auto-fill test order
- `create_position_with_sl_tp()` - Create test position with SL/TP
- `trigger_stop_loss()` - Simulate SL trigger
- `trigger_take_profit()` - Simulate TP trigger
- `create_bar()` - Create price bar for testing

[→ See helpers.py for full API](helpers.py)

## Running Tests in Development

### Pre-commit Testing
```bash
# Quick smoke test (< 30 seconds)
pytest tests/unit/ -v

# Full test suite before commit
pytest tests/ --cov=core --cov=engines
```

### Continuous Testing
```bash
# Watch mode - rerun on file changes
pytest-watch tests/unit/
```

### Debugging Tests
```bash
# Run with detailed output
pytest tests/ -vv --tb=long

# Run specific test
pytest tests/unit/test_configuration.py::test_config_valid -vv

# Drop into debugger on failure
pytest tests/ --pdb
```

## Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Key workflows covered
- **Feature Tests**: All user-facing features tested

Current coverage: ~15% (improving to 30%+)

## Contributing Tests

When adding new tests:
1. Choose appropriate category (unit/integration/features)
2. Follow existing naming conventions (`test_*.py`)
3. Add docstrings explaining what is tested
4. Update relevant README.md
5. Ensure tests pass before committing

## CI/CD Integration

Tests run automatically on:
- Every commit (unit tests)
- Pull requests (full suite)
- Nightly builds (integration + performance)

## Notes

⚠️ **MT5 Tests**: Require MetaTrader 5 running with valid account

💡 **Tip**: Run unit tests frequently, integration tests before commits

✅ **Best Practice**: Write tests for new features before implementation (TDD)

---

For more details on testing strategy, see:
- [Testing Index](../docs/04-testing/TESTING_INDEX.md)
- [Test Plan](../docs/04-testing/TEST_PLAN.md)
- [Test Requirements](../docs/04-testing/TEST_REQUIREMENTS.md)
- `test_dual_order_risk_awareness()` - Warns about 2x risk with dual orders

### 5. test_risk_management.py
Tests for risk calculations and account protection:
-  Position sizing for different pairs (EUR, GBP, JPY, XAU)
-  Risk limits enforcement
-  Stop loss calculation
-  Take profit calculation
-  Risk-reward ratio validation
-  Account protection mechanisms
-  Lot size validation
-  Balance impact calculations

**Key Tests:**
- `test_position_size_with_dual_orders()` - Validates 2x risk
- `test_dual_order_tp_both_orders()` - Validates dual TPs
- `test_total_account_risk_limit()` - Ensures safe total risk
- `test_lot_size_rounding()` - Ensures correct lot sizing

### 6. test_live_trading.py  NEW
Tests for live trading mode and safety:
-  MT5 connection and initialization
-  Account login and authentication
-  Live order placement (BUY/SELL)
-  Dual order placement validation
-  Position management (open/close/monitor)
-  Safety mechanisms (daily loss, drawdown, consecutive losses)
-  Live risk management
-  Data validation (ticks, historical, symbols)
-  Logging and monitoring
-  Recovery mechanisms (reconnection, restart)
-  Trading modes (demo/live/paper)

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
-  ICT Bot signal generation
-  Dual orders implementation (RR 1:1 + Main RR)
-  Position sizing with 2x risk awareness
-  Stop loss and take profit calculations
-  Backtest P&L calculations
-  Configuration validation
-  Risk management rules
-  Account protection mechanisms

### Components Not Tested (Integration/Manual Testing)
-  MetaTrader5 connection (requires MT5 running)
-  Real order placement (requires demo account)
-  Historical data fetching (requires MT5)
-  Live trading execution

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

###  All Pass
System is ready for demo trading. Configuration is valid, risk calculations are correct, dual orders logic is working properly.

###  Some Fail
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
