"""
Plugin System for QuantumTrader-MT5

Provides extensibility through plugins that can:
- Add custom indicators
- Filter signals
- Send notifications
- Modify bot behavior

Author: Trần Trọng Hiếu (@thales1020)
Date: November 4, 2025
Version: 2.0.0
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Base exception for plugin-related errors"""
    pass


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Plugins can hook into bot lifecycle at various points:
    - on_init: When plugin is registered
    - on_data: Modify/add indicators to data
    - on_signal: Filter or modify signals
    - on_trade_open: Notification when trade opens
    - on_trade_close: Notification when trade closes
    - on_error: Handle errors
    - on_shutdown: Cleanup resources
    
    Example:
        >>> class MyPlugin(BasePlugin):
        ...     def on_signal(self, signal, df):
        ...         if signal and signal['confidence'] < 50:
        ...             return None  # Reject low confidence
        ...         return signal
    """
    
    def __init__(self, name: str = None, enabled: bool = True):
        """
        Initialize plugin.
        
        Args:
            name: Unique plugin name (can be overridden by @property)
            enabled: Whether plugin is active
        """
        self._name = name
        self.enabled = enabled
        self.bot = None
    
    @property
    def name(self) -> str:
        """Get plugin name (can be overridden in subclass)"""
        return self._name
    
    def on_init(self, bot) -> None:
        """
        Called when plugin is registered to bot.
        
        Args:
            bot: The trading bot instance
        """
        self.bot = bot
        logger.info(f"Plugin '{self.name}' initialized")
    
    def on_shutdown(self) -> None:
        """
        Called when bot shuts down.
        Use for cleanup (close files, connections, etc.)
        """
        logger.info(f"Plugin '{self.name}' shutting down")
    
    def on_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Modify or add indicators to data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Modified DataFrame (must return df, not None)
        
        Example:
            >>> def on_data(self, df):
            ...     df['my_indicator'] = calculate_indicator(df)
            ...     return df
        """
        return df
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """
        Filter or modify trading signal.
        
        Args:
            signal: Signal dict or None
            df: DataFrame with market data
            
        Returns:
            Modified signal or None to reject
        
        Example:
            >>> def on_signal(self, signal, df):
            ...     if signal and df['volume'].iloc[-1] < 1000:
            ...         return None  # Reject low volume
            ...     return signal
        """
        return signal
    
    def on_trade_open(self, trade_info: Dict[str, Any]) -> None:
        """
        Called after trade is opened.
        
        Args:
            trade_info: Dict with trade details (ticket, type, price, sl, tp)
        """
        pass
    
    def on_trade_close(self, trade_info: Dict[str, Any]) -> None:
        """
        Called after trade is closed.
        
        Args:
            trade_info: Dict with trade details and profit/loss
        """
        pass
    
    def on_error(self, error: Exception) -> None:
        """
        Called when plugin encounters error.
        
        Args:
            error: The exception that occurred
        """
        logger.error(f"Plugin '{self.name}' error: {error}")


class PluginManager:
    """
    Manages plugin lifecycle and execution.
    
    The PluginManager coordinates running hooks across all registered plugins.
    It handles errors gracefully to prevent plugins from crashing the bot.
    
    Example:
        >>> manager = PluginManager(bot)
        >>> manager.register(RSIFilterPlugin())
        >>> manager.register(TelegramNotifierPlugin())
        >>> 
        >>> # Run hooks
        >>> df = manager.run_hook('on_data', df)
        >>> signal = manager.run_hook('on_signal', signal, df)
    """
    
    def __init__(self, bot):
        """
        Initialize plugin manager.
        
        Args:
            bot: The trading bot instance or logger
        """
        self.bot = bot
        # Use bot as logger if it has logging methods, otherwise use module logger
        if hasattr(bot, 'error') and hasattr(bot, 'info'):
            self.logger = bot
        else:
            self.logger = logger
        self.plugins: List[BasePlugin] = []
        self.logger.info("PluginManager initialized")
    
    def register(self, plugin: BasePlugin) -> None:
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance to register
            
        Raises:
            PluginError: If plugin is invalid
        """
        if not isinstance(plugin, BasePlugin):
            raise PluginError(f"Plugin must inherit from BasePlugin, got {type(plugin)}")
        
        # Initialize plugin
        try:
            plugin.on_init(self.bot)
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin '{plugin.name}': {e}")
            raise PluginError(f"Plugin initialization failed") from e
        
        # Register
        self.plugins.append(plugin)
        self.logger.info(f"Registered plugin: {plugin.name} (enabled={plugin.enabled})")
    
    def run_hook(self, hook_name: str, *args, **kwargs):
        """
        Execute a hook on all enabled plugins.
        
        Plugins are called in registration order. If a plugin in the 'on_signal'
        hook returns None, the chain stops and None is returned (signal rejected).
        
        Args:
            hook_name: Name of hook method (e.g., 'on_data', 'on_signal')
            *args: Arguments to pass to hook
            **kwargs: Keyword arguments to pass to hook
            
        Returns:
            Result after all plugins have processed (or None if signal rejected)
        
        Example:
            >>> # Add RSI to data
            >>> df = manager.run_hook('on_data', df)
            >>> 
            >>> # Filter signal
            >>> signal = manager.run_hook('on_signal', signal, df)
        """
        # Get initial value (first arg or None)
        result = args[0] if args else None
        
        for plugin in self.plugins:
            # Skip disabled plugins
            if not plugin.enabled:
                self.logger.debug(f"Skipping disabled plugin: {plugin.name}")
                continue
            
            # Get hook method
            hook_method = getattr(plugin, hook_name, None)
            if not hook_method or not callable(hook_method):
                continue
            
            try:
                # Call hook
                result = hook_method(result, *args[1:], **kwargs)
                
                # Special handling for signal hooks
                if hook_name == 'on_signal' and result is None:
                    self.logger.info(f"Plugin '{plugin.name}' rejected signal")
                    return None  # Stop chain, signal rejected
                
            except Exception as e:
                self.logger.error(f"Error in plugin '{plugin.name}' hook '{hook_name}': {e}")
                
                # Notify plugin of error
                try:
                    plugin.on_error(e)
                except Exception as err_e:
                    self.logger.error(f"Plugin error handler also failed: {err_e}")
                
                # Continue with other plugins (don't crash bot)
                continue
        
        return result
    
    def shutdown(self) -> None:
        """
        Shutdown all plugins.
        
        Calls on_shutdown on each plugin for cleanup.
        Errors are logged but don't prevent shutdown.
        """
        self.logger.info("Shutting down all plugins...")
        
        for plugin in self.plugins:
            try:
                plugin.on_shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin '{plugin.name}': {e}")
        
        self.logger.info("All plugins shut down")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None if not found
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was found and enabled
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = True
            self.logger.info(f"Enabled plugin: {name}")
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was found and disabled
        """
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enabled = False
            self.logger.info(f"Disabled plugin: {name}")
            return True
        return False
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins.
        
        Returns:
            List of dicts with plugin info
        """
        return [
            {
                'name': p.name,
                'enabled': p.enabled,
                'type': type(p).__name__
            }
            for p in self.plugins
        ]
