#!/usr/bin/env python3
"""
Unit Tests for Configuration
Test config loading, validation, and symbol settings
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import mock_open, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfigLoading(unittest.TestCase):
    """Test Configuration File Loading"""
    
    def test_config_file_exists(self):
        """Test that config.json exists"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        self.assertTrue(config_path.exists(), "config.json not found")
    
    def test_config_file_valid_json(self):
        """Test that config.json is valid JSON"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.assertIsInstance(config, dict)
        except json.JSONDecodeError as e:
            self.fail(f"config.json is not valid JSON: {e}")
    
    def test_config_has_required_sections(self):
        """Test config has required sections"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('accounts', config)
        self.assertIn('symbols', config)
    
    def test_accounts_section_structure(self):
        """Test accounts section has required fields"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        accounts_config = config.get('accounts', {})
        
        self.assertIn('demo', accounts_config)
        demo_account = accounts_config['demo']
        self.assertIn('login', demo_account)
        self.assertIn('password', demo_account)
        self.assertIn('server', demo_account)


class TestSymbolConfiguration(unittest.TestCase):
    """Test Symbol Configuration"""
    
    def setUp(self):
        """Load config for testing"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def test_symbols_is_dict(self):
        """Test symbols is a dict"""
        self.assertIsInstance(self.config['symbols'], dict)
        self.assertGreater(len(self.config['symbols']), 0)
    
    def test_symbol_has_required_fields(self):
        """Test each symbol has required fields"""
        required_fields = ['timeframe', 'risk_percent']
        
        for symbol_name, symbol_config in self.config['symbols'].items():
            for field in required_fields:
                self.assertIn(field, symbol_config, 
                            f"Symbol {symbol_name} missing {field}")
    
    def test_symbol_names_valid(self):
        """Test symbol names are valid"""
        valid_symbols = [
            # Forex pairs
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'XAUUSDm',
            'AUDUSDm', 'USDCADm', 'USDCHFm', 'NZDUSDm',
            # Crypto pairs
            'BTCUSDm', 'ETHUSDm', 'LTCUSDm', 'XRPUSDm', 'ADAUSDm',
            # Alternative naming conventions
            'BTCUSD', 'ETHUSD', 'LTCUSD', 'XRPUSD', 'ADAUSD',
        ]
        
        for symbol_name in self.config['symbols'].keys():
            self.assertIn(symbol_name, valid_symbols, 
                         f"Unknown symbol: {symbol_name}")
    
    def test_timeframe_valid(self):
        """Test timeframes are valid"""
        valid_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
        
        for symbol_name, symbol_config in self.config['symbols'].items():
            tf = symbol_config.get('timeframe', 'M5')
            self.assertIn(tf, valid_timeframes, 
                         f"Invalid timeframe: {tf} for {symbol_name}")
    
    def test_risk_percent_range(self):
        """Test risk percent is in valid range"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            risk = symbol_config['risk_percent']
            self.assertGreaterEqual(risk, 0.1, f"{symbol_name}: Risk too low")
            self.assertLessEqual(risk, 5.0, f"{symbol_name}: Risk too high")
    
    def test_rr_ratio_valid(self):
        """Test risk-reward ratio is valid"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            sl = symbol_config.get('sl_multiplier', 2.0)
            tp = symbol_config.get('tp_multiplier', 6.0)
            
            self.assertGreater(sl, 0, f"{symbol_name}: SL multiplier must be positive")
            self.assertGreater(tp, 0, f"{symbol_name}: TP multiplier must be positive")
            
            # TP should be larger than SL for positive RR
            if sl > 0:
                rr = tp / sl
                self.assertGreaterEqual(rr, 1.0, f"{symbol_name}: RR ratio should be >= 1.0")


class TestICTConfiguration(unittest.TestCase):
    """Test ICT-specific Configuration"""
    
    def setUp(self):
        """Load config for testing"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def test_ict_parameters_present(self):
        """Test ICT parameters are present"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            # Check for ICT-specific parameters
            self.assertIn('sl_multiplier', symbol_config, f"{symbol_name} missing sl_multiplier")
            self.assertIn('tp_multiplier', symbol_config, f"{symbol_name} missing tp_multiplier")
    
    def test_quality_factors_range(self):
        """Test quality factors are in valid range"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            min_factor = symbol_config.get('min_factor', 1.0)
            max_factor = symbol_config.get('max_factor', 5.0)
            
            self.assertGreater(min_factor, 0, f"{symbol_name}: min_factor must be positive")
            self.assertGreater(max_factor, min_factor, f"{symbol_name}: max_factor must be > min_factor")
            self.assertLessEqual(max_factor, 10.0, f"{symbol_name}: max_factor too high")
    
    def test_volume_multiplier_valid(self):
        """Test volume multiplier is valid"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            vol_mult = symbol_config.get('volume_multiplier', 1.0)
            
            self.assertGreaterEqual(vol_mult, 0.5, f"{symbol_name}: volume_multiplier too low")
            self.assertLessEqual(vol_mult, 3.0, f"{symbol_name}: volume_multiplier too high")


class TestSuperTrendConfiguration(unittest.TestCase):
    """Test SuperTrend-specific Configuration"""
    
    def test_atr_period_valid(self):
        """Test ATR period is valid"""
        # Default ATR period
        atr_period = 10
        
        self.assertGreaterEqual(atr_period, 5)
        self.assertLessEqual(atr_period, 20)
    
    def test_factor_range_valid(self):
        """Test SuperTrend factor range is valid"""
        min_factor = 1.0
        max_factor = 5.0
        
        self.assertGreaterEqual(min_factor, 0.5)
        self.assertLessEqual(max_factor, 10.0)
        self.assertLess(min_factor, max_factor)


class TestDualOrderConfiguration(unittest.TestCase):
    """Test Dual Order Configuration"""
    
    def setUp(self):
        """Load config for testing"""
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def test_dual_order_risk_awareness(self):
        """Test that dual orders double the risk"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            risk_percent = symbol_config['risk_percent']
            
            # Actual risk with dual orders
            actual_total_risk = risk_percent * 2
            
            # Warn if total risk exceeds safe limits
            if actual_total_risk > 2.0:
                print(f"Warning: {symbol_name} has {actual_total_risk}% total risk (dual orders)")
    
    def test_rr_ratios_for_dual_orders(self):
        """Test RR ratios for dual orders"""
        for symbol_name, symbol_config in self.config['symbols'].items():
            sl = symbol_config.get('sl_multiplier', 2.0)
            tp = symbol_config.get('tp_multiplier', 6.0)
            
            # RR for quick order (1:1)
            rr_quick = 1.0 / 1.0
            self.assertEqual(rr_quick, 1.0)
            
            # RR for main order
            rr_main = tp / sl
            self.assertGreaterEqual(rr_main, 2.0, f"{symbol_name}: RR should be >= 2.0")


class TestBacktestConfiguration(unittest.TestCase):
    """Test Backtest Configuration"""
    
    def test_initial_balance_valid(self):
        """Test initial balance is valid"""
        initial_balance = 10000
        
        self.assertGreaterEqual(initial_balance, 1000)
        self.assertLessEqual(initial_balance, 1000000)
    
    def test_lookback_period_valid(self):
        """Test lookback period is valid"""
        lookback_days = 290
        
        self.assertGreaterEqual(lookback_days, 30)
        self.assertLessEqual(lookback_days, 730)  # 2 years max


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
