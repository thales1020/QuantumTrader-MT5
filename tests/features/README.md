# Feature Tests

Tests for specific features and capabilities of the trading system.

## Files

### Cryptocurrency Trading
- `test_crypto_import.py` - Crypto module import tests
- `test_crypto_orders.py` - Crypto order handling
- `test_crypto_trading.py` - Full crypto trading workflow

### Plugin System
- `test_plugin_integration.py` - Plugin integration tests
- `test_plugin_system.py` - Plugin system core functionality

### Templates & Helpers
- `test_template_system.py` - Strategy template system
- `test_with_helpers_example.py` - Test helper usage examples

## Running Feature Tests

```bash
# Run all feature tests
pytest tests/features/

# Run crypto tests only
pytest tests/features/test_crypto_*.py

# Run plugin tests only
pytest tests/features/test_plugin_*.py

# Run specific test
pytest tests/features/test_template_system.py
```

## Test Categories

### Crypto Trading Tests
Focus on cryptocurrency-specific functionality:
- Symbol handling (BTCUSDm, ETHUSDm, etc.)
- Dual order system (long + short simultaneously)
- Crypto-specific risk management
- Market data handling

### Plugin System Tests
Verify plugin architecture:
- Plugin discovery and loading
- Plugin lifecycle management
- Plugin configuration
- Plugin integration with core system

### Template System Tests
Validate strategy template system:
- Template loading and parsing
- Parameter validation
- Strategy instantiation from templates
- Template error handling

## Requirements

- All project dependencies installed
- Test fixtures available
- Mock MT5 data (if not testing with real MT5)

## Notes

💡 **Tip**: Feature tests are independent and can run without MT5 connection.

✅ **Best Practice**: Run feature tests frequently during development to catch regressions early.
