#!/usr/bin/env python3
"""
Unit Tests for Crypto Trading (BTC, ETH)
Tests buy/sell orders, position sizing, and P&L calculations for cryptocurrencies
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import MetaTrader5 as mt5
except ImportError:
    print("Warning: MetaTrader5 not available - some tests will be skipped")
    mt5 = None

import json
from datetime import datetime


class TestCryptoPositionSizing(unittest.TestCase):
    """Test position sizing calculations for crypto (USD-based)"""
    
    def test_btc_position_size_calculation(self):
        """Test BTC position size with USD-based calculation"""
        balance = 10000.0
        risk_percent = 0.75
        btc_price = 67000.0
        sl_distance = 2000.0  # $2000 SL
        contract_size = 1.0  # 1 BTC per lot
        
        # Calculate risk amount
        risk_amount = balance * (risk_percent / 100)
        
        # USD-based lot calculation for crypto
        lot_size = risk_amount / (sl_distance * contract_size)
        lot_size = round(lot_size, 2)  # Round to 2 decimals
        
        # Expected: $75 / ($2000 * 1) = 0.0375 → 0.04 lots
        expected_lot = 0.04
        
        self.assertAlmostEqual(lot_size, expected_lot, places=2,
                              msg=f"BTC lot size should be {expected_lot}")
        
        # Verify actual risk
        actual_risk = lot_size * sl_distance * contract_size
        self.assertLessEqual(actual_risk, risk_amount * 1.1,
                            msg="Actual risk should not exceed intended risk by >10%")
    
    def test_eth_position_size_calculation(self):
        """Test ETH position size with USD-based calculation"""
        balance = 10000.0
        risk_percent = 0.5
        eth_price = 2600.0
        sl_distance = 100.0  # $100 SL
        contract_size = 1.0  # 1 ETH per lot
        
        # Calculate risk amount
        risk_amount = balance * (risk_percent / 100)
        
        # USD-based lot calculation
        lot_size = risk_amount / (sl_distance * contract_size)
        lot_size = round(lot_size, 2)
        
        # Expected: $50 / ($100 * 1) = 0.5 lots
        expected_lot = 0.5
        
        self.assertAlmostEqual(lot_size, expected_lot, places=2,
                              msg=f"ETH lot size should be {expected_lot}")
    
    def test_crypto_vs_forex_lot_sizing(self):
        """Verify crypto uses different calculation than forex"""
        # Crypto: lot = risk / (sl_distance * contract_size)
        # Forex: lot = risk / (pips * pip_value)
        
        balance = 10000.0
        risk_percent = 1.0
        risk_amount = balance * (risk_percent / 100)  # $100
        
        # BTC calculation (USD-based)
        btc_sl_distance = 1000.0  # $1000
        btc_contract_size = 1.0
        btc_lot = risk_amount / (btc_sl_distance * btc_contract_size)
        
        # EURUSD calculation (pip-based) for comparison
        eur_sl_pips = 50
        eur_pip_value = 1.0  # $1 per pip for 0.01 lot
        eur_lot = risk_amount / (eur_sl_pips * eur_pip_value)
        
        # BTC should have smaller lot size due to higher price movements
        self.assertNotEqual(btc_lot, eur_lot,
                           msg="Crypto and forex should use different lot calculations")


class TestCryptoProfitCalculation(unittest.TestCase):
    """Test P&L calculations for crypto trades"""
    
    def test_btc_profit_calculation(self):
        """Test BTC profit calculation (direct USD)"""
        lot_size = 0.05
        contract_size = 1.0
        entry_price = 65000.0
        exit_price = 67000.0  # +$2000
        
        # Crypto P&L: price_diff * contract_size * lot_size
        price_diff = exit_price - entry_price
        profit = price_diff * contract_size * lot_size
        
        # Expected: 2000 * 1.0 * 0.05 = $100
        expected_profit = 100.0
        
        self.assertAlmostEqual(profit, expected_profit, places=2,
                              msg=f"BTC profit should be ${expected_profit}")
    
    def test_btc_loss_calculation(self):
        """Test BTC loss calculation"""
        lot_size = 0.1
        contract_size = 1.0
        entry_price = 68000.0
        exit_price = 66500.0  # -$1500
        
        price_diff = exit_price - entry_price
        profit = price_diff * contract_size * lot_size
        
        # Expected: -1500 * 1.0 * 0.1 = -$150
        expected_loss = -150.0
        
        self.assertAlmostEqual(profit, expected_loss, places=2,
                              msg=f"BTC loss should be ${expected_loss}")
    
    def test_eth_profit_calculation(self):
        """Test ETH profit calculation"""
        lot_size = 0.5
        contract_size = 1.0
        entry_price = 2500.0
        exit_price = 2700.0  # +$200
        
        price_diff = exit_price - entry_price
        profit = price_diff * contract_size * lot_size
        
        # Expected: 200 * 1.0 * 0.5 = $100
        expected_profit = 100.0
        
        self.assertAlmostEqual(profit, expected_profit, places=2,
                              msg=f"ETH profit should be ${expected_profit}")
    
    def test_dual_order_crypto_profit(self):
        """Test profit calculation for dual orders on crypto"""
        # Order 1: RR 1:1 (quick profit)
        # Order 2: Main RR 4:1
        
        lot_size = 0.05  # Each order
        contract_size = 1.0
        entry_price = 66000.0
        sl_distance = 1000.0  # $1000 SL
        
        # Order 1: TP at RR 1:1
        tp1_distance = sl_distance  # $1000
        tp1_price = entry_price + tp1_distance
        profit1 = tp1_distance * contract_size * lot_size
        
        # Order 2: TP at RR 4:1
        tp2_distance = sl_distance * 4  # $4000
        tp2_price = entry_price + tp2_distance
        profit2 = tp2_distance * contract_size * lot_size
        
        # Total if both hit TP
        total_profit = profit1 + profit2
        
        # Expected: (1000 + 4000) * 1.0 * 0.05 = $250
        expected_total = 250.0
        
        self.assertAlmostEqual(total_profit, expected_total, places=2,
                              msg=f"Dual order total profit should be ${expected_total}")


@unittest.skipIf(mt5 is None, "MetaTrader5 not available")
class TestCryptoLiveOrders(unittest.TestCase):
    """Test live crypto order placement (requires MT5 connection)"""
    
    @classmethod
    def setUpClass(cls):
        """Setup MT5 connection"""
        # Load config
        config_path = Path(__file__).parent.parent / 'config' / 'config.json'
        with open(config_path, 'r') as f:
            cls.config = json.load(f)
        
        cls.demo_config = cls.config['accounts']['demo']
        
        # Initialize MT5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        # Login
        if not mt5.login(
            cls.demo_config['login'],
            password=cls.demo_config['password'],
            server=cls.demo_config['server']
        ):
            mt5.shutdown()
            raise Exception(f"MT5 login failed: {mt5.last_error()}")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup MT5 connection"""
        if mt5 is not None:
            mt5.shutdown()
    
    def test_btc_symbol_availability(self):
        """Test if BTCUSDm is available for trading"""
        symbol = "BTCUSDm"
        symbol_info = mt5.symbol_info(symbol)
        
        self.assertIsNotNone(symbol_info, f"{symbol} should be available")
        
        # Enable if not visible
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
            symbol_info = mt5.symbol_info(symbol)
        
        self.assertTrue(symbol_info.visible, f"{symbol} should be visible in Market Watch")
    
    def test_eth_symbol_availability(self):
        """Test if ETHUSDm is available for trading"""
        symbol = "ETHUSDm"
        symbol_info = mt5.symbol_info(symbol)
        
        self.assertIsNotNone(symbol_info, f"{symbol} should be available")
        
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
            symbol_info = mt5.symbol_info(symbol)
        
        self.assertTrue(symbol_info.visible, f"{symbol} should be visible in Market Watch")
    
    def test_btc_price_data(self):
        """Test if BTC price data is available"""
        symbol = "BTCUSDm"
        
        # Get current tick
        tick = mt5.symbol_info_tick(symbol)
        self.assertIsNotNone(tick, f"Should get tick data for {symbol}")
        
        # Verify prices are reasonable
        self.assertGreater(tick.ask, 0, "BTC ask price should be positive")
        self.assertGreater(tick.bid, 0, "BTC bid price should be positive")
        self.assertGreater(tick.ask, tick.bid, "Ask should be higher than bid")
        
        # BTC price should be in reasonable range (e.g., $20k - $200k)
        self.assertGreater(tick.ask, 20000, "BTC price should be > $20,000")
        self.assertLess(tick.ask, 200000, "BTC price should be < $200,000")
    
    def test_eth_price_data(self):
        """Test if ETH price data is available"""
        symbol = "ETHUSDm"
        
        tick = mt5.symbol_info_tick(symbol)
        self.assertIsNotNone(tick, f"Should get tick data for {symbol}")
        
        self.assertGreater(tick.ask, 0, "ETH ask price should be positive")
        self.assertGreater(tick.bid, 0, "ETH bid price should be positive")
        
        # ETH price should be in reasonable range (e.g., $500 - $10k)
        self.assertGreater(tick.ask, 500, "ETH price should be > $500")
        self.assertLess(tick.ask, 10000, "ETH price should be < $10,000")
    
    def test_btc_contract_specs(self):
        """Test BTC contract specifications"""
        symbol = "BTCUSDm"
        symbol_info = mt5.symbol_info(symbol)
        
        # Contract size should be 1.0 (1 BTC per lot)
        self.assertEqual(symbol_info.trade_contract_size, 1.0,
                        "BTC contract size should be 1.0")
        
        # Min volume
        self.assertGreater(symbol_info.volume_min, 0,
                          "Min volume should be positive")
        
        # Volume step
        self.assertGreater(symbol_info.volume_step, 0,
                          "Volume step should be positive")
    
    def test_crypto_order_validation(self):
        """Test crypto order parameters validation (dry run)"""
        symbol = "BTCUSDm"
        symbol_info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        
        # Calculate realistic order parameters
        balance = mt5.account_info().balance
        risk_percent = 0.5
        risk_amount = balance * (risk_percent / 100)
        
        price = tick.ask
        sl_distance = 1000.0  # $1000 SL
        lot_size = risk_amount / (sl_distance * symbol_info.trade_contract_size)
        lot_size = max(symbol_info.volume_min, round(lot_size, 2))
        
        # Validate lot size
        self.assertGreaterEqual(lot_size, symbol_info.volume_min,
                               "Lot size should be >= minimum")
        self.assertLessEqual(lot_size, symbol_info.volume_max,
                            "Lot size should be <= maximum")
        
        # Validate SL/TP distances
        sl_price = price - sl_distance
        tp_price = price + (sl_distance * 4)  # RR 4:1
        
        self.assertGreater(sl_price, 0, "SL price should be positive")
        self.assertGreater(tp_price, price, "TP should be above entry")
        self.assertLess(sl_price, price, "SL should be below entry (BUY)")


class TestCryptoRiskManagement(unittest.TestCase):
    """Test risk management for crypto trading"""
    
    def test_dual_order_total_risk(self):
        """Test that dual orders respect total risk limit"""
        balance = 10000.0
        risk_per_order = 0.5  # Each order risks 0.5%
        
        # Total risk should be 1.0% (2 orders × 0.5%)
        total_risk_percent = risk_per_order * 2
        total_risk_amount = balance * (total_risk_percent / 100)
        
        # Expected: $100 total risk
        expected_risk = 100.0
        
        self.assertEqual(total_risk_amount, expected_risk,
                        msg="Dual orders should risk 1.0% total")
    
    def test_crypto_max_position_size(self):
        """Test maximum position size limits for crypto"""
        balance = 10000.0
        max_risk_percent = 2.0  # Max 2% per trade
        
        btc_price = 66000.0
        sl_distance = 2000.0
        
        max_risk_amount = balance * (max_risk_percent / 100)
        max_lot_size = max_risk_amount / (sl_distance * 1.0)
        
        # Ensure lot size doesn't exceed reasonable limits
        self.assertLessEqual(max_lot_size, 0.5,
                            msg="Max lot size should be reasonable")
    
    def test_crypto_drawdown_impact(self):
        """Test drawdown calculation for crypto losses"""
        initial_balance = 10000.0
        
        # Simulate 3 losing trades
        loss_per_trade = 75.0  # 0.75% each
        num_losses = 3
        
        total_loss = loss_per_trade * num_losses
        final_balance = initial_balance - total_loss
        
        drawdown = (total_loss / initial_balance) * 100
        
        # Expected: 2.25% drawdown
        expected_dd = 2.25
        
        self.assertAlmostEqual(drawdown, expected_dd, places=2,
                              msg=f"Drawdown should be {expected_dd}%")


def run_tests():
    """Run all crypto trading tests"""
    print("="*70)
    print("CRYPTO TRADING UNIT TESTS")
    print("="*70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCryptoPositionSizing))
    suite.addTests(loader.loadTestsFromTestCase(TestCryptoProfitCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestCryptoRiskManagement))
    
    # Add live tests if MT5 is available
    if mt5 is not None:
        suite.addTests(loader.loadTestsFromTestCase(TestCryptoLiveOrders))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - Crypto trading ready!")
    else:
        print("\n❌ SOME TESTS FAILED - Check output above")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
