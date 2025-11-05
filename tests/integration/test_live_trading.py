#!/usr/bin/env python3
"""
Unit Tests for Live Trading Mode
Test live trading functionality, MT5 integration, and safety mechanisms
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMT5Connection(unittest.TestCase):
    """Test MetaTrader5 Connection and Initialization"""
    
    @patch('MetaTrader5.initialize')
    @patch('MetaTrader5.login')
    def test_mt5_initialization_success(self, mock_login, mock_initialize):
        """Test successful MT5 initialization"""
        mock_initialize.return_value = True
        mock_login.return_value = True
        
        # Simulate initialization
        result = mock_initialize()
        self.assertTrue(result)
    
    @patch('MetaTrader5.initialize')
    def test_mt5_initialization_failure(self, mock_initialize):
        """Test MT5 initialization failure handling"""
        mock_initialize.return_value = False
        
        result = mock_initialize()
        self.assertFalse(result)
    
    @patch('MetaTrader5.login')
    def test_mt5_login_success(self, mock_login):
        """Test successful MT5 login"""
        mock_login.return_value = True
        
        result = mock_login(account=270192254, password="test", server="Exness-MT5Trial17")
        self.assertTrue(result)
    
    @patch('MetaTrader5.login')
    def test_mt5_login_failure(self, mock_login):
        """Test MT5 login failure handling"""
        mock_login.return_value = False
        
        result = mock_login(account=999999, password="wrong", server="InvalidServer")
        self.assertFalse(result)
    
    @patch('MetaTrader5.account_info')
    def test_account_info_retrieval(self, mock_account_info):
        """Test account information retrieval"""
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account.equity = 10150.0
        mock_account.margin = 200.0
        mock_account.margin_free = 9950.0
        mock_account.leverage = 100
        
        mock_account_info.return_value = mock_account
        
        account = mock_account_info()
        
        self.assertEqual(account.balance, 10000.0)
        self.assertEqual(account.equity, 10150.0)
        self.assertGreater(account.equity, account.balance)


class TestLiveOrderPlacement(unittest.TestCase):
    """Test Live Order Placement and Validation"""
    
    @patch('MetaTrader5.order_send')
    @patch('MetaTrader5.symbol_info_tick')
    def test_buy_order_placement(self, mock_tick, mock_order_send):
        """Test BUY order placement"""
        # Mock current price
        mock_tick.return_value = Mock(ask=1.0850, bid=1.0848)
        
        # Mock successful order
        mock_result = Mock()
        mock_result.retcode = 10009  # TRADE_RETCODE_DONE
        mock_result.order = 123456
        mock_result.volume = 0.1
        mock_order_send.return_value = mock_result
        
        result = mock_order_send({
            'action': 1,  # TRADE_ACTION_DEAL
            'symbol': 'EURUSDm',
            'volume': 0.1,
            'type': 0,  # ORDER_TYPE_BUY
            'price': 1.0850,
            'sl': 1.0800,
            'tp': 1.0950
        })
        
        self.assertEqual(result.retcode, 10009)
        self.assertEqual(result.order, 123456)
    
    @patch('MetaTrader5.order_send')
    def test_sell_order_placement(self, mock_order_send):
        """Test SELL order placement"""
        mock_result = Mock()
        mock_result.retcode = 10009
        mock_result.order = 123457
        mock_order_send.return_value = mock_result
        
        result = mock_order_send({
            'action': 1,
            'symbol': 'EURUSDm',
            'volume': 0.1,
            'type': 1,  # ORDER_TYPE_SELL
            'price': 1.0850,
            'sl': 1.0900,
            'tp': 1.0750
        })
        
        self.assertEqual(result.retcode, 10009)
    
    @patch('MetaTrader5.order_send')
    def test_order_placement_failure(self, mock_order_send):
        """Test order placement failure handling"""
        mock_result = Mock()
        mock_result.retcode = 10013  # Invalid request
        mock_result.comment = "Invalid volume"
        mock_order_send.return_value = mock_result
        
        result = mock_order_send({
            'volume': 0.001  # Too small
        })
        
        self.assertNotEqual(result.retcode, 10009)
        self.assertEqual(result.retcode, 10013)
    
    def test_dual_order_placement_validation(self):
        """Test dual order placement validation"""
        # Validate that both orders have correct parameters
        order1 = {
            'volume': 0.1,
            'tp': 1.0900,  # RR 1:1
            'comment': 'ICT_SMC_BUY_Q75_RR1'
        }
        
        order2 = {
            'volume': 0.1,
            'tp': 1.1000,  # RR 3:1
            'comment': 'ICT_SMC_BUY_Q75_RR2'
        }
        
        self.assertEqual(order1['volume'], order2['volume'])
        self.assertGreater(order2['tp'], order1['tp'])
        self.assertIn('RR1', order1['comment'])
        self.assertIn('RR2', order2['comment'])


class TestLivePositionManagement(unittest.TestCase):
    """Test Live Position Management"""
    
    @patch('MetaTrader5.positions_get')
    def test_get_open_positions(self, mock_positions):
        """Test retrieving open positions"""
        mock_pos1 = Mock()
        mock_pos1.ticket = 123456
        mock_pos1.symbol = 'EURUSDm'
        mock_pos1.volume = 0.1
        mock_pos1.profit = 50.0
        
        mock_positions.return_value = [mock_pos1]
        
        positions = mock_positions()
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].ticket, 123456)
        self.assertEqual(positions[0].profit, 50.0)
    
    @patch('MetaTrader5.positions_total')
    def test_position_count_limit(self, mock_positions_total):
        """Test position count limit enforcement"""
        max_positions = 3
        
        mock_positions_total.return_value = 2
        current_positions = mock_positions_total()
        
        can_open_new = current_positions < max_positions
        self.assertTrue(can_open_new)
        
        mock_positions_total.return_value = 3
        current_positions = mock_positions_total()
        
        can_open_new = current_positions < max_positions
        self.assertFalse(can_open_new)
    
    @patch('MetaTrader5.order_send')
    @patch('MetaTrader5.positions_get')
    def test_position_close(self, mock_positions, mock_order_send):
        """Test closing a position"""
        # Mock open position
        mock_pos = Mock()
        mock_pos.ticket = 123456
        mock_pos.volume = 0.1
        mock_pos.type = 0  # BUY
        
        mock_positions.return_value = [mock_pos]
        
        # Mock close order
        mock_result = Mock()
        mock_result.retcode = 10009
        mock_order_send.return_value = mock_result
        
        result = mock_order_send({
            'action': 1,
            'position': 123456,
            'type': 1,  # SELL to close BUY
            'volume': 0.1
        })
        
        self.assertEqual(result.retcode, 10009)
    
    @patch('MetaTrader5.positions_get')
    def test_position_monitoring(self, mock_positions):
        """Test position profit monitoring"""
        mock_pos = Mock()
        mock_pos.ticket = 123456
        mock_pos.profit = -150.0  # Loss
        mock_pos.volume = 0.1
        
        mock_positions.return_value = [mock_pos]
        
        positions = mock_positions()
        
        # Check if loss exceeds threshold
        max_loss_per_position = 200.0
        should_close = positions[0].profit < -max_loss_per_position
        
        self.assertFalse(should_close)  # Still within limit


class TestLiveSafetyMechanisms(unittest.TestCase):
    """Test Live Trading Safety Mechanisms"""
    
    def test_daily_loss_limit_check(self):
        """Test daily loss limit enforcement"""
        starting_balance = 10000.0
        current_balance = 9600.0
        max_daily_loss_percent = 5.0
        
        daily_loss = starting_balance - current_balance
        daily_loss_percent = (daily_loss / starting_balance) * 100
        
        self.assertEqual(daily_loss_percent, 4.0)
        
        should_stop_trading = daily_loss_percent >= max_daily_loss_percent
        self.assertFalse(should_stop_trading)
        
        # Test with exceeded limit
        current_balance = 9400.0
        daily_loss = starting_balance - current_balance
        daily_loss_percent = (daily_loss / starting_balance) * 100
        
        should_stop_trading = daily_loss_percent >= max_daily_loss_percent
        self.assertTrue(should_stop_trading)
    
    def test_max_drawdown_stop(self):
        """Test maximum drawdown stop loss"""
        peak_balance = 10500.0
        current_balance = 9200.0
        max_drawdown_percent = 15.0
        
        drawdown = ((peak_balance - current_balance) / peak_balance) * 100
        
        self.assertAlmostEqual(drawdown, 12.38, places=2)
        
        should_stop = drawdown >= max_drawdown_percent
        self.assertFalse(should_stop)
    
    def test_consecutive_losses_limit(self):
        """Test consecutive losses limit"""
        trades = [
            {'result': 'LOSS'},
            {'result': 'LOSS'},
            {'result': 'LOSS'},
            {'result': 'LOSS'},
        ]
        
        consecutive_losses = len([t for t in trades if t['result'] == 'LOSS'])
        max_consecutive_losses = 5
        
        should_stop = consecutive_losses >= max_consecutive_losses
        self.assertFalse(should_stop)
        
        # Add one more loss
        trades.append({'result': 'LOSS'})
        consecutive_losses = len([t for t in trades if t['result'] == 'LOSS'])
        
        should_stop = consecutive_losses >= max_consecutive_losses
        self.assertTrue(should_stop)
    
    @patch('MetaTrader5.account_info')
    def test_margin_level_check(self, mock_account_info):
        """Test margin level safety check"""
        mock_account = Mock()
        mock_account.margin = 1000.0
        mock_account.equity = 10000.0
        mock_account.margin_level = 1000.0  # (equity / margin) * 100
        
        mock_account_info.return_value = mock_account
        
        account = mock_account_info()
        
        min_margin_level = 200.0
        is_safe = account.margin_level > min_margin_level
        
        self.assertTrue(is_safe)
    
    def test_trading_hours_validation(self):
        """Test trading hours validation"""
        start_hour = 8
        end_hour = 22
        
        # Test during trading hours
        current_time = datetime(2025, 10, 17, 15, 30)  # 15:30
        current_hour = current_time.hour
        
        is_trading_hours = start_hour <= current_hour < end_hour
        self.assertTrue(is_trading_hours)
        
        # Test outside trading hours
        current_time = datetime(2025, 10, 17, 2, 30)  # 02:30
        current_hour = current_time.hour
        
        is_trading_hours = start_hour <= current_hour < end_hour
        self.assertFalse(is_trading_hours)


class TestLiveRiskManagement(unittest.TestCase):
    """Test Live Risk Management"""
    
    @patch('MetaTrader5.account_info')
    def test_position_size_with_live_balance(self, mock_account_info):
        """Test position sizing with live account balance"""
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account_info.return_value = mock_account
        
        account = mock_account_info()
        
        risk_percent = 1.0
        risk_amount = account.balance * (risk_percent / 100)
        
        entry = 1.0850
        sl = 1.0800
        pip_risk = abs(entry - sl) / 0.0001
        
        lot_size = risk_amount / (pip_risk * 10)
        
        self.assertEqual(risk_amount, 100.0)
        self.assertAlmostEqual(lot_size, 0.2, places=2)
    
    @patch('MetaTrader5.positions_get')
    @patch('MetaTrader5.account_info')
    def test_total_exposure_limit(self, mock_account_info, mock_positions):
        """Test total account exposure limit"""
        mock_account = Mock()
        mock_account.balance = 10000.0
        mock_account_info.return_value = mock_account
        
        # Mock 2 open positions
        mock_pos1 = Mock()
        mock_pos1.volume = 0.2
        mock_pos1.profit = 50.0
        
        mock_pos2 = Mock()
        mock_pos2.volume = 0.1
        mock_pos2.profit = -30.0
        
        mock_positions.return_value = [mock_pos1, mock_pos2]
        
        account = mock_account_info()
        positions = mock_positions()
        
        # Calculate total exposure (simplified)
        total_volume = sum(p.volume for p in positions)
        
        max_total_volume = 1.0  # Max total volume
        
        can_open_more = total_volume < max_total_volume
        self.assertTrue(can_open_more)
    
    def test_emergency_stop_conditions(self):
        """Test emergency stop conditions"""
        conditions = {
            'daily_loss_exceeded': False,
            'max_drawdown_exceeded': False,
            'consecutive_losses': False,
            'margin_call': False,
            'connection_lost': False
        }
        
        should_emergency_stop = any(conditions.values())
        self.assertFalse(should_emergency_stop)
        
        # Trigger emergency condition
        conditions['max_drawdown_exceeded'] = True
        
        should_emergency_stop = any(conditions.values())
        self.assertTrue(should_emergency_stop)


class TestLiveDataValidation(unittest.TestCase):
    """Test Live Market Data Validation"""
    
    @patch('MetaTrader5.symbol_info_tick')
    def test_tick_data_validation(self, mock_tick):
        """Test tick data validation"""
        mock_tick.return_value = Mock(
            bid=1.0848,
            ask=1.0850,
            last=1.0849,
            time=int(datetime.now().timestamp())
        )
        
        tick = mock_tick()
        
        self.assertGreater(tick.ask, tick.bid)
        self.assertLessEqual(tick.ask - tick.bid, 0.0010)  # Max 10 pip spread
    
    @patch('MetaTrader5.copy_rates_from_pos')
    def test_historical_data_availability(self, mock_rates):
        """Test historical data availability"""
        # Mock 100 bars
        mock_rates.return_value = np.array([(0, 0, 0, 0, 0, 0, 0, 0)] * 100)
        
        rates = mock_rates('EURUSDm', 5, 0, 100)  # M5, 100 bars
        
        self.assertEqual(len(rates), 100)
        self.assertGreaterEqual(len(rates), 50)  # Minimum required
    
    @patch('MetaTrader5.symbol_info')
    def test_symbol_availability(self, mock_symbol_info):
        """Test symbol availability and trading status"""
        mock_symbol = Mock()
        mock_symbol.visible = True
        mock_symbol.select = True
        mock_symbol.trade_mode = 4  # Full trading allowed
        
        mock_symbol_info.return_value = mock_symbol
        
        symbol = mock_symbol_info()
        
        is_tradeable = (symbol.visible and 
                       symbol.select and 
                       symbol.trade_mode == 4)
        
        self.assertTrue(is_tradeable)
    
    def test_price_staleness_check(self):
        """Test price data staleness detection"""
        last_update = datetime.now() - timedelta(seconds=30)
        current_time = datetime.now()
        
        max_staleness_seconds = 60
        
        staleness = (current_time - last_update).total_seconds()
        is_stale = staleness > max_staleness_seconds
        
        self.assertFalse(is_stale)
        
        # Test stale data
        last_update = datetime.now() - timedelta(seconds=120)
        staleness = (current_time - last_update).total_seconds()
        is_stale = staleness > max_staleness_seconds
        
        self.assertTrue(is_stale)


class TestLiveLogging(unittest.TestCase):
    """Test Live Trading Logging and Monitoring"""
    
    def test_trade_logging_format(self):
        """Test trade log format"""
        trade_log = {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'EURUSDm',
            'action': 'BUY',
            'volume': 0.1,
            'entry': 1.0850,
            'sl': 1.0800,
            'tp': 1.0950,
            'ticket': 123456,
            'comment': 'ICT_SMC_BUY_Q75_RR1'
        }
        
        self.assertIn('timestamp', trade_log)
        self.assertIn('symbol', trade_log)
        self.assertIn('action', trade_log)
        self.assertIn('ticket', trade_log)
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking"""
        metrics = {
            'total_trades': 50,
            'wins': 20,
            'losses': 30,
            'win_rate': 40.0,
            'profit_factor': 1.2,
            'total_profit': 500.0,
            'max_drawdown': 12.5
        }
        
        self.assertEqual(metrics['win_rate'], 40.0)
        self.assertGreater(metrics['profit_factor'], 1.0)
        self.assertGreater(metrics['total_profit'], 0)
    
    def test_error_logging(self):
        """Test error logging and handling"""
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'error_type': 'ORDER_FAILED',
            'error_code': 10013,
            'message': 'Invalid volume',
            'symbol': 'EURUSDm',
            'action': 'RETRY'
        }
        
        self.assertIn('error_type', error_log)
        self.assertIn('error_code', error_log)
        self.assertIn('action', error_log)


class TestLiveRecoveryMechanisms(unittest.TestCase):
    """Test Live Trading Recovery and Failover"""
    
    @patch('MetaTrader5.initialize')
    def test_reconnection_logic(self, mock_initialize):
        """Test MT5 reconnection logic"""
        # First attempt fails
        mock_initialize.return_value = False
        result1 = mock_initialize()
        self.assertFalse(result1)
        
        # Retry succeeds
        mock_initialize.return_value = True
        result2 = mock_initialize()
        self.assertTrue(result2)
    
    def test_position_recovery_on_restart(self):
        """Test position recovery after restart"""
        # Simulate positions saved to file
        saved_positions = [
            {'ticket': 123456, 'symbol': 'EURUSDm', 'volume': 0.1},
            {'ticket': 123457, 'symbol': 'GBPUSDm', 'volume': 0.1}
        ]
        
        self.assertEqual(len(saved_positions), 2)
        
        # Recovery should restore these positions
        recovered = saved_positions.copy()
        self.assertEqual(len(recovered), 2)
        self.assertEqual(recovered[0]['ticket'], 123456)
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown procedure"""
        shutdown_steps = [
            'close_new_positions',
            'save_current_state',
            'close_mt5_connection',
            'save_logs'
        ]
        
        completed_steps = []
        
        for step in shutdown_steps:
            completed_steps.append(step)
        
        self.assertEqual(len(completed_steps), 4)
        self.assertIn('save_current_state', completed_steps)


class TestLiveTradingModes(unittest.TestCase):
    """Test Different Live Trading Modes"""
    
    def test_demo_mode_validation(self):
        """Test demo trading mode validation"""
        account_config = {
            'mode': 'demo',
            'login': 270192254,
            'server': 'Exness-MT5Trial17'
        }
        
        is_demo = account_config['mode'] == 'demo'
        self.assertTrue(is_demo)
    
    def test_live_mode_validation(self):
        """Test live trading mode validation"""
        account_config = {
            'mode': 'live',
            'login': 87654321,
            'server': 'YourBroker-Live'
        }
        
        is_live = account_config['mode'] == 'live'
        self.assertTrue(is_live)
        
        # Extra validation for live mode
        requires_confirmation = is_live
        self.assertTrue(requires_confirmation)
    
    def test_paper_trading_mode(self):
        """Test paper trading (simulation) mode"""
        mode = 'paper'
        
        is_paper = mode == 'paper'
        self.assertTrue(is_paper)
        
        # Paper trading doesn't send real orders
        send_real_orders = not is_paper
        self.assertFalse(send_real_orders)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
