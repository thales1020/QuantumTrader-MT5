# API Testing Guide - Paper Trading Broker

**Version**: 1.1  
**Date**: January 2025  
**For**: Independent Testers  
**Purpose**: How to correctly test PaperTradingBrokerAPI

---

## NEW: Test Helper Functions Available!

**RECOMMENDED**: Use the test helpers to write cleaner, faster tests!

```python
from tests.helpers import (
    create_test_broker,           # Create broker with temp DB
    submit_and_fill_order,        # Submit + fill in one call
    create_position_with_sl_tp,   # Create position with SL/TP
    trigger_stop_loss,            # Trigger SL automatically
    trigger_take_profit,          # Trigger TP automatically
    get_last_trade,              # Get most recent trade
    assert_position_has_sl_tp    # Assert SL/TP values
)

# Example - Test in 5 lines instead of 50:
broker = create_test_broker()
success, pos_id, _ = create_position_with_sl_tp(broker, stop_loss=1.0950)
closed = trigger_stop_loss(broker, pos_id)
assert closed is True
assert get_last_trade(broker)['pnl'] < 0  # Hit SL = loss
```

**See**: `tests/test_with_helpers_example.py` for complete examples

---

## CRITICAL: Read Implementation First

Before writing ANY tests, you MUST understand the actual implementation.

### Common Mistakes to Avoid

1. DO NOT assume class structure - READ THE CODE
2. DO NOT use made-up attributes - VERIFY THEY EXIST
3. DO NOT create test objects blindly - CHECK ACTUAL CONSTRUCTORS
4. DO NOT copy-paste test templates - UNDERSTAND THE API
5. **USE TEST HELPERS** - They prevent common mistakes

---

## Understanding PaperTradingBrokerAPI

### Architecture Overview

The `PaperTradingBrokerAPI` uses TWO different Order classes:

#### 1. Order Matching Engine Order
**File**: `engines/order_matching_engine.py`  
**Class**: `Order`

```python
from engines.order_matching_engine import Order, OrderType, OrderSide

# Attributes:
order = Order(
    order_id="ORD_001",
    symbol="EURUSD",
    order_type=OrderType.MARKET,  # ENUM, not string
    side=OrderSide.BUY,           # ENUM, not string
    quantity=0.1,                  # NOT 'volume' or 'lot_size'
    limit_price=None,              # For LIMIT orders
    stop_price=None,               # For STOP orders
    time_in_force=TimeInForce.GTC
)
```

**IMPORTANT**:
- Use `quantity` NOT `volume` or `lot_size`
- Use `side` (OrderSide enum) NOT `order_type` string
- Use `OrderType.MARKET` NOT `"MARKET"`

#### 2. Broker Simulator Order
**File**: `engines/broker_simulator.py`  
**Class**: `Order`

```python
from engines.broker_simulator import Order, OrderType

# Attributes:
order = Order(
    order_id="ORD_001",
    symbol="EURUSD",
    direction=0,              # 0=BUY, 1=SELL (int, not string)
    lot_size=0.1,             # NOT 'quantity' or 'volume'
    requested_price=1.1000,
    order_type=OrderType.MARKET
)
```

**IMPORTANT**:
- Use `lot_size` NOT `quantity` or `volume`
- Use `direction` (int: 0 or 1) NOT `side` or string
- Use `requested_price` NOT `limit_price` or `entry_price`

---

## API Attributes Reference

### What EXISTS in PaperTradingBrokerAPI

```python
broker = PaperTradingBrokerAPI()

# CORRECT - These exist:
broker.balance                    # float
broker.initial_balance            # float
broker.equity                     # float
broker.positions                  # Dict[str, Position]
broker.orders                     # Dict[str, Order] - NEW! Returns pending_orders
broker.trade_history             # List
broker.matching_engine           # OrderMatchingEngine
broker.database                  # DatabaseManager

# CORRECT - Access pending orders (two ways):
broker.orders                              # Recommended - clean API
broker.matching_engine.pending_orders      # Also works - direct access

# WRONG - These DO NOT exist:
broker.open_positions            # Use broker.positions instead
broker.trades                    # Use broker.trade_history instead
```

### API Reference

**Available Properties & Methods**:
```python
broker = PaperTradingBrokerAPI()

# Properties:
broker.balance                    # float - Current account balance
broker.initial_balance            # float - Starting balance
broker.equity                     # float - Account equity
broker.positions                  # Dict[str, Position] - Active positions
broker.orders                     # Dict[str, Order] - Pending orders (NEW!)
broker.trade_history             # List[Dict] - Completed trades
broker.matching_engine           # OrderMatchingEngine - Internal engine
broker.database                  # DatabaseManager - Trade database

# Methods:
success, order_id, error = broker.submit_order(...)  # Returns TUPLE!
broker.update(symbol, bar)                           # Update prices
broker.close_position(position_id)                  # Manual close
broker.cancel_order(order_id)                       # Cancel pending order
```

**IMPORTANT - Return Values**:
- `submit_order()` returns `(success: bool, order_id: str, error: str)`
- Do NOT treat return value as string!
- Always unpack: `success, order_id, error = broker.submit_order(...)`

---

## How to Write Correct Tests

### Step 1: Import Correctly

```python
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

# Mock MT5 BEFORE importing broker
import sys
sys.modules['MetaTrader5'] = MagicMock()

# Now import
from engines.paper_trading_broker_api import PaperTradingBrokerAPI
from engines.order_matching_engine import (
    Order, OrderType, OrderSide, TimeInForce
)
from engines.broker_simulator import Position
```

### Step 2: Create Test Broker

```python
@pytest.fixture
def broker():
    """Create test broker instance"""
    return PaperTradingBrokerAPI(
        initial_balance=10000.0,
        auto_update=False  # Disable background updates in tests
    )
```

### Step 3: Submit Orders Correctly

**CRITICAL**: `submit_order()` returns a **TUPLE**, not a string!

```python
def test_submit_market_order(broker):
    """Test submitting a market order - CORRECT VERSION"""
    
    # Correct: Unpack the tuple
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",    # String is OK for API
        side="BUY",             # String is OK for API
        quantity=0.1,           # Use quantity
        stop_loss=1.0950,       # Optional
        take_profit=1.1100      # Optional
    )
    
    # Check success
    assert success is True, f"Order failed: {error}"
    assert order_id is not None
    assert order_id.startswith("ORD_")
    assert error is None
```

**WRONG WAY** (what Tester #1 & #2 did):
```python
# WRONG - Treats return value as string:
order_id = broker.submit_order(...)  # Gets tuple, not string!
assert order_id.startswith("ORD_")  # AttributeError: tuple has no startswith
```

---

## Real Working Examples

### Example 1: Submit Market Order and Check Position

```python
def test_market_order_creates_position():
    """Complete example: Market order → Position created"""
    
    # Step 1: Create broker
    broker = PaperTradingBrokerAPI(initial_balance=10000.0)
    
    # Step 2: Submit market order
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,
        take_profit=1.1100
    )
    
    # Step 3: Verify order submitted
    assert success is True, f"Order failed: {error}"
    
    # Step 4: Simulate price feed to fill order
    bar = {
        'time': datetime.now(),
        'open': 1.1000,
        'high': 1.1010,
        'low': 1.0990,
        'close': 1.1000,
        'volume': 1000,
        'bid': 1.0999,
        'ask': 1.1001
    }
    broker.update("EURUSD", bar)
    
    # Step 5: Check position created
    assert len(broker.positions) == 1
    
    position = list(broker.positions.values())[0]
    assert position.symbol == "EURUSD"
    assert position.lot_size == 0.1
    assert position.stop_loss == 1.0950
    assert position.take_profit == 1.1100
    assert position.direction == 0  # BUY
```

### Example 2: Test Stop Loss Auto-Close

```python
def test_stop_loss_auto_closes_position():
    """Complete example: Position → SL hit → Auto-close"""
    
    # Setup: Create position
    broker = PaperTradingBrokerAPI(initial_balance=10000.0)
    
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950  # SL at 1.0950
    )
    
    # Fill order at 1.1000
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.1000, 'high': 1.1000, 'low': 1.1000, 'close': 1.1000,
        'volume': 1000, 'bid': 1.0999, 'ask': 1.1001
    })
    
    assert len(broker.positions) == 1  # Position created
    position_id = list(broker.positions.keys())[0]
    
    # Price drops below SL
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.0945,  # Below SL!
        'high': 1.0945,
        'low': 1.0940,
        'close': 1.0945,
        'volume': 1000,
        'bid': 1.0944,
        'ask': 1.0946
    })
    
    # Position should auto-close
    assert len(broker.positions) == 0, "Position should be closed by SL"
    assert len(broker.trade_history) == 1, "Trade should be in history"
    
    # Check P&L
    trade = broker.trade_history[0]
    assert trade['exit_price'] <= 1.0950  # Closed at or below SL
    assert trade['pnl'] < 0  # Loss (price went down)
```

### Example 3: Check Pending Orders

```python
def test_check_pending_limit_order():
    """Complete example: Submit limit order → Check it's pending"""
    
    broker = PaperTradingBrokerAPI(initial_balance=10000.0)
    
    # Submit LIMIT order (won't fill immediately)
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="LIMIT",
        side="BUY",
        quantity=0.1,
        limit_price=1.0950  # Only fill at 1.0950 or better
    )
    
    assert success is True
    
    # Check order is pending (NEW API - clean!)
    assert len(broker.orders) == 1
    assert order_id in broker.orders
    
    order = broker.orders[order_id]
    assert order.symbol == "EURUSD"
    assert order.quantity == 0.1
    
    # Price at 1.1000 - order should NOT fill
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.1000, 'high': 1.1000, 'low': 1.1000, 'close': 1.1000,
        'volume': 1000, 'bid': 1.0999, 'ask': 1.1001
    })
    
    assert len(broker.orders) == 1  # Still pending
    assert len(broker.positions) == 0  # Not filled
    
    # Price drops to 1.0950 - order should fill
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.0950, 'high': 1.0950, 'low': 1.0950, 'close': 1.0950,
        'volume': 1000, 'bid': 1.0949, 'ask': 1.0951
    })
    
    assert len(broker.orders) == 0  # Order filled
    assert len(broker.positions) == 1  # Position created
```

### Example 4: Calculate P&L with Costs

```python
def test_pnl_calculation_with_costs():
    """Complete example: Full trade cycle with P&L calculation"""
    
    broker = PaperTradingBrokerAPI(initial_balance=10000.0)
    initial_balance = broker.balance
    
    # Open position
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1  # 0.1 lots = 10,000 units
    )
    
    # Fill at 1.1000
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.1000, 'high': 1.1000, 'low': 1.1000, 'close': 1.1000,
        'volume': 1000, 'bid': 1.0999, 'ask': 1.1001
    })
    
    position_id = list(broker.positions.keys())[0]
    
    # Close position at 1.1100 (100 pips profit)
    success, close_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="SELL",
        quantity=0.1
    )
    
    broker.update("EURUSD", {
        'time': datetime.now(),
        'open': 1.1100, 'high': 1.1100, 'low': 1.1100, 'close': 1.1100,
        'volume': 1000, 'bid': 1.1099, 'ask': 1.1101
    })
    
    # Check P&L calculation
    assert len(broker.positions) == 0  # Position closed
    assert len(broker.trade_history) == 1
    
    trade = broker.trade_history[0]
    
    # Gross P&L = (1.1100 - 1.1000) * 10,000 units = $100
    assert trade['gross_pnl'] == pytest.approx(100.0, abs=1.0)
    
    # Net P&L = Gross - (commission + swap + spread)
    # Should be slightly less than $100 due to costs
    assert trade['pnl'] < trade['gross_pnl']
    assert trade['pnl'] > 95.0  # Still profitable
    
    # Balance should increase
    assert broker.balance > initial_balance
    assert broker.balance == pytest.approx(initial_balance + trade['pnl'], abs=0.01)
```

---

## Step 4: Check Positions Correctly

```python
def test_position_creation(broker):
    """Test position is created after order fill"""
    
    # Submit order
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950
    )
    
    # Simulate market data to fill order
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    # Check position created
    assert len(broker.positions) > 0
    
    position = list(broker.positions.values())[0]
    assert position.symbol == "EURUSD"
    assert position.lot_size == 0.1
    assert position.stop_loss == 1.0950
```

---

## Testing the 3 Critical Fixes

### Fix #1: SL/TP Extraction from Orders

**What to test**: Orders with SL/TP create positions with SL/TP

```python
def test_sl_tp_extraction_from_order(broker):
    """Test SL/TP values are extracted from order to position"""
    
    # Submit order with SL/TP
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,
        take_profit=1.1100
    )
    
    # Fill the order
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    # Verify position has SL/TP
    position = list(broker.positions.values())[0]
    
    # THESE SHOULD PASS NOW (after fix):
    assert position.stop_loss == 1.0950
    assert position.take_profit == 1.1100
```

### Fix #2: SL/TP Monitoring and Auto-Close

**What to test**: Positions auto-close when price hits SL/TP

```python
def test_stop_loss_triggers_auto_close(broker):
    """Test position auto-closes when SL is hit"""
    
    # Create position
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,
        take_profit=1.1100
    )
    
    # Fill at 1.1000
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    
    # Simulate price drop to hit SL
    bar = {
        'time': datetime.now(),
        'open': 1.0980,
        'high': 1.0990,
        'low': 1.0940,   # Below SL (1.0950)
        'close': 1.0960,
        'volume': 100
    }
    
    # Update positions with this bar
    broker._update_positions("EURUSD", bar)
    
    # SHOULD PASS NOW (after fix):
    # Position should be auto-closed
    assert position_id not in broker.positions
    
    # Trade should be saved
    assert len(broker.trade_history) > 0
    
    # Exit reason should be "Stop Loss"
    trade = broker.trade_history[-1]
    assert trade.exit_reason == "Stop Loss"
```

```python
def test_take_profit_triggers_auto_close(broker):
    """Test position auto-closes when TP is hit"""
    
    # Create position
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,
        take_profit=1.1100
    )
    
    # Fill at 1.1000
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    
    # Simulate price rise to hit TP
    bar = {
        'time': datetime.now(),
        'open': 1.1050,
        'high': 1.1110,  # Above TP (1.1100)
        'low': 1.1040,
        'close': 1.1080,
        'volume': 100
    }
    
    broker._update_positions("EURUSD", bar)
    
    # SHOULD PASS NOW (after fix):
    assert position_id not in broker.positions
    assert len(broker.trade_history) > 0
    
    trade = broker.trade_history[-1]
    assert trade.exit_reason == "Take Profit"
    assert trade.net_pnl > 0  # Should be profitable
```

### Fix #3: P&L Calculation

**What to test**: P&L calculated correctly with all costs

```python
def test_pnl_calculation_accuracy(broker):
    """Test P&L calculation includes all costs"""
    
    # Create position
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1
    )
    
    # Fill at 1.1000
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    
    # Close at 1.1050 (+50 pips)
    initial_balance = broker.balance
    
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1050):
        broker.close_position(position_id)
    
    # SHOULD PASS NOW (after fix):
    trade = broker.trade_history[-1]
    
    # Verify P&L components exist
    assert hasattr(trade, 'gross_pnl')
    assert hasattr(trade, 'net_pnl')
    assert hasattr(trade, 'commission')
    assert hasattr(trade, 'swap')
    
    # Gross P&L = (1.1050 - 1.1000) * 0.1 * 100,000 = $500
    expected_gross = 0.0050 * 0.1 * 100000
    assert abs(trade.gross_pnl - expected_gross) < 5  # Within $5
    
    # Net P&L = Gross - Costs
    expected_net = trade.gross_pnl - trade.commission - trade.swap
    assert abs(trade.net_pnl - expected_net) < 0.01  # Within 1 cent
    
    # Balance should increase by Net P&L
    final_balance = broker.balance
    balance_change = final_balance - initial_balance
    assert abs(balance_change - trade.net_pnl) < 0.01
```

---

## Common Test Patterns

### Pattern 1: Testing with Mocked MT5

```python
def test_with_mocked_mt5(broker):
    """Example of mocking MT5 data"""
    
    # Mock symbol info
    mock_symbol_info = Mock()
    mock_symbol_info.point = 0.0001
    mock_symbol_info.digits = 5
    
    # Mock tick data
    mock_tick = Mock()
    mock_tick.bid = 1.1000
    mock_tick.ask = 1.1002
    mock_tick.time = int(datetime.now().timestamp())
    
    with patch('MetaTrader5.symbol_info', return_value=mock_symbol_info):
        with patch('MetaTrader5.symbol_info_tick', return_value=mock_tick):
            # Your test code here
            pass
```

### Pattern 2: Testing Database Integration

```python
def test_trade_saved_to_database(broker):
    """Test trades are saved to database"""
    
    # Execute a trade
    order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)
    
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    broker.close_position(position_id)
    
    # Query database
    trades = broker.database.get_all_trades()
    
    assert len(trades) > 0
    last_trade = trades[-1]
    assert last_trade.symbol == "EURUSD"
```

### Pattern 3: Testing Edge Cases

```python
def test_zero_lot_size_rejected(broker):
    """Test that zero lot size is rejected"""
    
    with pytest.raises(ValueError):
        broker.submit_order("EURUSD", "MARKET", "BUY", 0.0)

def test_negative_lot_size_rejected(broker):
    """Test that negative lot size is rejected"""
    
    with pytest.raises(ValueError):
        broker.submit_order("EURUSD", "MARKET", "BUY", -0.1)

def test_invalid_symbol_rejected(broker):
    """Test that invalid symbol is rejected"""
    
    with pytest.raises(ValueError):
        broker.submit_order("INVALID", "MARKET", "BUY", 0.1)
```

---

## Debugging Failed Tests

### Problem: AttributeError

```
AttributeError: 'PaperTradingBrokerAPI' object has no attribute 'orders'
```

**Solution**: Use `broker.matching_engine.pending_orders`

### Problem: TypeError on Order creation

```
TypeError: Order.__init__() got an unexpected keyword argument 'volume'
```

**Solution**: 
- For OME Order: Use `quantity` not `volume`
- For BrokerSim Order: Use `lot_size` not `volume`

### Problem: Test passes locally but fails in CI

**Common causes**:
- MT5 not mocked properly
- Database path issues
- Timezone differences
- Random number generation (slippage)

**Solution**: 
- Always mock MT5
- Use in-memory database for tests
- Use UTC for all timestamps
- Seed random number generator

---

## Coverage Analysis

### How to Run Coverage

```bash
pytest tests/unit/test_paper_trading_broker.py --cov=engines.paper_trading_broker_api --cov-report=html
```

### Target Coverage

- Critical methods: 100%
  - `submit_order()`
  - `_create_position_from_fill()`
  - `_update_positions()`
  - `_close_position_internal()`

- Important methods: 95%+
  - All public API methods
  - All position management

- Other methods: 80%+

---

## Example: Complete Test Class

```python
class TestSLTPFunctionality:
    """Complete test class for SL/TP functionality"""
    
    @pytest.fixture
    def broker(self):
        """Create test broker"""
        return PaperTradingBrokerAPI(
            initial_balance=10000.0,
            auto_update=False
        )
    
    def test_sl_extraction(self, broker):
        """Test SL is extracted from order"""
        order_id = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950
        )
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position = list(broker.positions.values())[0]
        assert position.stop_loss == 1.0950
    
    def test_tp_extraction(self, broker):
        """Test TP is extracted from order"""
        order_id = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            take_profit=1.1100
        )
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position = list(broker.positions.values())[0]
        assert position.take_profit == 1.1100
    
    def test_sl_triggers_close(self, broker):
        """Test SL triggers auto-close"""
        # Create position
        order_id = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950
        )
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position_id = list(broker.positions.keys())[0]
        
        # Hit SL
        bar = {
            'time': datetime.now(),
            'open': 1.0980,
            'high': 1.0990,
            'low': 1.0940,
            'close': 1.0960,
            'volume': 100
        }
        
        broker._update_positions("EURUSD", bar)
        
        assert position_id not in broker.positions
        assert len(broker.trade_history) > 0
    
    def test_tp_triggers_close(self, broker):
        """Test TP triggers auto-close"""
        # Similar to SL test but with TP
        pass
    
    def test_pnl_calculation(self, broker):
        """Test P&L is calculated correctly"""
        # Create and close position
        # Verify P&L components
        pass
```

---

## Checklist Before Submitting Tests

- [ ] Read the actual implementation code
- [ ] Verified all attributes exist
- [ ] Used correct Order class for context
- [ ] Mocked MT5 properly
- [ ] Tests run independently (no shared state)
- [ ] Cleaned up resources (database, files)
- [ ] Added docstrings to all tests
- [ ] Tested edge cases
- [ ] Ran coverage analysis
- [ ] All tests pass locally

---

## Getting Help

### If tests fail:

1. Read the error message carefully
2. Check if attribute/method exists in actual code
3. Verify you're using correct class structure
4. Check mocking is correct
5. Print debug info (actual vs expected)

### If coverage is low:

1. Identify uncovered lines in HTML report
2. Write tests for those specific lines
3. Focus on critical paths first
4. Edge cases can come later

### If confused:

1. Read this guide again
2. Read the actual implementation code
3. Look at existing working tests
4. Ask for clarification with specific examples

---

**Good luck with testing!**

Remember: **READ THE CODE FIRST** before writing tests!
