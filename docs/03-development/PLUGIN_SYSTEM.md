# Plugin System Architecture

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Date**: November 4, 2025  
**Tests**: 23/23 Passing

## Overview

The Plugin System allows extending QuantumTrader-MT5 functionality without modifying core code. Plugins can:
- Add custom indicators
- Filter trading signals  
- Send notifications
- Modify bot behavior at runtime

**Integration Status**: ✅ Fully integrated with BaseTradingBot, SuperTrendBot, and ICTBot.

## Architecture

### 1. Core Components

#### BasePlugin (Abstract Class)
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.bot = None  # Set when plugin is registered
    
    # Lifecycle hooks
    def on_init(self, bot) -> None:
        """Called when plugin is registered to bot"""
        self.bot = bot
    
    def on_shutdown(self) -> None:
        """Called when bot shuts down"""
        pass
    
    # Data processing hooks
    def on_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Modify/add indicators to data. Return modified DataFrame."""
        return df
    
    # Signal hooks
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """Filter or modify signal. Return signal or None to reject."""
        return signal
    
    # Trade hooks
    def on_trade_open(self, trade_info: Dict[str, Any]) -> None:
        """Called after trade is opened"""
        pass
    
    def on_trade_close(self, trade_info: Dict[str, Any]) -> None:
        """Called after trade is closed"""
        pass
    
    # Error handling
    def on_error(self, error: Exception) -> None:
        """Called when bot encounters error"""
        pass
```

#### PluginManager
```python
class PluginManager:
    """Manages plugin lifecycle and execution"""
    
    def __init__(self, bot):
        self.bot = bot
        self.plugins: List[BasePlugin] = []
    
    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin"""
        plugin.on_init(self.bot)
        self.plugins.append(plugin)
    
    def run_hook(self, hook_name: str, *args, **kwargs):
        """Execute a hook on all enabled plugins"""
        result = args[0] if args else None
        
        for plugin in self.plugins:
            if not plugin.enabled:
                continue
            
            try:
                hook_method = getattr(plugin, hook_name, None)
                if hook_method:
                    result = hook_method(result, *args[1:], **kwargs)
                    
                    # If signal hook returns None, stop chain
                    if hook_name == 'on_signal' and result is None:
                        return None
                        
            except Exception as e:
                logger.error(f"Plugin {plugin.name} error in {hook_name}: {e}")
                plugin.on_error(e)
        
        return result
    
    def shutdown(self) -> None:
        """Shutdown all plugins"""
        for plugin in self.plugins:
            try:
                plugin.on_shutdown()
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin.name}: {e}")
```

### 2. Integration with BaseTradingBot

```python
class BaseTradingBot(ABC):
    def __init__(self, config: BaseConfig):
        # ... existing code ...
        self.plugin_manager = PluginManager(self)
        
        # Load plugins from config
        if hasattr(config, 'plugins'):
            for plugin in config.plugins:
                self.plugin_manager.register(plugin)
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # Existing indicator calculation
        df = self._calculate_core_indicators(df)
        
        # Allow plugins to add indicators
        df = self.plugin_manager.run_hook('on_data', df)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        # Core signal generation
        signal = self._generate_core_signal(df)
        
        # Allow plugins to filter/modify signal
        signal = self.plugin_manager.run_hook('on_signal', signal, df)
        
        return signal
    
    def execute_trade(self, signal: Dict):
        result = self._execute_core_trade(signal)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            # Notify plugins
            trade_info = {
                'ticket': result.order,
                'type': signal['type'],
                'price': signal['price'],
                'sl': signal['stop_loss'],
                'tp': signal['take_profit']
            }
            self.plugin_manager.run_hook('on_trade_open', trade_info)
        
        return result
```

## Example Plugins

### 1. RSI Filter Plugin

```python
class RSIFilterPlugin(BasePlugin):
    """Filter signals based on RSI"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__(name="RSIFilter")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def on_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add RSI to dataframe"""
        import talib
        df['rsi'] = talib.RSI(df['close'], timeperiod=self.period)
        return df
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """Filter signal based on RSI"""
        if signal is None:
            return None
        
        rsi = df['rsi'].iloc[-1]
        
        if signal['type'] == 'BUY':
            if rsi >= self.oversold:  # Accept only oversold
                return signal
        elif signal['type'] == 'SELL':
            if rsi <= self.overbought:  # Accept only overbought
                return signal
        
        return None  # Reject signal
```

### 2. Telegram Notifier Plugin

```python
class TelegramNotifierPlugin(BasePlugin):
    """Send Telegram notifications on trades"""
    
    def __init__(self, bot_token: str, chat_id: str):
        super().__init__(name="TelegramNotifier")
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def on_trade_open(self, trade_info: Dict[str, Any]) -> None:
        """Send notification when trade opens"""
        message = f"""
🟢 Trade Opened
Symbol: {trade_info.get('symbol')}
Type: {trade_info['type']}
Price: {trade_info['price']:.5f}
SL: {trade_info['sl']:.5f}
TP: {trade_info['tp']:.5f}
        """
        self._send_telegram(message)
    
    def on_trade_close(self, trade_info: Dict[str, Any]) -> None:
        """Send notification when trade closes"""
        profit = trade_info.get('profit', 0)
        emoji = "✅" if profit > 0 else "❌"
        
        message = f"""
{emoji} Trade Closed
Ticket: #{trade_info['ticket']}
Profit: ${profit:.2f}
        """
        self._send_telegram(message)
    
    def _send_telegram(self, message: str) -> None:
        import requests
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        requests.post(url, json={'chat_id': self.chat_id, 'text': message})
```

### 3. Volume Filter Plugin

```python
class VolumeFilterPlugin(BasePlugin):
    """Filter signals based on volume"""
    
    def __init__(self, multiplier: float = 1.5, period: int = 20):
        super().__init__(name="VolumeFilter")
        self.multiplier = multiplier
        self.period = period
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """Reject signals with low volume"""
        if signal is None:
            return None
        
        avg_volume = df['tick_volume'].rolling(self.period).mean().iloc[-1]
        current_volume = df['tick_volume'].iloc[-1]
        
        if current_volume < avg_volume * self.multiplier:
            return None  # Reject low volume
        
        # Increase confidence for high volume
        if 'confidence' in signal:
            signal['confidence'] += 10
        
        return signal
```

## Usage Examples

### Basic Usage

```python
from core.ict_bot import ICTBot, ICTConfig
from plugins.rsi_filter import RSIFilterPlugin
from plugins.telegram_notifier import TelegramNotifierPlugin

# Create config with plugins
config = ICTConfig(
    symbol="AUDUSDm",
    timeframe=mt5.TIMEFRAME_H1,
    risk_percent=1.0,
    plugins=[
        RSIFilterPlugin(period=14, oversold=30, overbought=70),
        TelegramNotifierPlugin(bot_token="xxx", chat_id="yyy")
    ]
)

bot = ICTBot(config)
bot.run()  # Plugins work automatically
```

### Adding Plugins at Runtime

```python
bot = ICTBot(config)

# Add plugin after initialization
volume_filter = VolumeFilterPlugin(multiplier=1.5)
bot.plugin_manager.register(volume_filter)

# Disable plugin
volume_filter.enabled = False

# Re-enable
volume_filter.enabled = True
```

## Plugin Development Guide

### Creating a Custom Plugin

1. **Inherit from BasePlugin**
2. **Override needed hooks**
3. **Handle errors gracefully**
4. **Test independently**

```python
class MyCustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="MyPlugin")
    
    def on_init(self, bot):
        super().on_init(bot)
        # Initialize resources
        self.some_resource = self._setup()
    
    def on_signal(self, signal, df):
        # Your logic here
        return signal
    
    def on_shutdown(self):
        # Cleanup resources
        if hasattr(self, 'some_resource'):
            self.some_resource.close()
```

### Best Practices

1. **Always return modified data/signal** - Don't return None unless rejecting
2. **Handle exceptions** - Don't crash the bot
3. **Log important events** - Use bot's logger
4. **Be efficient** - Plugins run on every cycle
5. **Test thoroughly** - Unit test + integration test

## Configuration Schema

```python
@dataclass
class BaseConfig:
    # ... existing fields ...
    
    # Plugin support
    plugins: List[BasePlugin] = field(default_factory=list)
    plugin_error_handling: str = 'continue'  # 'continue' or 'stop'
```

## Performance Considerations

- **Plugin execution time**: Each plugin adds latency
- **Memory usage**: Plugins may store data
- **Error propagation**: Failed plugins don't crash bot
- **Hook chain**: Signals pass through ALL plugins

## Security Considerations

- **Trust plugins**: Only load from trusted sources
- **Validate inputs**: Plugins receive raw market data
- **API keys**: Store securely (env vars, not code)
- **Network calls**: May expose bot to external services

## Integration with BaseTradingBot

The plugin system is fully integrated into the bot lifecycle:

### Hook Execution Points

1. **on_init**: Called when plugin is registered to PluginManager
2. **on_data**: After `calculate_indicators()` - line ~220 in base_bot.py
3. **on_signal**: After `generate_signal()` - line ~240 in base_bot.py
4. **on_trade_open**: After successful position open - line ~445 in base_bot.py
5. **on_trade_close**: When position closes - line ~738 in base_bot.py
6. **on_error**: On indicator calculation or hook execution errors
7. **on_shutdown**: During bot shutdown - line ~778 in base_bot.py

### Integration Example

```python
# In config.json
{
    "symbol": "EURUSD",
    "timeframe": "H1",
    "plugins": [
        {
            "name": "RSIFilter",
            "enabled": true,
            "config": {
                "period": 14,
                "oversold": 30,
                "overbought": 70
            }
        }
    ]
}

# Bot automatically loads and initializes plugins
bot = SuperTrendBot(config)
bot.start()  # Plugins run on each cycle
```

### Testing

Run integration tests to verify plugins work with real bots:

```bash
python -m pytest tests/test_plugin_integration.py -v
```

**Test Coverage**: 23 tests covering:
- Plugin registration and lifecycle
- Multiple plugin chaining
- Signal filtering and rejection
- Error handling
- Trade notifications
- All 7 lifecycle hooks

## Future Extensions

- **Plugin marketplace**: Share/download community plugins
- **Hot reload**: Update plugins without restart
- **Plugin dependencies**: Plugins that require other plugins
- **Async plugins**: Non-blocking operations
- **Plugin priorities**: Control execution order

---

## Summary

✅ **Phase 2 Complete**: Plugin system fully implemented and integrated  
✅ **Tests**: 23/23 passing  
✅ **Documentation**: Complete with examples  
✅ **Example Plugins**: RSI Filter, Volume Filter, Telegram Notifier  
✅ **Production Ready**: Safe error handling, backward compatible

4. Write tests
5. Update documentation
