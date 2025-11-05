# Integration Tests

Integration tests that verify components working together and MT5 connectivity.

## Files

### MT5 Integration
- `test_ict_mt5.py` - ICT strategy with real MT5 connection
- `test_ict_real_mt5.py` - ICT bot real MT5 integration
- `test_supertrend_real_mt5.py` - SuperTrend bot real MT5 integration
- `test_live_trading.py` - Live trading integration tests

### System Integration
- `test_backtest_system.py` - Backtest system integration
- `test_backtest_engines.py` - Backtest engine integration
- `test_buy_order.py` - Order submission integration
- `test_memory_leak.py` - Memory leak detection
- `test_paper_trading_fixes.py` - Paper trading fixes validation
- `test_paper_trading_simple.py` - Simple paper trading integration
- `test_simple_integration.py` - Basic integration tests

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run MT5 tests only (requires MT5 running)
pytest tests/integration/test_*_mt5.py

# Run without MT5 connection
pytest tests/integration/ -k "not mt5"

# Run specific test
pytest tests/integration/test_backtest_system.py
```

## Requirements

### For MT5 Tests
- MetaTrader 5 installed and running
- Valid MT5 account (demo or real)
- MT5 Python package installed
- Network connection

### For System Tests
- All project dependencies installed
- Test data available
- Sufficient system resources

## Notes

⚠️ **Warning**: MT5 integration tests require actual MT5 connection and may take longer to run.

💡 **Tip**: Run system integration tests first, then MT5 tests separately.
