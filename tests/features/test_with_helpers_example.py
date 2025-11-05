"""
Example Tests Using Test Helpers

This demonstrates how to use the test helpers from tests/helpers.py
to write clean, concise tests.

Run with: pytest tests/test_with_helpers_example.py -v
"""

import pytest
from tests.helpers import (
    create_test_broker,
    cleanup_test_broker,
    create_bar,
    submit_and_fill_order,
    create_position_with_sl_tp,
    trigger_stop_loss,
    trigger_take_profit,
    get_last_trade,
    assert_position_has_sl_tp
)


class TestWithHelpers:
    """Examples showing helper function usage"""
    
    def test_basic_order_submission(self):
        """Example: Submit and fill order using helper"""
        # Create broker
        broker = create_test_broker(initial_balance=10000.0)
        
        try:
            # Submit and fill in one call
            success, order_id, error, position_id = submit_and_fill_order(
                broker=broker,
                symbol="EURUSD",
                side="BUY",
                quantity=0.1,
                fill_price=1.1000
            )
            
            # Verify
            assert success is True
            assert error is None
            assert position_id is not None
            assert position_id in broker.positions
            
            # Check position details
            position = broker.positions[position_id]
            assert position.symbol == "EURUSD"
            assert position.lot_size == 0.1
            
        finally:
            cleanup_test_broker(broker)
    
    def test_position_with_sl_tp(self):
        """Example: Create position with SL/TP using helper"""
        broker = create_test_broker()
        
        try:
            # Create position with SL/TP in one call
            success, position_id, error = create_position_with_sl_tp(
                broker=broker,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100
            )
            
            # Verify
            assert success is True
            assert position_id is not None
            
            # Use assertion helper
            assert_position_has_sl_tp(
                broker=broker,
                position_id=position_id,
                expected_sl=1.0950,
                expected_tp=1.1100
            )
            
        finally:
            cleanup_test_broker(broker)
    
    def test_stop_loss_trigger(self):
        """Example: Test SL trigger using helper"""
        broker = create_test_broker()
        
        try:
            # Create position
            success, position_id, _ = create_position_with_sl_tp(
                broker=broker,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100
            )
            
            assert len(broker.positions) == 1
            
            # Trigger SL with helper
            closed = trigger_stop_loss(broker, position_id)
            
            # Verify position closed
            assert closed is True
            assert position_id not in broker.positions
            assert len(broker.trade_history) == 1
            
            # Check trade details
            trade = get_last_trade(broker)
            assert trade is not None
            assert trade['pnl'] < 0  # Loss (hit SL)
            
        finally:
            cleanup_test_broker(broker)
    
    def test_take_profit_trigger(self):
        """Example: Test TP trigger using helper"""
        broker = create_test_broker()
        
        try:
            # Create position
            success, position_id, _ = create_position_with_sl_tp(
                broker=broker,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100
            )
            
            # Trigger TP
            closed = trigger_take_profit(broker, position_id)
            
            # Verify
            assert closed is True
            assert len(broker.positions) == 0
            
            # Check P&L
            trade = get_last_trade(broker)
            assert trade['pnl'] > 0  # Profit (hit TP)
            assert trade['exit_price'] >= 1.1100
            
        finally:
            cleanup_test_broker(broker)
    
    def test_custom_bar_creation(self):
        """Example: Create custom price bars"""
        broker = create_test_broker()
        
        try:
            # Create position
            success, order_id, error, position_id = submit_and_fill_order(
                broker=broker,
                fill_price=1.1000
            )
            
            # Create custom bar with specific spread
            bar = create_bar(
                symbol="EURUSD",
                price=1.1050,  # 50 pips up
                spread=0.0003,  # 3 pips spread
                volume=5000
            )
            
            # Update broker
            broker.update("EURUSD", bar)
            
            # Check unrealized P&L changed
            position = broker.positions[position_id]
            assert position.unrealized_pnl > 0  # In profit
            
        finally:
            cleanup_test_broker(broker)


class TestComparisonWithoutHelpers:
    """Same tests WITHOUT helpers - see the difference!"""
    
    def test_basic_order_without_helpers(self):
        """BEFORE: Without helpers - verbose and repetitive"""
        from engines.paper_trading_broker_api import PaperTradingBrokerAPI
        from datetime import datetime
        
        # Lots of setup code
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Verbose order submission
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1
        )
        
        assert success is True
        
        # Manual bar creation (repetitive)
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
        
        # Manual update
        broker.update("EURUSD", bar)
        
        # Manual position lookup
        position_id = list(broker.positions.keys())[0]
        position = broker.positions[position_id]
        
        assert position.symbol == "EURUSD"
    
    def test_sl_trigger_without_helpers(self):
        """BEFORE: Without helpers - lots of boilerplate"""
        from engines.paper_trading_broker_api import PaperTradingBrokerAPI
        from datetime import datetime
        
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Submit order
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950
        )
        
        # Fill order
        bar = {
            'time': datetime.now(),
            'open': 1.1000,
            'high': 1.1000,
            'low': 1.1000,
            'close': 1.1000,
            'volume': 1000,
            'bid': 1.0999,
            'ask': 1.1001
        }
        broker.update("EURUSD", bar)
        
        # Get position
        position_id = list(broker.positions.keys())[0]
        
        # Trigger SL manually
        bar_sl = {
            'time': datetime.now(),
            'open': 1.0945,
            'high': 1.0945,
            'low': 1.0940,
            'close': 1.0945,
            'volume': 1000,
            'bid': 1.0944,
            'ask': 1.0946
        }
        broker.update("EURUSD", bar_sl)
        
        # Check closed
        assert position_id not in broker.positions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
