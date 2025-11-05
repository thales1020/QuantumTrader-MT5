# Quick Reference - Paper Trading Broker API

**Last Updated**: November 5, 2025  
**For**: Testers who need quick answers

---

## API Attributes Quick Lookup

### What EXISTS

```python
broker = PaperTradingBrokerAPI()

# Account
broker.balance                           # Current balance
broker.initial_balance                   # Starting balance
broker.equity                            # Current equity

# Positions
broker.positions                         # Dict[str, Position]
len(broker.positions)                    # Number of open positions

# Orders (CAREFUL!)
broker.matching_engine.pending_orders    # Dict[str, Order] - USE THIS
# broker.orders                          # DOES NOT EXIST (Bug #2)

# Trade History
broker.trade_history                     # List[Trade]

# Database
broker.database                          # DatabaseManager instance
```

### What DOES NOT EXIST

```python
# These will throw AttributeError:
broker.orders                            # Use matching_engine.pending_orders
broker.open_positions                    # Use broker.positions
broker.trades                            # Use broker.trade_history
broker.account_info                      # Use individual attributes
```

---

## Order Class Quick Reference

### Order Matching Engine Order (PUBLIC API)

**Use when**: Submitting orders via API

```python
# Via API (recommended):
order_id = broker.submit_order(
    symbol="EURUSD",        # String
    order_type="MARKET",    # String: "MARKET", "LIMIT", "STOP"
    side="BUY",             # String: "BUY", "SELL"
    quantity=0.1,           # Float (lot size)
    stop_loss=1.0950,       # Optional float
    take_profit=1.1100      # Optional float
)

# Direct class (for internal testing):
from engines.order_matching_engine import Order, OrderType, OrderSide

order = Order(
    order_id="ORD_001",
    symbol="EURUSD",
    order_type=OrderType.MARKET,    # ENUM
    side=OrderSide.BUY,             # ENUM
    quantity=0.1,                   # NOT volume/lot_size
    limit_price=None,
    stop_price=None
)
```

### Broker Simulator Order (INTERNAL)

**Use when**: Testing broker internals

```python
from engines.broker_simulator import Order, OrderType

order = Order(
    order_id="ORD_001",
    symbol="EURUSD",
    direction=0,              # 0=BUY, 1=SELL (int)
    lot_size=0.1,             # NOT quantity/volume
    requested_price=1.1000,
    order_type=OrderType.MARKET
)
```

---

## Position Attributes

```python
position = broker.positions[position_id]

# Position details
position.position_id        # String
position.symbol            # String
position.direction         # "BUY" or "SELL"
position.lot_size          # Float
position.entry_price       # Float
position.current_price     # Float
position.stop_loss         # Float or None
position.take_profit       # Float or None

# P&L
position.unrealized_pnl    # Float (updated on each bar)
position.realized_pnl      # Float (when closed)
position.net_pnl          # Float (gross - costs)

# Timing
position.open_time         # datetime
position.exit_time         # datetime or None

# Costs
position.total_commission  # Float
position.total_swap        # Float
```

---

## Trade Attributes

```python
trade = broker.trade_history[-1]

# Trade details
trade.trade_id             # String
trade.symbol              # String
trade.direction           # "BUY" or "SELL"
trade.lot_size            # Float

# Prices
trade.entry_price         # Float
trade.exit_price          # Float

# Timing
trade.entry_time          # datetime
trade.exit_time           # datetime

# P&L
trade.gross_pnl           # Float (before costs)
trade.net_pnl             # Float (after costs)

# Costs
trade.commission          # Float
trade.swap               # Float

# Metadata
trade.exit_reason         # String: "Stop Loss", "Take Profit", "Manual"
```

---

## Common Test Patterns

### Pattern: Submit and Fill Order

```python
# Submit
order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)

# Mock price and fill
with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
    broker._process_pending_orders()

# Verify
assert len(broker.positions) == 1
```

### Pattern: Trigger Stop Loss

```python
# Create position with SL
order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1, stop_loss=1.0950)

with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
    broker._process_pending_orders()

position_id = list(broker.positions.keys())[0]

# Hit SL with bar
bar = {
    'time': datetime.now(),
    'open': 1.0980,
    'high': 1.0990,
    'low': 1.0940,    # Below SL
    'close': 1.0960,
    'volume': 100
}

broker._update_positions("EURUSD", bar)

# Verify closed
assert position_id not in broker.positions
```

### Pattern: Trigger Take Profit

```python
# Create position with TP
order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1, take_profit=1.1100)

with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
    broker._process_pending_orders()

position_id = list(broker.positions.keys())[0]

# Hit TP with bar
bar = {
    'time': datetime.now(),
    'open': 1.1050,
    'high': 1.1110,   # Above TP
    'low': 1.1040,
    'close': 1.1080,
    'volume': 100
}

broker._update_positions("EURUSD", bar)

# Verify closed
assert position_id not in broker.positions
assert len(broker.trade_history) > 0
```

### Pattern: Verify P&L Calculation

```python
# Create and close position
order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)

with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
    broker._process_pending_orders()

position_id = list(broker.positions.keys())[0]

initial_balance = broker.balance

# Close at +50 pips
with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1050):
    broker.close_position(position_id)

trade = broker.trade_history[-1]

# Verify
expected_gross = 0.0050 * 0.1 * 100000  # $500
assert abs(trade.gross_pnl - expected_gross) < 5

final_balance = broker.balance
assert abs((final_balance - initial_balance) - trade.net_pnl) < 0.01
```

---

## Mock MT5 Template

```python
import sys
from unittest.mock import MagicMock, Mock, patch

# Mock MT5 module
sys.modules['MetaTrader5'] = MagicMock()

# Mock symbol info
mock_symbol_info = Mock()
mock_symbol_info.point = 0.0001
mock_symbol_info.digits = 5

# Mock tick
mock_tick = Mock()
mock_tick.bid = 1.1000
mock_tick.ask = 1.1002
mock_tick.time = int(datetime.now().timestamp())

# Use in test
with patch('MetaTrader5.symbol_info', return_value=mock_symbol_info):
    with patch('MetaTrader5.symbol_info_tick', return_value=mock_tick):
        # Your test code
        pass
```

---

## Pytest Fixture Template

```python
import pytest

@pytest.fixture
def broker():
    """Create test broker instance"""
    return PaperTradingBrokerAPI(
        initial_balance=10000.0,
        auto_update=False  # Important for testing!
    )

@pytest.fixture
def filled_position(broker):
    """Create a filled position for testing"""
    order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)
    
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    return broker, position_id
```

---

## Coverage Command

```bash
# Basic coverage
pytest tests/unit/test_paper_trading_broker.py --cov=engines.paper_trading_broker_api

# With HTML report
pytest tests/unit/test_paper_trading_broker.py \
  --cov=engines.paper_trading_broker_api \
  --cov-report=html

# Open report
# Windows: start htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

---

## Common Errors and Fixes

### Error: AttributeError: 'PaperTradingBrokerAPI' object has no attribute 'orders'

**Fix**: Use `broker.matching_engine.pending_orders`

### Error: TypeError: Order.__init__() got an unexpected keyword argument 'volume'

**Fix**: Use `quantity` (OME Order) or `lot_size` (BrokerSim Order)

### Error: AssertionError: assert 0 == 1

**Fix**: Position count is 0. Did you call `_process_pending_orders()`?

### Error: KeyError: 'POS_001'

**Fix**: Position already closed. Check if SL/TP auto-closed it.

---

## Test Execution Checklist

Before running tests:
- [ ] MT5 mocked properly
- [ ] Database path set correctly (or in-memory)
- [ ] `auto_update=False` in broker init
- [ ] All imports correct

When test fails:
- [ ] Read error message completely
- [ ] Check attribute exists in actual code
- [ ] Verify correct Order class used
- [ ] Print actual values for debugging

After tests pass:
- [ ] Run coverage report
- [ ] Check coverage of critical methods
- [ ] Add edge case tests
- [ ] Clean up test files/database

---

## Need More Help?

1. Read `docs/API_TESTING_GUIDE.md` (full guide)
2. Read actual code in `engines/paper_trading_broker_api.py`
3. Check existing tests in `tests/unit/`
4. Ask with specific code example

---

**Remember: READ THE CODE FIRST!**
