"""
Example Plugins for QuantumTrader-MT5

This package contains example plugins demonstrating
the plugin system capabilities.
"""

from .rsi_filter import RSIFilterPlugin
from .volume_filter import VolumeFilterPlugin
from .telegram_notifier import TelegramNotifierPlugin

__all__ = [
    'RSIFilterPlugin',
    'VolumeFilterPlugin',
    'TelegramNotifierPlugin',
]
