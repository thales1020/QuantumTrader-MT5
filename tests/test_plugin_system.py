#!/usr/bin/env python3
"""
Unit Tests for Plugin System
Test-Driven Development: Write tests FIRST, then implement
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# These imports will fail initially - that's OK in TDD!
# We write tests first, then implement the classes
try:
    from core.plugin_system import BasePlugin, PluginManager, PluginError
except ImportError:
    print("⚠️ Plugin system not implemented yet - tests will fail")
    print("This is expected in TDD! Implement the code to make tests pass.")


class TestBasePlugin(unittest.TestCase):
    """Test BasePlugin abstract class"""
    
    def test_plugin_initialization(self):
        """Test plugin can be initialized with name"""
        # This will fail until we implement BasePlugin
        plugin = BasePlugin(name="TestPlugin")
        
        self.assertEqual(plugin.name, "TestPlugin")
        self.assertTrue(plugin.enabled)
        self.assertIsNone(plugin.bot)
    
    def test_plugin_disabled_state(self):
        """Test plugin can be disabled"""
        plugin = BasePlugin(name="TestPlugin", enabled=False)
        self.assertFalse(plugin.enabled)
    
    def test_plugin_on_init_sets_bot(self):
        """Test on_init sets bot reference"""
        plugin = BasePlugin(name="TestPlugin")
        mock_bot = Mock()
        
        plugin.on_init(mock_bot)
        
        self.assertEqual(plugin.bot, mock_bot)
    
    def test_plugin_hooks_return_passthrough_by_default(self):
        """Test default hook implementations don't modify data"""
        plugin = BasePlugin(name="TestPlugin")
        
        # Create test data
        df = pd.DataFrame({'close': [1.0, 2.0, 3.0]})
        signal = {'type': 'BUY', 'price': 1.0}
        
        # Default implementations should return unchanged
        self.assertEqual(plugin.on_data(df).equals(df), True)
        self.assertEqual(plugin.on_signal(signal, df), signal)
    
    def test_plugin_on_shutdown_callable(self):
        """Test on_shutdown can be called"""
        plugin = BasePlugin(name="TestPlugin")
        # Should not raise
        plugin.on_shutdown()


class TestPluginManager(unittest.TestCase):
    """Test PluginManager"""
    
    def setUp(self):
        """Create mock bot for testing"""
        self.mock_bot = Mock()
    
    def test_manager_initialization(self):
        """Test PluginManager can be initialized"""
        manager = PluginManager(self.mock_bot)
        
        self.assertEqual(manager.bot, self.mock_bot)
        self.assertEqual(len(manager.plugins), 0)
    
    def test_register_plugin(self):
        """Test registering a plugin"""
        manager = PluginManager(self.mock_bot)
        plugin = Mock(spec=BasePlugin)
        plugin.name = "TestPlugin"
        plugin.enabled = True
        
        manager.register(plugin)
        
        # Plugin should be registered
        self.assertEqual(len(manager.plugins), 1)
        self.assertIn(plugin, manager.plugins)
        
        # on_init should have been called
        plugin.on_init.assert_called_once_with(self.mock_bot)
    
    def test_register_multiple_plugins(self):
        """Test registering multiple plugins"""
        manager = PluginManager(self.mock_bot)
        
        plugin1 = Mock(spec=BasePlugin)
        plugin1.name = "Plugin1"
        plugin1.enabled = True
        
        plugin2 = Mock(spec=BasePlugin)
        plugin2.name = "Plugin2"
        plugin2.enabled = True
        
        manager.register(plugin1)
        manager.register(plugin2)
        
        self.assertEqual(len(manager.plugins), 2)
    
    def test_run_hook_on_data(self):
        """Test running on_data hook"""
        manager = PluginManager(self.mock_bot)
        
        # Create mock plugin that modifies data
        plugin = Mock(spec=BasePlugin)
        plugin.name = "TestPlugin"
        plugin.enabled = True
        plugin.on_data = Mock(side_effect=lambda df: df)  # Passthrough
        
        manager.register(plugin)
        
        # Run hook
        df = pd.DataFrame({'close': [1.0, 2.0, 3.0]})
        result = manager.run_hook('on_data', df)
        
        # Plugin should have been called
        plugin.on_data.assert_called_once()
        self.assertIsNotNone(result)
    
    def test_run_hook_on_signal(self):
        """Test running on_signal hook"""
        manager = PluginManager(self.mock_bot)
        
        plugin = Mock(spec=BasePlugin)
        plugin.name = "TestPlugin"
        plugin.enabled = True
        signal_input = {'type': 'BUY', 'price': 1.0}
        plugin.on_signal = Mock(return_value=signal_input)
        
        manager.register(plugin)
        
        # Run hook
        df = pd.DataFrame({'close': [1.0]})
        result = manager.run_hook('on_signal', signal_input, df)
        
        plugin.on_signal.assert_called_once()
        self.assertEqual(result, signal_input)
    
    def test_run_hook_signal_rejection(self):
        """Test plugin can reject signal by returning None"""
        manager = PluginManager(self.mock_bot)
        
        # Plugin that rejects signal
        plugin = Mock(spec=BasePlugin)
        plugin.name = "RejectPlugin"
        plugin.enabled = True
        plugin.on_signal = Mock(return_value=None)
        
        manager.register(plugin)
        
        signal = {'type': 'BUY', 'price': 1.0}
        df = pd.DataFrame({'close': [1.0]})
        result = manager.run_hook('on_signal', signal, df)
        
        # Signal should be None (rejected)
        self.assertIsNone(result)
    
    def test_run_hook_chain_multiple_plugins(self):
        """Test signal passes through multiple plugins"""
        manager = PluginManager(self.mock_bot)
        
        # Plugin 1: Adds confidence field
        plugin1 = Mock(spec=BasePlugin)
        plugin1.name = "Plugin1"
        plugin1.enabled = True
        def add_confidence(signal, df):
            signal['confidence'] = 50
            return signal
        plugin1.on_signal = Mock(side_effect=add_confidence)
        
        # Plugin 2: Increases confidence
        plugin2 = Mock(spec=BasePlugin)
        plugin2.name = "Plugin2"
        plugin2.enabled = True
        def increase_confidence(signal, df):
            signal['confidence'] += 20
            return signal
        plugin2.on_signal = Mock(side_effect=increase_confidence)
        
        manager.register(plugin1)
        manager.register(plugin2)
        
        # Run hook
        signal = {'type': 'BUY', 'price': 1.0}
        df = pd.DataFrame({'close': [1.0]})
        result = manager.run_hook('on_signal', signal, df)
        
        # Both plugins should have modified signal
        self.assertEqual(result['confidence'], 70)
    
    def test_disabled_plugin_not_executed(self):
        """Test disabled plugins are skipped"""
        manager = PluginManager(self.mock_bot)
        
        plugin = Mock(spec=BasePlugin)
        plugin.name = "DisabledPlugin"
        plugin.enabled = False
        plugin.on_signal = Mock()
        
        manager.register(plugin)
        
        signal = {'type': 'BUY'}
        df = pd.DataFrame({'close': [1.0]})
        manager.run_hook('on_signal', signal, df)
        
        # Plugin should NOT have been called (disabled)
        plugin.on_signal.assert_not_called()
    
    def test_plugin_error_handling(self):
        """Test plugin errors don't crash manager"""
        manager = PluginManager(self.mock_bot)
        
        # Plugin that raises error
        plugin = Mock(spec=BasePlugin)
        plugin.name = "ErrorPlugin"
        plugin.enabled = True
        plugin.on_signal = Mock(side_effect=Exception("Plugin error"))
        plugin.on_error = Mock()
        
        manager.register(plugin)
        
        signal = {'type': 'BUY'}
        df = pd.DataFrame({'close': [1.0]})
        
        # Should not raise, should continue
        result = manager.run_hook('on_signal', signal, df)
        
        # Error handler should have been called
        plugin.on_error.assert_called_once()
    
    def test_shutdown_all_plugins(self):
        """Test shutdown calls on_shutdown on all plugins"""
        manager = PluginManager(self.mock_bot)
        
        plugin1 = Mock(spec=BasePlugin)
        plugin1.name = "Plugin1"
        plugin1.enabled = True
        
        plugin2 = Mock(spec=BasePlugin)
        plugin2.name = "Plugin2"
        plugin2.enabled = True
        
        manager.register(plugin1)
        manager.register(plugin2)
        
        manager.shutdown()
        
        plugin1.on_shutdown.assert_called_once()
        plugin2.on_shutdown.assert_called_once()


class TestExamplePlugins(unittest.TestCase):
    """Test example plugin implementations"""
    
    def test_rsi_filter_plugin(self):
        """Test RSI filter plugin (will implement later)"""
        # This test defines the interface we expect
        # Implementation comes after
        pass
    
    def test_volume_filter_plugin(self):
        """Test volume filter plugin"""
        pass
    
    def test_telegram_notifier_plugin(self):
        """Test Telegram notifier plugin"""
        pass


class TestPluginIntegration(unittest.TestCase):
    """Test plugin integration with BaseTradingBot"""
    
    def test_bot_initializes_plugin_manager(self):
        """Test bot creates plugin manager on init"""
        # Will test after integrating with BaseTradingBot
        pass
    
    def test_bot_loads_plugins_from_config(self):
        """Test bot loads plugins from config.plugins"""
        pass
    
    def test_bot_calls_on_data_hook(self):
        """Test bot calls on_data during calculate_indicators"""
        pass
    
    def test_bot_calls_on_signal_hook(self):
        """Test bot calls on_signal during generate_signal"""
        pass
    
    def test_bot_calls_on_trade_open_hook(self):
        """Test bot calls on_trade_open after executing trade"""
        pass


def run_tests():
    """Run all tests with verbose output"""
    print("="*70)
    print("PLUGIN SYSTEM TESTS - TDD Mode")
    print("="*70)
    print("These tests will FAIL initially - that's expected!")
    print("Implement the code to make them pass.")
    print("="*70)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        print("Plugin system is ready for production!")
    else:
        print("\n❌ TESTS FAILED")
        print("Implement the code to make tests pass.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
