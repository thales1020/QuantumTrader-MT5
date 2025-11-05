"""
Test Helper Functions for Paper Trading Tests

This module provides factory functions and utilities to simplify
test writing and reduce code duplication.

Created: 2025-01-XX (Bug Fix #4 from Tester #3 feedback)
"""

import tempfile
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from unittest.mock import MagicMock
import sys

# Mock MT5 before any imports
if 'MetaTrader5' not in sys.modules:
    sys.modules['MetaTrader5'] = MagicMock()

from engines.paper_trading_broker_api import PaperTradingBrokerAPI


def create_test_broker(
    initial_balance: float = 10000.0,
    auto_update: bool = False,
    use_temp_db: bool = True
) -> PaperTradingBrokerAPI:
    """
    Create a PaperTradingBrokerAPI instance for testing
    
    Args:
        initial_balance: Starting account balance (default: 10000.0)
        auto_update: Enable background updates (default: False for tests)
        use_temp_db: Use temporary database file (default: True)
    
    Returns:
        PaperTradingBrokerAPI instance configured for testing
    
    Example:
        >>> broker = create_test_broker(initial_balance=5000.0)
        >>> assert broker.balance == 5000.0
    """
    if use_temp_db:
        # Create temporary database to avoid conflicts
        temp_db = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.db',
            delete=False,
            prefix='test_paper_trading_'
        )
        temp_db.close()
        
        # Store for cleanup later
        broker = PaperTradingBrokerAPI(
            initial_balance=initial_balance,
            auto_update=auto_update
        )
        broker._test_db_path = temp_db.name
        
        return broker
    else:
        return PaperTradingBrokerAPI(
            initial_balance=initial_balance,
            auto_update=auto_update
        )


def cleanup_test_broker(broker: PaperTradingBrokerAPI):
    """
    Clean up test broker resources (database files, etc.)
    
    Args:
        broker: The broker instance to clean up
    
    Example:
        >>> broker = create_test_broker()
        >>> # ... run tests ...
        >>> cleanup_test_broker(broker)
    """
    # Remove temporary database if exists
    if hasattr(broker, '_test_db_path'):
        try:
            os.unlink(broker._test_db_path)
        except (OSError, FileNotFoundError):
            pass


def create_bar(
    symbol: str = "EURUSD",
    price: float = 1.1000,
    spread: float = 0.0002,
    volume: int = 1000,
    time: Optional[datetime] = None
) -> Dict:
    """
    Create a price bar for testing
    
    Args:
        symbol: Trading symbol (not used in bar, but helpful for context)
        price: Mid price (default: 1.1000)
        spread: Bid-Ask spread (default: 0.0002 = 2 pips)
        volume: Trading volume (default: 1000)
        time: Bar timestamp (default: datetime.now())
    
    Returns:
        Dictionary with OHLCV + bid/ask data
    
    Example:
        >>> bar = create_bar(price=1.1000)
        >>> assert bar['close'] == 1.1000
        >>> assert bar['ask'] - bar['bid'] == 0.0002
    """
    if time is None:
        time = datetime.now()
    
    half_spread = spread / 2
    
    return {
        'time': time,
        'open': price,
        'high': price + 0.0010,  # 10 pips above
        'low': price - 0.0010,   # 10 pips below
        'close': price,
        'volume': volume,
        'bid': price - half_spread,
        'ask': price + half_spread
    }


def submit_and_fill_order(
    broker: PaperTradingBrokerAPI,
    symbol: str = "EURUSD",
    side: str = "BUY",
    quantity: float = 0.1,
    fill_price: float = 1.1000,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> Tuple[bool, str, Optional[str], str]:
    """
    Submit a market order and immediately fill it
    
    This is a common pattern in tests: submit order → update price → check position
    This helper combines those steps.
    
    Args:
        broker: PaperTradingBrokerAPI instance
        symbol: Trading symbol (default: "EURUSD")
        side: "BUY" or "SELL" (default: "BUY")
        quantity: Position size in lots (default: 0.1)
        fill_price: Price to fill order at (default: 1.1000)
        stop_loss: Stop loss price (optional)
        take_profit: Take profit price (optional)
    
    Returns:
        Tuple of (success, order_id, error, position_id)
        - success: True if order submitted and filled
        - order_id: Order ID from submission
        - error: Error message if any
        - position_id: Created position ID (or None if failed)
    
    Example:
        >>> broker = create_test_broker()
        >>> success, order_id, error, position_id = submit_and_fill_order(
        ...     broker=broker,
        ...     side="BUY",
        ...     quantity=0.1,
        ...     fill_price=1.1000,
        ...     stop_loss=1.0950
        ... )
        >>> assert success is True
        >>> assert position_id in broker.positions
    """
    # Submit order
    success, order_id, error = broker.submit_order(
        symbol=symbol,
        order_type="MARKET",
        side=side,
        quantity=quantity,
        stop_loss=stop_loss,
        take_profit=take_profit
    )
    
    if not success:
        return success, order_id, error, None
    
    # Create bar at fill price
    bar = create_bar(symbol=symbol, price=fill_price)
    
    # Update broker to fill order
    broker.update(symbol, bar)
    
    # Find created position
    position_id = None
    for pos_id, pos in broker.positions.items():
        if pos.symbol == symbol:
            position_id = pos_id
            break
    
    return success, order_id, error, position_id


def create_position_with_sl_tp(
    broker: PaperTradingBrokerAPI,
    symbol: str = "EURUSD",
    side: str = "BUY",
    quantity: float = 0.1,
    entry_price: float = 1.1000,
    stop_loss: float = 1.0950,
    take_profit: float = 1.1100
) -> Tuple[bool, str, Optional[str]]:
    """
    Create a position with Stop Loss and Take Profit
    
    This is the most common test pattern for SL/TP tests.
    
    Args:
        broker: PaperTradingBrokerAPI instance
        symbol: Trading symbol (default: "EURUSD")
        side: "BUY" or "SELL" (default: "BUY")
        quantity: Position size in lots (default: 0.1)
        entry_price: Entry price (default: 1.1000)
        stop_loss: Stop loss price (default: 1.0950)
        take_profit: Take profit price (default: 1.1100)
    
    Returns:
        Tuple of (success, position_id, error)
    
    Example:
        >>> broker = create_test_broker()
        >>> success, position_id, error = create_position_with_sl_tp(
        ...     broker=broker,
        ...     entry_price=1.1000,
        ...     stop_loss=1.0950,
        ...     take_profit=1.1100
        ... )
        >>> position = broker.positions[position_id]
        >>> assert position.stop_loss == 1.0950
        >>> assert position.take_profit == 1.1100
    """
    success, order_id, error, position_id = submit_and_fill_order(
        broker=broker,
        symbol=symbol,
        side=side,
        quantity=quantity,
        fill_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit
    )
    
    return success, position_id, error


def trigger_stop_loss(
    broker: PaperTradingBrokerAPI,
    position_id: str,
    trigger_price: Optional[float] = None
) -> bool:
    """
    Trigger stop loss for a position
    
    Args:
        broker: PaperTradingBrokerAPI instance
        position_id: Position to trigger SL for
        trigger_price: Price to trigger at (default: use position's SL)
    
    Returns:
        True if position was closed, False otherwise
    
    Example:
        >>> broker = create_test_broker()
        >>> success, pos_id, _ = create_position_with_sl_tp(
        ...     broker=broker, entry_price=1.1000, stop_loss=1.0950
        ... )
        >>> closed = trigger_stop_loss(broker, pos_id)
        >>> assert closed is True
        >>> assert pos_id not in broker.positions
    """
    if position_id not in broker.positions:
        return False
    
    position = broker.positions[position_id]
    
    if trigger_price is None:
        trigger_price = position.stop_loss
    
    if trigger_price is None:
        raise ValueError("Position has no stop_loss and no trigger_price provided")
    
    # Create bar that triggers SL
    bar = create_bar(
        symbol=position.symbol,
        price=trigger_price - 0.0005  # 5 pips below SL to ensure trigger
    )
    
    broker.update(position.symbol, bar)
    
    # Check if position closed
    return position_id not in broker.positions


def trigger_take_profit(
    broker: PaperTradingBrokerAPI,
    position_id: str,
    trigger_price: Optional[float] = None
) -> bool:
    """
    Trigger take profit for a position
    
    Args:
        broker: PaperTradingBrokerAPI instance
        position_id: Position to trigger TP for
        trigger_price: Price to trigger at (default: use position's TP)
    
    Returns:
        True if position was closed, False otherwise
    
    Example:
        >>> broker = create_test_broker()
        >>> success, pos_id, _ = create_position_with_sl_tp(
        ...     broker=broker, entry_price=1.1000, take_profit=1.1100
        ... )
        >>> closed = trigger_take_profit(broker, pos_id)
        >>> assert closed is True
        >>> assert len(broker.trade_history) == 1
    """
    if position_id not in broker.positions:
        return False
    
    position = broker.positions[position_id]
    
    if trigger_price is None:
        trigger_price = position.take_profit
    
    if trigger_price is None:
        raise ValueError("Position has no take_profit and no trigger_price provided")
    
    # Create bar that triggers TP
    bar = create_bar(
        symbol=position.symbol,
        price=trigger_price + 0.0005  # 5 pips above TP to ensure trigger
    )
    
    broker.update(position.symbol, bar)
    
    # Check if position closed
    return position_id not in broker.positions


def get_last_trade(broker: PaperTradingBrokerAPI) -> Optional[Dict]:
    """
    Get the most recent trade from history
    
    Args:
        broker: PaperTradingBrokerAPI instance
    
    Returns:
        Last trade dict or None if no trades
    
    Example:
        >>> broker = create_test_broker()
        >>> success, pos_id, _ = create_position_with_sl_tp(broker)
        >>> trigger_take_profit(broker, pos_id)
        >>> trade = get_last_trade(broker)
        >>> assert trade['pnl'] > 0  # Profitable trade
    """
    if not broker.trade_history:
        return None
    return broker.trade_history[-1]


def assert_position_has_sl_tp(
    broker: PaperTradingBrokerAPI,
    position_id: str,
    expected_sl: float,
    expected_tp: float
):
    """
    Assert a position has expected SL/TP values
    
    Args:
        broker: PaperTradingBrokerAPI instance
        position_id: Position to check
        expected_sl: Expected stop loss price
        expected_tp: Expected take profit price
    
    Raises:
        AssertionError if values don't match
    
    Example:
        >>> broker = create_test_broker()
        >>> success, pos_id, _ = create_position_with_sl_tp(
        ...     broker=broker, stop_loss=1.0950, take_profit=1.1100
        ... )
        >>> assert_position_has_sl_tp(broker, pos_id, 1.0950, 1.1100)
    """
    assert position_id in broker.positions, f"Position {position_id} not found"
    
    position = broker.positions[position_id]
    
    assert position.stop_loss == expected_sl, \
        f"Expected SL={expected_sl}, got {position.stop_loss}"
    
    assert position.take_profit == expected_tp, \
        f"Expected TP={expected_tp}, got {position.take_profit}"
