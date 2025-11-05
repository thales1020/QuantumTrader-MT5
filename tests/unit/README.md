# Unit Tests

Unit tests for individual components and modules.

## Files

- `test_configuration.py` - Configuration manager tests
- `test_symbol.py` - Symbol handling tests
- `test_breakeven.py` - Breakeven stop-loss feature tests
- `test_risk_management.py` - Risk management module tests
- `test_paper_trading_broker.py` - Paper trading broker API tests
- `test_paper_trading_broker_v2.py` - Paper trading broker v2 tests

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_configuration.py

# Run with coverage
pytest tests/unit/ --cov=core --cov=engines
```

## Test Coverage

Unit tests focus on:
- Individual function correctness
- Edge cases and error handling
- Configuration validation
- Data structure integrity
