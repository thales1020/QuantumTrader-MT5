"""
Example: Using Plugins with QuantumTrader-MT5

This example demonstrates how to use the plugin system
to extend bot functionality without modifying core code.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
from core.ict_bot import ICTBot, ICTConfig
from plugins.rsi_filter import RSIFilterPlugin
from plugins.volume_filter import VolumeFilterPlugin
from plugins.telegram_notifier import TelegramNotifierPlugin

print("="*70)
print("Plugin System Example - QuantumTrader-MT5")
print("="*70)
print()

# Example 1: Using RSI Filter Plugin
print("Example 1: RSI Filter Plugin")
print("-"*70)

# Create RSI filter plugin
rsi_plugin = RSIFilterPlugin(
    period=14,
    oversold=30,
    overbought=70,
    boost_confidence=True
)

# Configure bot with plugin
config = ICTConfig(
    symbol="AUDUSDm",
    timeframe=mt5.TIMEFRAME_H1,
    risk_percent=1.0,
    rr_ratio=2.0,
    plugins=[rsi_plugin]  # Add plugin to config
)

bot = ICTBot(config)

print(f"✓ Bot created with RSI filter plugin")
print(f"  - RSI period: {rsi_plugin.period}")
print(f"  - Oversold: {rsi_plugin.oversold}")
print(f"  - Overbought: {rsi_plugin.overbought}")
print()

# Example 2: Using Multiple Plugins
print("Example 2: Multiple Plugins (RSI + Volume)")
print("-"*70)

# Create multiple plugins
rsi_plugin = RSIFilterPlugin(period=14, oversold=30, overbought=70)
volume_plugin = VolumeFilterPlugin(multiplier=1.5, period=20)

# Bot with multiple plugins
config = ICTConfig(
    symbol="AUDUSDm",
    timeframe=mt5.TIMEFRAME_H1,
    risk_percent=1.0,
    plugins=[rsi_plugin, volume_plugin]
)

bot = ICTBot(config)

print(f"✓ Bot created with 2 plugins:")
print(f"  1. RSI Filter: Only oversold/overbought signals")
print(f"  2. Volume Filter: Minimum {volume_plugin.multiplier}x avg volume")
print()

# Example 3: Adding Plugin at Runtime
print("Example 3: Adding Plugin at Runtime")
print("-"*70)

# Create bot without plugins
config = ICTConfig(symbol="AUDUSDm")
bot = ICTBot(config)

print(f"✓ Bot created without plugins")

# Add plugin after initialization
volume_plugin = VolumeFilterPlugin(multiplier=2.0)
bot.plugin_manager.register(volume_plugin)

print(f"✓ Volume filter plugin added at runtime")
print()

# Example 4: Enabling/Disabling Plugins
print("Example 4: Enabling/Disabling Plugins")
print("-"*70)

rsi_plugin = RSIFilterPlugin()
volume_plugin = VolumeFilterPlugin()

config = ICTConfig(
    symbol="AUDUSDm",
    plugins=[rsi_plugin, volume_plugin]
)
bot = ICTBot(config)

print(f"✓ Bot with 2 plugins")
print(f"  Plugins: {[p['name'] for p in bot.plugin_manager.list_plugins()]}")

# Disable RSI filter
rsi_plugin.enabled = False
print(f"✓ RSI filter disabled")
print(f"  Active plugins: {[p['name'] for p in bot.plugin_manager.list_plugins() if p['enabled']]}")

# Re-enable
rsi_plugin.enabled = True
print(f"✓ RSI filter re-enabled")
print()

# Example 5: Telegram Notifications (requires setup)
print("Example 5: Telegram Notifications")
print("-"*70)
print("To use Telegram notifications:")
print("  1. Create bot with @BotFather on Telegram")
print("  2. Get your chat ID from @userinfobot")
print("  3. Configure plugin:")
print()
print("    telegram_plugin = TelegramNotifierPlugin(")
print("        bot_token='YOUR_BOT_TOKEN',")
print("        chat_id='YOUR_CHAT_ID'")
print("    )")
print()
print("    config = ICTConfig(")
print("        symbol='AUDUSDm',")
print("        plugins=[telegram_plugin]")
print("    )")
print()
print("  4. Bot will send notifications on trades!")
print()

# Example 6: Custom Plugin
print("Example 6: Creating a Custom Plugin")
print("-"*70)
print("To create your own plugin:")
print()
print("    from core.plugin_system import BasePlugin")
print()
print("    class MyCustomPlugin(BasePlugin):")
print("        def __init__(self):")
print("            super().__init__(name='MyPlugin')")
print()
print("        def on_signal(self, signal, df):")
print("            # Your custom logic here")
print("            if signal:")
print("                signal['confidence'] += 10")
print("            return signal")
print()
print("Then use it:")
print()
print("    my_plugin = MyCustomPlugin()")
print("    bot.plugin_manager.register(my_plugin)")
print()

print("="*70)
print("For more information, see:")
print("  - docs/PLUGIN_SYSTEM.md")
print("  - plugins/rsi_filter.py (example implementation)")
print("  - tests/test_plugin_system.py (usage examples)")
print("="*70)
