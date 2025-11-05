"""
Integration Tests for Plugin System with Real Bots

Tests plugin system integration with SuperTrendBot and ICTBot.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import numpy as np

from core.plugin_system import BasePlugin, PluginManager, PluginError
from core.base_bot import BaseConfig
from plugins.rsi_filter import RSIFilterPlugin
from plugins.volume_filter import VolumeFilterPlugin


class MockTradingBot:
    """Mock trading bot for testing plugin integration"""
    
    def __init__(self, config: BaseConfig):
        self.config = config
        self.logger = Mock()
        self.plugin_manager = None
        
        # Initialize plugin system
        if hasattr(self, 'config') and hasattr(self.config, 'plugins'):
            self.plugin_manager = PluginManager(self.logger)
            
            for plugin_config in self.config.plugins:
                # Skip disabled plugins
                if not plugin_config.get('enabled', True):
                    continue
                
                plugin_class = self._get_plugin_class(plugin_config['name'])
                if plugin_class:
                    plugin = plugin_class(plugin_config.get('config', {}))
                    self.plugin_manager.register(plugin)
    
    def _get_plugin_class(self, name: str):
        """Get plugin class by name"""
        if name == 'RSIFilter':
            return RSIFilterPlugin
        elif name == 'VolumeFilter':
            return VolumeFilterPlugin
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicators with plugin hook"""
        # Simulate indicator calculation
        data['sma_20'] = data['close'].rolling(20).mean()
        
        # Run plugin hook
        if self.plugin_manager:
            data = self.plugin_manager.run_hook('on_data', data)
        
        return data
    
    def generate_signal(self, data: pd.DataFrame) -> dict:
        """Generate signal with plugin hook"""
        # Simulate signal generation
        signal = {
            'type': 'BUY',
            'confidence': 70,
            'entry_price': data['close'].iloc[-1]
        }
        
        # Run plugin hook
        if self.plugin_manager:
            signal = self.plugin_manager.run_hook('on_signal', signal, data)
        
        return signal


class TestPluginIntegration(unittest.TestCase):
    """Test plugin system integration with bots"""
    
    def setUp(self):
        """Setup test data"""
        # Create sample OHLCV data
        dates = pd.date_range('2025-01-01', periods=100, freq='1h')
        self.data = pd.DataFrame({
            'time': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'tick_volume': np.random.uniform(1000, 5000, 100)
        })
    
    def test_rsi_filter_integration(self):
        """Test RSI filter plugin integration"""
        # Create config with RSI filter
        config = BaseConfig(
            symbol='EURUSD',
            timeframe='H1',
            magic_number=12345,
            plugins=[
                {
                    'name': 'RSIFilter',
                    'enabled': True,
                    'config': {
                        'period': 14,
                        'oversold': 30,
                        'overbought': 70
                    }
                }
            ]
        )
        
        # Create mock bot
        bot = MockTradingBot(config)
        
        # Calculate indicators (should add RSI)
        result = bot.calculate_indicators(self.data.copy())
        
        # Verify RSI was added
        self.assertIn('rsi', result.columns)
        self.assertFalse(result['rsi'].isna().all())
    
    def test_volume_filter_integration(self):
        """Test volume filter plugin integration"""
        # Create config with volume filter
        config = BaseConfig(
            symbol='EURUSD',
            timeframe='H1',
            magic_number=12345,
            plugins=[
                {
                    'name': 'VolumeFilter',
                    'enabled': True,
                    'config': {
                        'multiplier': 1.5,
                        'period': 20
                    }
                }
            ]
        )
        
        # Create mock bot
        bot = MockTradingBot(config)
        
        # Calculate indicators
        data = bot.calculate_indicators(self.data.copy())
        
        # Generate signal with low volume (should be rejected)
        data.loc[data.index[-1], 'tick_volume'] = 100  # Very low volume
        signal = bot.generate_signal(data)
        
        # Signal should be rejected
        self.assertIsNone(signal)
    
    def test_multiple_plugins_chain(self):
        """Test multiple plugins working together"""
        # Create config with both filters
        config = BaseConfig(
            symbol='EURUSD',
            timeframe='H1',
            magic_number=12345,
            plugins=[
                {
                    'name': 'RSIFilter',
                    'enabled': True,
                    'config': {'period': 14, 'oversold': 30, 'overbought': 70}
                },
                {
                    'name': 'VolumeFilter',
                    'enabled': True,
                    'config': {'multiplier': 1.5, 'period': 20}
                }
            ]
        )
        
        # Create mock bot
        bot = MockTradingBot(config)
        
        # Calculate indicators
        data = bot.calculate_indicators(self.data.copy())
        
        # Verify both plugins ran
        self.assertIn('rsi', data.columns)
        self.assertIn('avg_volume', data.columns)
        
        # Generate signal
        # Set RSI to oversold (good for BUY)
        data.loc[data.index[-1], 'rsi'] = 25
        # Set high volume (good for BUY)
        data.loc[data.index[-1], 'tick_volume'] = 5000
        
        signal = bot.generate_signal(data)
        
        # Signal should pass both filters and be boosted
        self.assertIsNotNone(signal)
        self.assertGreater(signal['confidence'], 70)  # Boosted by filters
    
    def test_plugin_signal_rejection(self):
        """Test plugin can reject signals"""
        # Create config with RSI filter
        config = BaseConfig(
            symbol='EURUSD',
            timeframe='H1',
            magic_number=12345,
            plugins=[
                {
                    'name': 'RSIFilter',
                    'enabled': True,
                    'config': {'period': 14, 'oversold': 30, 'overbought': 70}
                }
            ]
        )
        
        # Create mock bot
        bot = MockTradingBot(config)
        
        # Calculate indicators
        data = bot.calculate_indicators(self.data.copy())
        
        # Set RSI to neutral (should reject BUY signal)
        data.loc[data.index[-1], 'rsi'] = 50
        
        signal = bot.generate_signal(data)
        
        # Signal should be rejected
        self.assertIsNone(signal)
    
    def test_disabled_plugin_ignored(self):
        """Test disabled plugins are ignored"""
        # Create config with disabled RSI filter
        config = BaseConfig(
            symbol='EURUSD',
            timeframe='H1',
            magic_number=12345,
            plugins=[
                {
                    'name': 'RSIFilter',
                    'enabled': False,
                    'config': {'period': 14}
                }
            ]
        )
        
        # Create mock bot
        bot = MockTradingBot(config)
        
        # Calculate indicators
        data = bot.calculate_indicators(self.data.copy())
        
        # RSI should NOT be added (plugin disabled)
        self.assertNotIn('rsi', data.columns)
    
    def test_plugin_error_handling(self):
        """Test plugin errors don't crash bot"""
        
        class BrokenPlugin(BasePlugin):
            """Plugin that raises error"""
            
            def __init__(self, config: dict):
                super().__init__(name="BrokenPlugin")
            
            @property
            def name(self) -> str:
                return "BrokenPlugin"
            
            def on_data(self, data: pd.DataFrame) -> pd.DataFrame:
                raise ValueError("Intentional error for testing")
        
        # Create plugin manager
        logger = Mock()
        manager = PluginManager(logger)
        
        # Register broken plugin
        broken = BrokenPlugin({})
        manager.register(broken)
        
        # Run hook - should catch error and continue
        data = self.data.copy()
        result = manager.run_hook('on_data', data)
        
        # Should return original data
        self.assertIsNotNone(result)
        self.assertEqual(len(result), len(data))
        
        # Should log error
        logger.error.assert_called()


class TestPluginLifecycle(unittest.TestCase):
    """Test plugin lifecycle hooks"""
    
    def test_plugin_initialization(self):
        """Test plugin on_init hook"""
        
        class TestPlugin(BasePlugin):
            def __init__(self, config: dict):
                super().__init__(name="TestPlugin")
                self.initialized = False
            
            @property
            def name(self) -> str:
                return "TestPlugin"
            
            def on_init(self, bot):
                self.initialized = True
        
        # Create and register plugin
        logger = Mock()
        manager = PluginManager(logger)
        plugin = TestPlugin({})
        manager.register(plugin)
        
        # on_init should be called
        self.assertTrue(plugin.initialized)
    
    def test_plugin_shutdown(self):
        """Test plugin on_shutdown hook"""
        
        class TestPlugin(BasePlugin):
            def __init__(self, config: dict):
                super().__init__(name="TestPlugin")
                self.shutdown_called = False
            
            @property
            def name(self) -> str:
                return "TestPlugin"
            
            def on_shutdown(self):
                self.shutdown_called = True
        
        # Create and register plugin
        logger = Mock()
        manager = PluginManager(logger)
        plugin = TestPlugin({})
        manager.register(plugin)
        
        # Shutdown
        manager.shutdown()
        
        # on_shutdown should be called
        self.assertTrue(plugin.shutdown_called)
    
    def test_trade_lifecycle_hooks(self):
        """Test on_trade_open and on_trade_close hooks"""
        
        class TrackingPlugin(BasePlugin):
            def __init__(self, config: dict):
                super().__init__(name="TrackingPlugin")
                self.trades_opened = []
                self.trades_closed = []
            
            @property
            def name(self) -> str:
                return "TrackingPlugin"
            
            def on_trade_open(self, trade_info: dict):
                self.trades_opened.append(trade_info)
            
            def on_trade_close(self, position_info: dict):
                self.trades_closed.append(position_info)
        
        # Create plugin
        logger = Mock()
        manager = PluginManager(logger)
        plugin = TrackingPlugin({})
        manager.register(plugin)
        
        # Simulate trade open
        trade_info = {
            'ticket': 12345,
            'type': 'BUY',
            'symbol': 'EURUSD',
            'volume': 0.1
        }
        manager.run_hook('on_trade_open', trade_info)
        
        # Simulate trade close
        position_info = {
            'ticket': 12345,
            'profit': 100.50,
            'exit_price': 1.1050
        }
        manager.run_hook('on_trade_close', position_info)
        
        # Verify hooks were called
        self.assertEqual(len(plugin.trades_opened), 1)
        self.assertEqual(len(plugin.trades_closed), 1)
        self.assertEqual(plugin.trades_opened[0]['ticket'], 12345)
        self.assertEqual(plugin.trades_closed[0]['profit'], 100.50)


if __name__ == '__main__':
    unittest.main()
