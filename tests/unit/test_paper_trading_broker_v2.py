"""
Unit Tests for Paper Trading Broker API - Version 2
====================================================

Corrected tests using proper API structure.

Author: Independent Tester (3rd attempt)
Date: November 5, 2025
Lessons Learned: READ THE CODE FIRST!
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock MetaTrader5 BEFORE any imports
sys.modules['MetaTrader5'] = MagicMock()

from engines.paper_trading_broker_api import PaperTradingBrokerAPI


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def broker():
    """Create test broker instance with auto_update disabled"""
    import tempfile
    import os
    
    # Use unique temp database for each test
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    broker_instance = PaperTradingBrokerAPI(
        initial_balance=10000.0,
        db_path=temp_db.name,
        auto_update=False  # Critical for testing!
    )
    
    yield broker_instance
    
    # Cleanup
    try:
        os.unlink(temp_db.name)
    except:
        pass


@pytest.fixture
def filled_buy_position(broker):
    """Create a filled BUY position for testing"""
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1
    )
    
    # Fill the order at 1.1000
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    return broker, position_id


# ============================================================================
# TEST 1: BROKER INITIALIZATION
# ============================================================================

class TestBrokerInitialization:
    """Test broker initialization"""
    
    def test_broker_initializes_with_default_balance(self):
        """Test broker initializes with default balance"""
        broker = PaperTradingBrokerAPI()
        
        assert broker.balance == 10000.0
        assert broker.initial_balance == 10000.0
        assert broker.equity == 10000.0
        
    def test_broker_initializes_with_custom_balance(self):
        """Test broker initializes with custom balance"""
        broker = PaperTradingBrokerAPI(initial_balance=50000.0)
        
        assert broker.balance == 50000.0
        assert broker.initial_balance == 50000.0
        
    def test_broker_has_empty_positions_on_init(self):
        """Test broker starts with no positions"""
        broker = PaperTradingBrokerAPI()
        
        assert len(broker.positions) == 0
        
    def test_broker_has_matching_engine(self):
        """Test broker has order matching engine"""
        broker = PaperTradingBrokerAPI()
        
        assert hasattr(broker, 'matching_engine')
        assert hasattr(broker.matching_engine, 'pending_orders')


# ============================================================================
# TEST 2: ORDER SUBMISSION
# ============================================================================

class TestOrderSubmission:
    """Test order submission via public API"""
    
    def test_submit_market_order_returns_order_id(self, broker):
        """Test submitting market order returns order ID"""
        result = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1
        )
        
        # submit_order returns (success, order_id, error)
        assert result is not None
        success, order_id, error = result
        assert success is True
        assert order_id is not None
        assert isinstance(order_id, str)
        
    def test_submit_order_with_sl_tp(self, broker):
        """Test submitting order with SL/TP parameters"""
        result = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950,
            take_profit=1.1100
        )
        
        success, order_id, error = result
        assert success is True
        assert order_id is not None
        
        # Order should be in pending orders
        pending_orders = broker.matching_engine.pending_orders
        assert order_id in pending_orders


# ============================================================================
# TEST 3: SL/TP EXTRACTION (Priority 1 - Fix #1)
# ============================================================================

class TestSLTPExtraction:
    """Test SL/TP extraction from orders to positions"""
    
    def test_stop_loss_extracted_to_position(self, broker):
        """Test SL is extracted from order to position"""
        # Submit order with SL
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950
        )
        
        # Fill order
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        # Verify SL extracted to position
        assert len(broker.positions) == 1
        position = list(broker.positions.values())[0]
        assert position.stop_loss == 1.0950
        
    def test_take_profit_extracted_to_position(self, broker):
        """Test TP is extracted from order to position"""
        # Submit order with TP
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            take_profit=1.1100
        )
        
        # Fill order
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        # Verify TP extracted to position
        assert len(broker.positions) == 1
        position = list(broker.positions.values())[0]
        assert position.take_profit == 1.1100
        
    def test_both_sl_and_tp_extracted(self, broker):
        """Test both SL and TP are extracted"""
        # Submit order with both SL and TP
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            stop_loss=1.0950,
            take_profit=1.1100
        )
        
        # Fill order
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        # Verify both extracted
        position = list(broker.positions.values())[0]
        assert position.stop_loss == 1.0950
        assert position.take_profit == 1.1100
        
    def test_missing_sl_tp_handles_gracefully(self, broker):
        """Test position creation with no SL/TP"""
        # Submit order without SL/TP
        success, order_id, error = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1
        )
        
        # Fill order
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        # Verify position created without SL/TP
        position = list(broker.positions.values())[0]
        assert position.stop_loss is None
        assert position.take_profit is None


# ============================================================================
# TEST 4: SL/TP MONITORING (Priority 1 - Fix #2)
# ============================================================================

class TestSLTPMonitoring:
    """Test SL/TP monitoring and auto-close"""
    
    def test_stop_loss_triggers_close_for_buy(self, broker):
        """Test BUY position closes when price hits SL"""
        # Create BUY position with SL at 1.0950
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
        
        # Simulate price dropping below SL
        bar = {
            'time': datetime.now(),
            'open': 1.0980,
            'high': 1.0990,
            'low': 1.0940,    # Below SL (1.0950)
            'close': 1.0960,
            'volume': 100
        }
        
        broker._update_positions("EURUSD", bar)
        
        # Verify position auto-closed
        assert position_id not in broker.positions
        assert len(broker.trade_history) > 0
        assert broker.trade_history[-1].exit_reason == "Stop Loss"
        
    def test_take_profit_triggers_close_for_buy(self, broker):
        """Test BUY position closes when price hits TP"""
        # Create BUY position with TP at 1.1100
        order_id = broker.submit_order(
            symbol="EURUSD",
            order_type="MARKET",
            side="BUY",
            quantity=0.1,
            take_profit=1.1100
        )
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position_id = list(broker.positions.keys())[0]
        
        # Simulate price rising above TP
        bar = {
            'time': datetime.now(),
            'open': 1.1050,
            'high': 1.1110,   # Above TP (1.1100)
            'low': 1.1040,
            'close': 1.1080,
            'volume': 100
        }
        
        broker._update_positions("EURUSD", bar)
        
        # Verify position auto-closed
        assert position_id not in broker.positions
        assert len(broker.trade_history) > 0
        assert broker.trade_history[-1].exit_reason == "Take Profit"


# ============================================================================
# TEST 5: P&L CALCULATION (Priority 1 - Fix #3)
# ============================================================================

class TestPnLCalculation:
    """Test P&L calculation accuracy"""
    
    def test_pnl_components_exist(self, broker):
        """Test that all P&L components exist in trade"""
        # Create and close position
        order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position_id = list(broker.positions.keys())[0]
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1050):
            broker.close_position(position_id)
        
        trade = broker.trade_history[-1]
        
        # Verify all P&L components exist
        assert hasattr(trade, 'gross_pnl')
        assert hasattr(trade, 'net_pnl')
        assert hasattr(trade, 'commission')
        assert hasattr(trade, 'swap')
        
    def test_profitable_buy_position_pnl(self, broker):
        """Test P&L calculation for profitable BUY"""
        order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)
        
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
            broker._process_pending_orders()
        
        position_id = list(broker.positions.keys())[0]
        initial_balance = broker.balance
        
        # Close at +50 pips profit
        with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1050):
            broker.close_position(position_id)
        
        trade = broker.trade_history[-1]
        
        # Verify P&L positive
        assert trade.gross_pnl > 0
        assert trade.net_pnl > 0
        
        # Verify costs deducted
        assert trade.net_pnl < trade.gross_pnl
        
        # Verify balance updated
        final_balance = broker.balance
        assert final_balance > initial_balance


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
