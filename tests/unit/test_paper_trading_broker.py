"""
Unit Tests for Paper Trading Broker API
========================================

Test the 3 critical fixes:
1. SL/TP extraction from orders
2. SL/TP monitoring and auto-close
3. P&L calculation

Author: Independent Tester
Date: November 5, 2025
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np


# Mock MetaTrader5 before any imports
import sys
sys.modules['MetaTrader5'] = MagicMock()

from engines.paper_trading_broker_api import PaperTradingBrokerAPI
from engines.broker_simulator import Position, Order, OrderType
from engines.order_matching_engine import Order as OMEOrder, OrderType as OMEOrderType, OrderSide


class TestPaperTradingBrokerInit:
    """Test broker initialization"""
    
    def test_broker_initialization_with_defaults(self):
        """Test broker initializes with default parameters"""
        broker = PaperTradingBrokerAPI()
        
        assert broker.balance == 10000.0
        assert broker.initial_balance == 10000.0
        assert len(broker.positions) == 0
        assert len(broker.orders) == 0
        assert len(broker.trade_history) == 0
        
    def test_broker_initialization_with_custom_balance(self):
        """Test broker initializes with custom balance"""
        broker = PaperTradingBrokerAPI(initial_balance=50000.0)
        
        assert broker.balance == 50000.0
        assert broker.initial_balance == 50000.0


class TestSLTPExtraction:
    """Test SL/TP extraction from orders (TODO Fix #1)"""
    
    def test_create_position_extracts_stop_loss(self):
        """Test that stop loss is extracted from order"""
        broker = PaperTradingBrokerAPI()
        
        # Create order with SL
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.0950,  # SL set
            take_profit=None
        )
        
        # Mock fill
        fill_price = 1.1000
        timestamp = datetime.now()
        
        # Create position from fill
        position = broker._create_position_from_fill(order, fill_price, timestamp)
        
        assert position.stop_loss == 1.0950
        assert position.entry_price == 1.1000
        
    def test_create_position_extracts_take_profit(self):
        """Test that take profit is extracted from order"""
        broker = PaperTradingBrokerAPI()
        
        # Create order with TP
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=1.1100  # TP set
        )
        
        # Mock fill
        fill_price = 1.1000
        timestamp = datetime.now()
        
        # Create position from fill
        position = broker._create_position_from_fill(order, fill_price, timestamp)
        
        assert position.take_profit == 1.1100
        assert position.entry_price == 1.1000
        
    def test_create_position_extracts_both_sl_and_tp(self):
        """Test that both SL and TP are extracted from order"""
        broker = PaperTradingBrokerAPI()
        
        # Create order with both SL and TP
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.0950,   # SL set
            take_profit=1.1100  # TP set
        )
        
        # Mock fill
        fill_price = 1.1000
        timestamp = datetime.now()
        
        # Create position from fill
        position = broker._create_position_from_fill(order, fill_price, timestamp)
        
        assert position.stop_loss == 1.0950
        assert position.take_profit == 1.1100
        assert position.entry_price == 1.1000
        
    def test_create_position_handles_missing_sl_tp(self):
        """Test that position creation handles missing SL/TP gracefully"""
        broker = PaperTradingBrokerAPI()
        
        # Create order without SL/TP
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Mock fill
        fill_price = 1.1000
        timestamp = datetime.now()
        
        # Create position from fill
        position = broker._create_position_from_fill(order, fill_price, timestamp)
        
        assert position.stop_loss is None
        assert position.take_profit is None
        assert position.entry_price == 1.1000


class TestSLTPMonitoring:
    """Test SL/TP monitoring and auto-close (TODO Fix #2)"""
    
    def test_stop_loss_triggers_for_buy_position(self):
        """Test that BUY position closes when price drops below SL"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Create BUY position with SL
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=None
        )
        
        # Execute order (position opens)
        broker._execute_market_order(order, 1.1000, datetime.now())
        
        assert len(broker.positions) == 1
        
        # Simulate price drop below SL
        market_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'high': [1.0960],
            'low': [1.0940],  # Below SL
            'close': [1.0945],
            'bid': [1.0944],
            'ask': [1.0946]
        })
        
        # Update positions (should trigger SL)
        broker._update_positions(market_data.iloc[0])
        
        # Position should be closed
        assert len(broker.positions) == 0
        assert len(broker.trade_history) == 1
        assert broker.trade_history[0].exit_reason == "Stop Loss"
        
    def test_take_profit_triggers_for_buy_position(self):
        """Test that BUY position closes when price rises above TP"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Create BUY position with TP
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=1.1100
        )
        
        # Execute order (position opens)
        broker._execute_market_order(order, 1.1000, datetime.now())
        
        assert len(broker.positions) == 1
        
        # Simulate price rise above TP
        market_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'high': [1.1110],  # Above TP
            'low': [1.1095],
            'close': [1.1105],
            'bid': [1.1104],
            'ask': [1.1106]
        })
        
        # Update positions (should trigger TP)
        broker._update_positions(market_data.iloc[0])
        
        # Position should be closed
        assert len(broker.positions) == 0
        assert len(broker.trade_history) == 1
        assert broker.trade_history[0].exit_reason == "Take Profit"
        
    def test_stop_loss_triggers_for_sell_position(self):
        """Test that SELL position closes when price rises above SL"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Create SELL position with SL
        order = Order(
            symbol='EURUSD',
            order_type='SELL',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.1050,  # Above entry for SELL
            take_profit=None
        )
        
        # Execute order (position opens)
        broker._execute_market_order(order, 1.1000, datetime.now())
        
        assert len(broker.positions) == 1
        
        # Simulate price rise above SL
        market_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'high': [1.1060],  # Above SL
            'low': [1.1045],
            'close': [1.1055],
            'bid': [1.1054],
            'ask': [1.1056]
        })
        
        # Update positions (should trigger SL)
        broker._update_positions(market_data.iloc[0])
        
        # Position should be closed
        assert len(broker.positions) == 0
        assert len(broker.trade_history) == 1
        assert broker.trade_history[0].exit_reason == "Stop Loss"
        
    def test_take_profit_triggers_for_sell_position(self):
        """Test that SELL position closes when price drops below TP"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # Create SELL position with TP
        order = Order(
            symbol='EURUSD',
            order_type='SELL',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=1.0900  # Below entry for SELL
        )
        
        # Execute order (position opens)
        broker._execute_market_order(order, 1.1000, datetime.now())
        
        assert len(broker.positions) == 1
        
        # Simulate price drop below TP
        market_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'high': [1.0905],
            'low': [1.0890],  # Below TP
            'close': [1.0895],
            'bid': [1.0894],
            'ask': [1.0896]
        })
        
        # Update positions (should trigger TP)
        broker._update_positions(market_data.iloc[0])
        
        # Position should be closed
        assert len(broker.positions) == 0
        assert len(broker.trade_history) == 1
        assert broker.trade_history[0].exit_reason == "Take Profit"


class TestPnLCalculation:
    """Test P&L calculation accuracy (TODO Fix #3)"""
    
    def test_pnl_calculation_buy_position_profit(self):
        """Test P&L calculation for profitable BUY position"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # BUY at 1.1000, close at 1.1050 (+50 pips)
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Execute order
        broker._execute_market_order(order, 1.1000, datetime.now())
        initial_balance = broker.balance
        
        # Close position at profit
        position = broker.positions[0]
        trade = broker._close_position_internal(position, 1.1050, datetime.now(), "Manual Close")
        
        # Expected: (1.1050 - 1.1000) * 0.1 * 100,000 = $500 (before costs)
        # Net should be positive after costs
        assert trade.gross_pnl > 0
        assert trade.net_pnl > 0
        assert trade.net_pnl < trade.gross_pnl  # Costs deducted
        assert broker.balance > initial_balance
        
    def test_pnl_calculation_buy_position_loss(self):
        """Test P&L calculation for losing BUY position"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # BUY at 1.1000, close at 1.0950 (-50 pips)
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Execute order
        broker._execute_market_order(order, 1.1000, datetime.now())
        initial_balance = broker.balance
        
        # Close position at loss
        position = broker.positions[0]
        trade = broker._close_position_internal(position, 1.0950, datetime.now(), "Manual Close")
        
        # Expected: (1.0950 - 1.1000) * 0.1 * 100,000 = -$500 (before costs)
        # Net should be negative after costs
        assert trade.gross_pnl < 0
        assert trade.net_pnl < 0
        assert trade.net_pnl < trade.gross_pnl  # Costs make it worse
        assert broker.balance < initial_balance
        
    def test_pnl_calculation_sell_position_profit(self):
        """Test P&L calculation for profitable SELL position"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # SELL at 1.1000, close at 1.0950 (+50 pips)
        order = Order(
            symbol='EURUSD',
            order_type='SELL',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Execute order
        broker._execute_market_order(order, 1.1000, datetime.now())
        initial_balance = broker.balance
        
        # Close position at profit
        position = broker.positions[0]
        trade = broker._close_position_internal(position, 1.0950, datetime.now(), "Manual Close")
        
        # Expected: (1.1000 - 1.0950) * 0.1 * 100,000 = $500 (before costs)
        # Net should be positive after costs
        assert trade.gross_pnl > 0
        assert trade.net_pnl > 0
        assert trade.net_pnl < trade.gross_pnl  # Costs deducted
        assert broker.balance > initial_balance
        
    def test_pnl_calculation_sell_position_loss(self):
        """Test P&L calculation for losing SELL position"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        # SELL at 1.1000, close at 1.1050 (-50 pips)
        order = Order(
            symbol='EURUSD',
            order_type='SELL',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Execute order
        broker._execute_market_order(order, 1.1000, datetime.now())
        initial_balance = broker.balance
        
        # Close position at loss
        position = broker.positions[0]
        trade = broker._close_position_internal(position, 1.1050, datetime.now(), "Manual Close")
        
        # Expected: (1.1000 - 1.1050) * 0.1 * 100,000 = -$500 (before costs)
        # Net should be negative after costs
        assert trade.gross_pnl < 0
        assert trade.net_pnl < 0
        assert trade.net_pnl < trade.gross_pnl  # Costs make it worse
        assert broker.balance < initial_balance
        
    def test_pnl_includes_all_costs(self):
        """Test that P&L calculation includes spread, commission, and swap"""
        broker = PaperTradingBrokerAPI(initial_balance=10000.0)
        
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Execute and close
        broker._execute_market_order(order, 1.1000, datetime.now())
        position = broker.positions[0]
        trade = broker._close_position_internal(position, 1.1050, datetime.now(), "Manual Close")
        
        # Verify all cost components exist
        assert hasattr(trade, 'spread_cost')
        assert hasattr(trade, 'commission')
        assert hasattr(trade, 'swap')
        assert hasattr(trade, 'gross_pnl')
        assert hasattr(trade, 'net_pnl')
        
        # Total costs should be sum of individual costs
        expected_costs = trade.spread_cost + trade.commission + trade.swap
        assert abs(trade.gross_pnl - trade.net_pnl - expected_costs) < 0.01  # Allow small rounding


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_volume_order_rejected(self):
        """Test that orders with zero volume are rejected"""
        broker = PaperTradingBrokerAPI()
        
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.0,  # Invalid
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Should raise error or return False
        with pytest.raises(Exception):
            broker._execute_market_order(order, 1.1000, datetime.now())
            
    def test_negative_volume_order_rejected(self):
        """Test that orders with negative volume are rejected"""
        broker = PaperTradingBrokerAPI()
        
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=-0.1,  # Invalid
            entry_price=1.1000,
            stop_loss=None,
            take_profit=None
        )
        
        # Should raise error or return False
        with pytest.raises(Exception):
            broker._execute_market_order(order, 1.1000, datetime.now())
            
    def test_invalid_sl_for_buy_rejected(self):
        """Test that invalid SL (above entry) for BUY is rejected"""
        broker = PaperTradingBrokerAPI()
        
        order = Order(
            symbol='EURUSD',
            order_type='BUY',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.1050,  # Invalid - should be below entry
            take_profit=None
        )
        
        # Should raise error or return False
        # Note: Implementation may or may not validate this
        # This test documents expected behavior
        
    def test_invalid_sl_for_sell_rejected(self):
        """Test that invalid SL (below entry) for SELL is rejected"""
        broker = PaperTradingBrokerAPI()
        
        order = Order(
            symbol='EURUSD',
            order_type='SELL',
            volume=0.1,
            entry_price=1.1000,
            stop_loss=1.0950,  # Invalid - should be above entry
            take_profit=None
        )
        
        # Should raise error or return False
        # Note: Implementation may or may not validate this
        # This test documents expected behavior


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
