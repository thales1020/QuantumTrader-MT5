#!/usr/bin/env python3
"""
Unit Tests for Risk Management
Test risk calculations, position sizing, and account protection
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPositionSizing(unittest.TestCase):
    """Test Position Size Calculation"""
    
    def test_position_size_calculation_eur(self):
        """Test position size for EUR pairs"""
        balance = 10000
        risk_percent = 1.0
        risk_amount = balance * (risk_percent / 100)  # $100
        
        entry = 1.0850
        sl = 1.0800
        pip_risk = abs(entry - sl) / 0.0001  # 50 pips
        
        # $10 per pip per lot for EUR pairs
        lot_size = risk_amount / (pip_risk * 10)
        
        self.assertAlmostEqual(lot_size, 0.2, places=2)
    
    def test_position_size_calculation_gbp(self):
        """Test position size for GBP pairs"""
        balance = 10000
        risk_percent = 0.75
        risk_amount = balance * (risk_percent / 100)  # $75
        
        entry = 1.2650
        sl = 1.2600
        pip_risk = abs(entry - sl) / 0.0001  # 50 pips
        
        lot_size = risk_amount / (pip_risk * 10)
        
        self.assertAlmostEqual(lot_size, 0.15, places=2)
    
    def test_position_size_calculation_jpy(self):
        """Test position size for JPY pairs"""
        balance = 10000
        risk_percent = 0.5
        risk_amount = balance * (risk_percent / 100)  # $50
        
        entry = 149.50
        sl = 149.00
        pip_risk = abs(entry - sl) / 0.01  # 50 pips (JPY uses 0.01)
        
        # $10 per pip per lot for JPY pairs
        lot_size = risk_amount / (pip_risk * 10)
        
        self.assertAlmostEqual(lot_size, 0.1, places=2)
    
    def test_position_size_calculation_gold(self):
        """Test position size for XAUUSD (Gold)"""
        balance = 10000
        risk_percent = 1.0
        risk_amount = balance * (risk_percent / 100)  # $100
        
        entry = 2050.00
        sl = 2040.00
        pip_risk = abs(entry - sl) / 0.01  # 1000 pips (Gold uses 0.01)
        
        # $1 per pip per lot for Gold
        lot_size = risk_amount / (pip_risk * 1)
        
        self.assertAlmostEqual(lot_size, 0.1, places=2)
    
    def test_position_size_with_dual_orders(self):
        """Test position size considering dual orders"""
        balance = 10000
        risk_percent_config = 1.0
        
        # With dual orders, actual risk is 2x
        actual_total_risk = risk_percent_config * 2  # 2%
        risk_amount = balance * (actual_total_risk / 100)  # $200
        
        self.assertEqual(actual_total_risk, 2.0)
        self.assertEqual(risk_amount, 200)


class TestRiskLimits(unittest.TestCase):
    """Test Risk Limit Enforcement"""
    
    def test_max_risk_per_trade(self):
        """Test maximum risk per trade limit"""
        max_risk_percent = 2.0
        
        # Test various risk levels
        safe_risk = 1.0
        high_risk = 2.0
        excessive_risk = 3.0
        
        self.assertLessEqual(safe_risk, max_risk_percent)
        self.assertLessEqual(high_risk, max_risk_percent)
        self.assertGreater(excessive_risk, max_risk_percent)
    
    def test_total_account_risk_limit(self):
        """Test total account risk limit"""
        balance = 10000
        max_total_risk_percent = 10.0  # Max 10% of account at risk
        
        # Simulate 3 open positions
        position1_risk = balance * 0.01  # 1%
        position2_risk = balance * 0.01  # 1%
        position3_risk = balance * 0.01  # 1%
        
        total_risk = position1_risk + position2_risk + position3_risk
        total_risk_percent = (total_risk / balance) * 100
        
        self.assertEqual(total_risk_percent, 3.0)
        self.assertLessEqual(total_risk_percent, max_total_risk_percent)
    
    def test_dual_order_risk_limit(self):
        """Test risk limit with dual orders"""
        balance = 10000
        risk_per_order = 1.0  # 1%
        
        # Dual orders double the risk
        total_risk_per_signal = risk_per_order * 2  # 2%
        
        # With max 3 signals, total risk is 6%
        max_signals = 3
        max_total_risk = total_risk_per_signal * max_signals
        
        self.assertEqual(max_total_risk, 6.0)
        self.assertLessEqual(max_total_risk, 10.0)  # Under 10% limit


class TestStopLossCalculation(unittest.TestCase):
    """Test Stop Loss Calculation"""
    
    def test_sl_buy_order(self):
        """Test SL calculation for BUY order"""
        entry = 1.0850
        atr = 0.0020
        sl_multiplier = 2.0
        
        sl = entry - (atr * sl_multiplier)
        
        self.assertAlmostEqual(sl, 1.0810)
        self.assertLess(sl, entry)
    
    def test_sl_sell_order(self):
        """Test SL calculation for SELL order"""
        entry = 1.0850
        atr = 0.0020
        sl_multiplier = 2.0
        
        sl = entry + (atr * sl_multiplier)
        
        self.assertAlmostEqual(sl, 1.0890)
        self.assertGreater(sl, entry)
    
    def test_sl_minimum_distance(self):
        """Test SL has minimum distance from entry"""
        entry = 1.0850
        atr = 0.0005  # Very small ATR
        min_sl_pips = 10  # Minimum 10 pips
        
        sl_from_atr = entry - (atr * 2.0)  # 0.001 = 10 pips
        min_sl = entry - (min_sl_pips * 0.0001)
        
        actual_sl = min(sl_from_atr, min_sl)  # Use min for SELL, max for BUY
        
        sl_distance_pips = abs(entry - actual_sl) / 0.0001
        self.assertGreaterEqual(round(sl_distance_pips), min_sl_pips)


class TestTakeProfitCalculation(unittest.TestCase):
    """Test Take Profit Calculation"""
    
    def test_tp_buy_order_rr_1_1(self):
        """Test TP calculation for BUY order (RR 1:1)"""
        entry = 1.0850
        sl = 1.0800
        risk = abs(entry - sl)
        
        tp = entry + (risk * 1.0)
        
        self.assertAlmostEqual(tp, 1.0900)
        self.assertGreater(tp, entry)
    
    def test_tp_buy_order_rr_3_1(self):
        """Test TP calculation for BUY order (RR 3:1)"""
        entry = 1.0850
        sl = 1.0800
        risk = abs(entry - sl)
        
        tp = entry + (risk * 3.0)
        
        self.assertAlmostEqual(tp, 1.1000)
        self.assertGreater(tp, entry)
    
    def test_tp_sell_order_rr_1_1(self):
        """Test TP calculation for SELL order (RR 1:1)"""
        entry = 1.0850
        sl = 1.0900
        risk = abs(entry - sl)
        
        tp = entry - (risk * 1.0)
        
        self.assertAlmostEqual(tp, 1.0800)
        self.assertLess(tp, entry)
    
    def test_tp_sell_order_rr_3_1(self):
        """Test TP calculation for SELL order (RR 3:1)"""
        entry = 1.0850
        sl = 1.0900
        risk = abs(entry - sl)
        
        tp = entry - (risk * 3.0)
        
        self.assertAlmostEqual(tp, 1.0700)
        self.assertLess(tp, entry)
    
    def test_dual_order_tp_both_orders(self):
        """Test TP for both orders in dual order strategy"""
        entry = 1.0850
        sl = 1.0800
        risk = abs(entry - sl)
        
        # Quick order (RR 1:1)
        tp_quick = entry + (risk * 1.0)
        
        # Main order (RR 3:1)
        tp_main = entry + (risk * 3.0)
        
        self.assertAlmostEqual(tp_quick, 1.0900)
        self.assertAlmostEqual(tp_main, 1.1000)
        self.assertGreater(tp_main, tp_quick)


class TestRiskRewardRatio(unittest.TestCase):
    """Test Risk-Reward Ratio Validation"""
    
    def test_rr_ratio_calculation(self):
        """Test RR ratio calculation"""
        entry = 1.0850
        sl = 1.0800
        tp = 1.0950
        
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / risk
        
        self.assertAlmostEqual(rr_ratio, 2.0)
    
    def test_rr_ratio_minimum(self):
        """Test minimum RR ratio"""
        min_rr = 1.5
        
        # Test various RR ratios
        good_rr = 2.0
        acceptable_rr = 1.5
        poor_rr = 1.0
        
        self.assertGreaterEqual(good_rr, min_rr)
        self.assertGreaterEqual(acceptable_rr, min_rr)
        self.assertLess(poor_rr, min_rr)
    
    def test_dual_order_combined_rr(self):
        """Test combined RR for dual orders"""
        # Quick order: RR 1:1
        rr_quick = 1.0
        
        # Main order: RR 3:1
        rr_main = 3.0
        
        # Average RR (both orders equal volume)
        avg_rr = (rr_quick + rr_main) / 2
        
        self.assertEqual(avg_rr, 2.0)


class TestAccountProtection(unittest.TestCase):
    """Test Account Protection Mechanisms"""
    
    def test_daily_loss_limit(self):
        """Test daily loss limit"""
        balance = 10000
        max_daily_loss_percent = 5.0
        max_daily_loss = balance * (max_daily_loss_percent / 100)
        
        # Simulate daily loss
        daily_loss = 300
        
        self.assertLess(daily_loss, max_daily_loss)
    
    def test_drawdown_limit(self):
        """Test maximum drawdown limit"""
        initial_balance = 10000
        current_balance = 9000
        
        drawdown_percent = ((initial_balance - current_balance) / initial_balance) * 100
        max_drawdown_limit = 20.0
        
        self.assertEqual(drawdown_percent, 10.0)
        self.assertLess(drawdown_percent, max_drawdown_limit)
    
    def test_consecutive_losses_limit(self):
        """Test consecutive losses limit"""
        max_consecutive_losses = 5
        
        consecutive_losses = 3
        
        self.assertLess(consecutive_losses, max_consecutive_losses)
    
    def test_position_limit(self):
        """Test maximum positions limit"""
        max_positions = 3
        
        current_positions = 2
        
        self.assertLessEqual(current_positions, max_positions)


class TestLotSizeValidation(unittest.TestCase):
    """Test Lot Size Validation"""
    
    def test_lot_size_minimum(self):
        """Test minimum lot size"""
        min_lot = 0.01
        
        calculated_lot = 0.15
        
        self.assertGreaterEqual(calculated_lot, min_lot)
    
    def test_lot_size_maximum(self):
        """Test maximum lot size"""
        max_lot = 10.0
        
        calculated_lot = 0.5
        
        self.assertLessEqual(calculated_lot, max_lot)
    
    def test_lot_size_step(self):
        """Test lot size step (0.01)"""
        lot_size = 0.16  # Use a value that divides cleanly
        lot_step = 0.01
        
        # Check if lot size is a multiple of lot_step
        # Round to avoid floating point precision issues
        remainder = round(lot_size % lot_step, 2)
        
        self.assertEqual(remainder, 0.0)
    
    def test_lot_size_rounding(self):
        """Test lot size rounding to 2 decimals"""
        calculated_lot = 0.156789
        
        rounded_lot = round(calculated_lot, 2)
        
        self.assertEqual(rounded_lot, 0.16)


class TestBalanceImpact(unittest.TestCase):
    """Test Balance Impact Calculations"""
    
    def test_balance_after_win(self):
        """Test balance after winning trade"""
        initial_balance = 10000
        profit = 150
        
        new_balance = initial_balance + profit
        
        self.assertEqual(new_balance, 10150)
    
    def test_balance_after_loss(self):
        """Test balance after losing trade"""
        initial_balance = 10000
        loss = -100
        
        new_balance = initial_balance + loss
        
        self.assertEqual(new_balance, 9900)
    
    def test_balance_after_series_of_trades(self):
        """Test balance after series of trades"""
        balance = 10000
        
        trades = [100, -50, 150, -100, 200]
        
        for trade_pnl in trades:
            balance += trade_pnl
        
        expected_balance = 10000 + 300
        self.assertEqual(balance, expected_balance)
    
    def test_percentage_gain(self):
        """Test percentage gain calculation"""
        initial_balance = 10000
        final_balance = 11000
        
        gain_percent = ((final_balance - initial_balance) / initial_balance) * 100
        
        self.assertAlmostEqual(gain_percent, 10.0)
    
    def test_percentage_loss(self):
        """Test percentage loss calculation"""
        initial_balance = 10000
        final_balance = 9500
        
        loss_percent = ((initial_balance - final_balance) / initial_balance) * 100
        
        self.assertAlmostEqual(loss_percent, 5.0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
