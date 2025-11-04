#  CUSTOMIZATION GUIDE - Making ML-SuperTrend-MT5 More Flexible

**Document Version**: 1.0  
**Date**: October 23, 2025  
**Author**: xPOURY4  
**Purpose**: Hướng dẫn và gợi ý để làm project dễ customize hơn

---

## 📋 TABLE OF CONTENTS

1. [Current State Analysis](#-current-state-analysis)
2. [Customization Levels](#-customization-levels)
3. [Architectural Improvements](#-architectural-improvements)
4. [Plugin System Design](#-plugin-system-design)
5. [Configuration Management](#-configuration-management)
6. [Strategy Templates](#-strategy-templates)
7. [Hooks & Events System](#-hooks--events-system)
8. [Extension Points](#-extension-points)
9. [Implementation Roadmap](#-implementation-roadmap)
10. [Examples](#-examples)

---

##  CURRENT STATE ANALYSIS

### **Customization Hiện Tại** (Đánh giá)

#### ** Điểm Mạnh:**
```python
 Config-driven: Parameters trong dataclass
 Modular bots: Dễ thêm bot mới
 Clear separation: Core logic tách biệt
 Type hints: Dễ hiểu interfaces
 Docstrings: Documentation tốt
```

#### ** Điểm Yếu:**
```python
 Hard-coded logic: Logic business baked in
 No plugin system: Không có extension mechanism
 Limited hooks: Không có event system
 Monolithic bots: Khó thay đổi từng phần
 Config limitations: JSON flat structure
 No strategy templates: Phải code từ đầu
```

---

##  CUSTOMIZATION LEVELS

### **Level 1: Configuration Only** (Easiest) 
```yaml
Users: Non-programmers, beginners
Changes: Parameters only
Files: config.json
Requires: No coding
Example: Change symbol, risk%, timeframe
```

### **Level 2: Strategy Tweaking** (Easy) 
```yaml
Users: Basic Python knowledge
Changes: Indicator parameters, thresholds
Files: config.json + simple scripts
Requires: Basic Python
Example: Adjust ATR period, change RR ratio
```

### **Level 3: Strategy Extension** (Moderate) 
```yaml
Users: Intermediate Python
Changes: Add filters, custom indicators
Files: Create new modules, extend bots
Requires: Good Python + trading knowledge
Example: Add volume filter, custom signal
```

### **Level 4: New Strategy** (Advanced) 
```yaml
Users: Advanced Python developers
Changes: Completely new trading logic
Files: New bot class, new indicators
Requires: Advanced Python + trading + architecture
Example: Implement MACD strategy, Mean Reversion
```

### **Level 5: Architecture Changes** (Expert) 
```yaml
Users: Expert developers
Changes: Core framework modifications
Files: Core modules, base classes
Requires: Deep understanding of codebase
Example: Add portfolio manager, multi-strategy
```

---

##  ARCHITECTURAL IMPROVEMENTS

### **1. Abstract Base Classes** (Foundation)

#### **Problem:**
```python
# Current: Implicit interfaces
class ICTBot:
    def __init__(self, config):
        ...
    def generate_signal(self, df):
        ...
    def open_position(self, signal):
        ...

# Issues:
- No enforced contract
- Hard to know what methods needed
- Duck typing can cause runtime errors
```

#### **Solution: Create Base Class**
```python
# File: core/base_bot.py
from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd

class BaseTradingBot(ABC):
    """
    Abstract base class for all trading bots.
    
    Enforces contract that all bots must implement.
    Provides common functionality through template methods.
    """
    
    def __init__(self, config):
        self.config = config
        self.current_trade = None
        self.trade_history = []
        self.is_connected = False
        self.logger = self._setup_logger()
        
        # Hooks for customization
        self._pre_signal_hooks = []
        self._post_signal_hooks = []
        self._pre_trade_hooks = []
        self._post_trade_hooks = []
    
    # Template methods (common flow)
    def run_cycle(self):
        """Template method for trading cycle"""
        if not self._validate_conditions():
            return
        
        data = self.get_data()
        if data is None:
            return
        
        # Call hooks
        self._execute_hooks(self._pre_signal_hooks, data)
        
        signal = self.generate_signal(data)
        
        if signal:
            self._execute_hooks(self._post_signal_hooks, signal)
            
            if self._should_trade(signal):
                self._execute_hooks(self._pre_trade_hooks, signal)
                self.open_position(signal)
                self._execute_hooks(self._post_trade_hooks, signal)
    
    # Abstract methods (must implement)
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal from data"""
        pass
    
    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate strategy-specific indicators"""
        pass
    
    # Concrete methods (can override)
    def get_data(self, bars: int = 500) -> Optional[pd.DataFrame]:
        """Get market data (common implementation)"""
        # Common MT5 data fetching logic
        pass
    
    def open_position(self, signal: Dict) -> bool:
        """Open position (common implementation with hooks)"""
        # Common position opening logic
        pass
    
    # Hook management
    def add_pre_signal_hook(self, func):
        """Add function to run before signal generation"""
        self._pre_signal_hooks.append(func)
    
    def add_post_signal_hook(self, func):
        """Add function to run after signal generation"""
        self._post_signal_hooks.append(func)
    
    def _execute_hooks(self, hooks, data):
        """Execute all hooks in list"""
        for hook in hooks:
            try:
                hook(data)
            except Exception as e:
                self.logger.error(f"Hook error: {e}")
    
    # Validation (can override)
    def _validate_conditions(self) -> bool:
        """Validate trading conditions"""
        return self.is_connected and self.current_trade is None
    
    def _should_trade(self, signal: Dict) -> bool:
        """Determine if should trade (can add filters)"""
        return True  # Override for custom filters

# Now all bots inherit from this
class ICTBot(BaseTradingBot):
    def generate_signal(self, df):
        # ICT-specific logic
        pass
    
    def calculate_indicators(self, df):
        # Calculate OB, FVG, etc.
        pass

class SuperTrendBot(BaseTradingBot):
    def generate_signal(self, df):
        # SuperTrend logic
        pass
    
    def calculate_indicators(self, df):
        # Calculate SuperTrend
        pass
```

**Benefits:**
-  Clear contract for new bots
-  Common functionality reused
-  Easy to add new bots
-  Hook system built-in
-  Better documentation

---

### **2. Strategy Pattern Enhancement**

#### **Current Problem:**
```python
# Hard to switch between strategies
# Hard to combine strategies
# Hard to A/B test strategies
```

#### **Solution: Strategy Registry**
```python
# File: core/strategy_registry.py
from typing import Dict, Type, List
from core.base_bot import BaseTradingBot

class StrategyRegistry:
    """
    Registry pattern for managing trading strategies.
    Allows dynamic strategy loading and switching.
    """
    
    _strategies: Dict[str, Type[BaseTradingBot]] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a strategy"""
        def wrapper(strategy_class):
            cls._strategies[name] = strategy_class
            return strategy_class
        return wrapper
    
    @classmethod
    def get_strategy(cls, name: str) -> Type[BaseTradingBot]:
        """Get strategy class by name"""
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        return cls._strategies[name]
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """List all registered strategies"""
        return list(cls._strategies.keys())
    
    @classmethod
    def create_bot(cls, strategy_name: str, config):
        """Factory method to create bot"""
        strategy_class = cls.get_strategy(strategy_name)
        return strategy_class(config)

# Usage:
@StrategyRegistry.register("supertrend")
class SuperTrendBot(BaseTradingBot):
    pass

@StrategyRegistry.register("ict")
class ICTBot(BaseTradingBot):
    pass

# User can now easily switch:
bot = StrategyRegistry.create_bot("supertrend", config)
# or
bot = StrategyRegistry.create_bot("ict", config)

# List available strategies:
print(StrategyRegistry.list_strategies())
# Output: ['supertrend', 'ict']
```

---

### **3. Plugin System** (Major Enhancement)

#### **Problem:**
```python
# Users want to add:
- Custom indicators
- Signal filters
- Risk rules
- Notification systems
- Data sources

# Currently: Must modify core files
```

#### **Solution: Plugin Architecture**
```python
# File: core/plugin_system.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import importlib
import os

class Plugin(ABC):
    """Base class for all plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, bot):
        """Initialize plugin with bot instance"""
        pass
    
    @abstractmethod
    def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass

class IndicatorPlugin(Plugin):
    """Plugin for custom indicators"""
    
    @abstractmethod
    def calculate(self, df) -> Dict[str, Any]:
        """Calculate indicator values"""
        pass

class FilterPlugin(Plugin):
    """Plugin for signal filtering"""
    
    @abstractmethod
    def filter_signal(self, signal: Dict) -> bool:
        """Return True if signal passes filter"""
        pass

class NotificationPlugin(Plugin):
    """Plugin for notifications"""
    
    @abstractmethod
    def notify(self, message: str, level: str = "info"):
        """Send notification"""
        pass

class PluginManager:
    """Manages plugin lifecycle"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dir = "plugins"
    
    def discover_plugins(self):
        """Auto-discover plugins in plugins directory"""
        if not os.path.exists(self.plugin_dir):
            return
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"{self.plugin_dir}.{module_name}")
                    self._register_plugin_from_module(module)
                except Exception as e:
                    print(f"Error loading plugin {module_name}: {e}")
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        plugin.on_load()
        self.plugins[plugin.name] = plugin
        print(f" Loaded plugin: {plugin.name} v{plugin.version}")
    
    def unregister_plugin(self, name: str):
        """Unregister a plugin"""
        if name in self.plugins:
            self.plugins[name].on_unload()
            del self.plugins[name]
            print(f"🔌 Unloaded plugin: {name}")
    
    def get_plugins_by_type(self, plugin_type: type) -> List[Plugin]:
        """Get all plugins of a specific type"""
        return [p for p in self.plugins.values() if isinstance(p, plugin_type)]
    
    def _register_plugin_from_module(self, module):
        """Register plugins from imported module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Plugin) and 
                attr is not Plugin):
                try:
                    plugin_instance = attr()
                    self.register_plugin(plugin_instance)
                except Exception as e:
                    print(f"Error instantiating plugin {attr_name}: {e}")

# Example: User creates custom indicator plugin
# File: plugins/rsi_divergence.py
class RSIDivergenceIndicator(IndicatorPlugin):
    @property
    def name(self):
        return "RSI Divergence"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, bot):
        self.bot = bot
    
    def on_load(self):
        print(f"Loading {self.name}...")
    
    def on_unload(self):
        print(f"Unloading {self.name}...")
    
    def calculate(self, df):
        # Calculate RSI divergence
        import talib
        rsi = talib.RSI(df['close'], timeperiod=14)
        
        # Detect divergence logic
        divergence = self._detect_divergence(df['close'], rsi)
        
        return {
            'rsi': rsi,
            'divergence': divergence
        }
    
    def _detect_divergence(self, price, rsi):
        # Divergence detection logic
        pass

# In main bot:
plugin_manager = PluginManager()
plugin_manager.discover_plugins()

# Use plugins
indicator_plugins = plugin_manager.get_plugins_by_type(IndicatorPlugin)
for plugin in indicator_plugins:
    plugin.initialize(bot)
    indicators = plugin.calculate(df)
```

**Plugin Types to Support:**
1. **IndicatorPlugin**: Custom indicators
2. **FilterPlugin**: Signal filtering
3. **NotificationPlugin**: Alerts (Telegram, Discord, Email)
4. **DataSourcePlugin**: Alternative data providers
5. **RiskPlugin**: Custom risk rules
6. **AnalyticsPlugin**: Custom analytics

---

##  CONFIGURATION MANAGEMENT

### **Problem: Current Config Limitations**
```json
// Current: config.json (flat structure)
{
    "accounts": {...},
    "symbols": {...}
}

// Issues:
 No inheritance
 No validation
 No environment variables
 No secrets management
 No profiles (dev/prod)
```

### **Solution: Enhanced Config System**

#### **1. Hierarchical Configuration**
```python
# File: core/config_manager.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import yaml
import json
from pathlib import Path

@dataclass
class BaseConfig:
    """Base configuration with common settings"""
    symbol: str = "EURUSD"
    timeframe: str = "M15"
    risk_percent: float = 1.0
    magic_number: int = 123456
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})

@dataclass
class SuperTrendConfig(BaseConfig):
    """SuperTrend-specific configuration"""
    atr_period: int = 10
    min_factor: float = 1.0
    max_factor: float = 5.0
    factor_step: float = 0.5
    use_ml: bool = True

@dataclass
class ICTConfig(BaseConfig):
    """ICT-specific configuration"""
    lookback_candles: int = 20
    fvg_min_size: float = 0.0005
    use_order_blocks: bool = True
    use_fvg: bool = True

class ConfigManager:
    """
    Advanced configuration management with:
    - Multiple formats (JSON, YAML, Python)
    - Environment variable override
    - Profile support (dev, prod)
    - Validation
    - Inheritance
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.profile = os.getenv("TRADING_PROFILE", "default")
        self._configs: Dict[str, Any] = {}
    
    def load(self, name: str, config_class: type) -> BaseConfig:
        """
        Load configuration with priority:
        1. Environment variables (highest)
        2. Profile-specific file (config.{profile}.yaml)
        3. Base file (config.yaml)
        4. Defaults (lowest)
        """
        # Load base config
        base_file = self.config_dir / f"{name}.yaml"
        config_data = self._load_file(base_file)
        
        # Load profile-specific overrides
        profile_file = self.config_dir / f"{name}.{self.profile}.yaml"
        if profile_file.exists():
            profile_data = self._load_file(profile_file)
            config_data = self._merge_configs(config_data, profile_data)
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data, name)
        
        # Create config instance
        config = config_class.from_dict(config_data)
        
        # Validate
        self._validate_config(config)
        
        self._configs[name] = config
        return config
    
    def _load_file(self, filepath: Path) -> Dict:
        """Load config from file"""
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            if filepath.suffix == '.yaml' or filepath.suffix == '.yml':
                return yaml.safe_load(f)
            elif filepath.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {filepath.suffix}")
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two config dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _apply_env_overrides(self, config: Dict, prefix: str) -> Dict:
        """Apply environment variable overrides"""
        for key, value in config.items():
            env_key = f"{prefix.upper()}_{key.upper()}"
            if env_key in os.environ:
                # Convert env var to appropriate type
                config[key] = self._parse_env_value(os.environ[env_key], type(value))
        return config
    
    def _parse_env_value(self, value: str, target_type: type):
        """Parse environment variable to target type"""
        if target_type == bool:
            return value.lower() in ('true', '1', 'yes')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        return value
    
    def _validate_config(self, config: BaseConfig):
        """Validate configuration"""
        # Add validation logic
        if config.risk_percent <= 0 or config.risk_percent > 100:
            raise ValueError(f"Invalid risk_percent: {config.risk_percent}")
        # Add more validation rules

# Usage:
config_manager = ConfigManager()

# Load with profile
config = config_manager.load("supertrend", SuperTrendConfig)

# Override with environment variable:
# export SUPERTREND_RISK_PERCENT=2.0
# export TRADING_PROFILE=production
```

#### **2. Config Files Structure**
```yaml
# config/supertrend.yaml (base config)
symbol: EURUSD
timeframe: M15
risk_percent: 1.0
atr_period: 10
use_ml: true

---

# config/supertrend.dev.yaml (development overrides)
risk_percent: 0.5  # Lower risk for testing
symbol: EURUSDm  # Demo symbol

---

# config/supertrend.prod.yaml (production overrides)
risk_percent: 1.0
symbol: EURUSD
use_ml: true

---

# Environment variables (highest priority)
# SUPERTREND_RISK_PERCENT=2.0
# SUPERTREND_SYMBOL=GBPUSD
# TRADING_PROFILE=prod
```

---

##  STRATEGY TEMPLATES

### **Problem:**
```python
# Users must code entire strategy from scratch
# No starter templates
# No example patterns
```

### **Solution: Strategy Templates**

```python
# File: templates/strategy_template.py
"""
Template for creating custom trading strategies.

Copy this file to create your own strategy.
Rename class and implement required methods.
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import pandas as pd
from typing import Dict, Optional

@StrategyRegistry.register("my_custom_strategy")
class CustomStrategyTemplate(BaseTradingBot):
    """
    Template for custom strategy.
    
    TODO: Implement the following methods:
    1. calculate_indicators() - Your indicator calculations
    2. generate_signal() - Your entry logic
    3. (Optional) _should_trade() - Additional filters
    """
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate your custom indicators here.
        
        Example:
            import talib
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        
        Returns:
            DataFrame with added indicator columns
        """
        # TODO: Add your indicators
        
        # Example: Simple RSI + SMA strategy
        import talib
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['sma_fast'] = talib.SMA(df['close'], timeperiod=10)
        df['sma_slow'] = talib.SMA(df['close'], timeperiod=30)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal from indicators.
        
        Returns:
            Dict with signal data if signal found, None otherwise
            
        Example:
            return {
                'type': 'BUY',  # or 'SELL'
                'price': current_price,
                'atr': current_atr,
                'confidence': 0.8,  # Optional
                'reason': 'RSI oversold + SMA crossover'  # Optional
            }
        """
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        # Get current values
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        sma_fast = df['sma_fast'].iloc[-1]
        sma_slow = df['sma_slow'].iloc[-1]
        
        # TODO: Implement your entry logic
        
        # Example: Buy when RSI < 30 and fast SMA crosses above slow SMA
        if current_rsi < 30 and sma_fast > sma_slow:
            return {
                'type': 'BUY',
                'price': current_price,
                'atr': self._calculate_atr(df),
                'confidence': (100 - current_rsi) / 100,  # Confidence based on RSI
                'reason': f'RSI oversold ({current_rsi:.2f}) + SMA golden cross'
            }
        
        # Example: Sell when RSI > 70 and fast SMA crosses below slow SMA
        elif current_rsi > 70 and sma_fast < sma_slow:
            return {
                'type': 'SELL',
                'price': current_price,
                'atr': self._calculate_atr(df),
                'confidence': (current_rsi - 50) / 100,
                'reason': f'RSI overbought ({current_rsi:.2f}) + SMA death cross'
            }
        
        return None
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Helper: Calculate ATR"""
        import talib
        atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
        return atr.iloc[-1]
    
    def _should_trade(self, signal: Dict) -> bool:
        """
        Optional: Add additional filters before trading.
        
        Example filters:
        - Time of day filter
        - Volatility filter
        - News filter
        - Spread filter
        
        Returns:
            True if all filters pass
        """
        # TODO: Add your filters
        
        # Example: Only trade if confidence > 60%
        if signal.get('confidence', 0) < 0.6:
            self.logger.info("Signal confidence too low, skipping trade")
            return False
        
        # Example: Time filter (only trade during London/NY session)
        from datetime import datetime
        current_hour = datetime.now().hour
        if not (8 <= current_hour <= 20):  # 8 AM to 8 PM
            self.logger.info("Outside trading hours, skipping trade")
            return False
        
        return True
    
    # Optional: Override risk management
    def calculate_position_size(self, entry: float, sl: float) -> float:
        """
        Optional: Custom position sizing logic.
        
        Default implementation uses fixed risk percentage.
        Override for custom sizing (e.g., Kelly Criterion, Volatility-based)
        """
        # Use default implementation
        return super().calculate_position_size(entry, sl)
        
        # Or implement custom sizing:
        # account_info = mt5.account_info()
        # balance = account_info.balance
        # risk_amount = balance * (self.config.risk_percent / 100)
        # ... your custom logic
```

#### **Additional Templates:**

```python
# templates/mean_reversion_template.py
"""Mean Reversion Strategy Template"""

# templates/momentum_template.py
"""Momentum/Breakout Strategy Template"""

# templates/scalping_template.py
"""Scalping Strategy Template"""

# templates/swing_trading_template.py
"""Swing Trading Strategy Template"""
```

---

## 🎣 HOOKS & EVENTS SYSTEM

### **Problem:**
```python
# Users want to:
- Log custom data
- Send notifications
- Add filters
- Modify behavior

# Currently: Must edit bot code
```

### **Solution: Event System**

```python
# File: core/events.py
from typing import Callable, List, Dict, Any
from enum import Enum

class EventType(Enum):
    """Trading bot events"""
    
    # Lifecycle events
    BOT_STARTED = "bot_started"
    BOT_STOPPED = "bot_stopped"
    CYCLE_START = "cycle_start"
    CYCLE_END = "cycle_end"
    
    # Data events
    DATA_LOADED = "data_loaded"
    INDICATORS_CALCULATED = "indicators_calculated"
    
    # Signal events
    SIGNAL_GENERATED = "signal_generated"
    SIGNAL_FILTERED = "signal_filtered"
    
    # Trade events
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    POSITION_MODIFIED = "position_modified"
    
    # Risk events
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    BREAKEVEN_MOVED = "breakeven_moved"
    
    # Error events
    ERROR_OCCURRED = "error_occurred"
    CONNECTION_LOST = "connection_lost"

class EventData:
    """Container for event data"""
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
        self.cancelled = False
    
    def cancel(self):
        """Cancel the event (prevent default action)"""
        self.cancelled = True

class EventManager:
    """
    Event-driven architecture for bot customization.
    
    Allows users to hook into any event without modifying core code.
    """
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._global_listeners: List[Callable] = []
    
    def on(self, event_type: EventType, callback: Callable, priority: int = 0):
        """
        Register event listener.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
            priority: Higher priority callbacks run first
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append((priority, callback))
        # Sort by priority (descending)
        self._listeners[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def on_any(self, callback: Callable):
        """Register listener for all events"""
        self._global_listeners.append(callback)
    
    def emit(self, event_type: EventType, data: Dict[str, Any]) -> EventData:
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Event data
        
        Returns:
            EventData object (can be checked if cancelled)
        """
        event_data = EventData(event_type, data)
        
        # Call global listeners first
        for listener in self._global_listeners:
            try:
                listener(event_data)
                if event_data.cancelled:
                    return event_data
            except Exception as e:
                print(f"Error in global listener: {e}")
        
        # Call specific event listeners
        if event_type in self._listeners:
            for priority, callback in self._listeners[event_type]:
                try:
                    callback(event_data)
                    if event_data.cancelled:
                        return event_data
                except Exception as e:
                    print(f"Error in event listener: {e}")
        
        return event_data
    
    def off(self, event_type: EventType, callback: Callable):
        """Unregister event listener"""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                (p, cb) for p, cb in self._listeners[event_type] 
                if cb != callback
            ]

# Usage in bot:
class BaseTradingBot:
    def __init__(self, config):
        self.events = EventManager()
        self.config = config
    
    def run_cycle(self):
        # Emit cycle start event
        self.events.emit(EventType.CYCLE_START, {'bot': self})
        
        # Get data
        df = self.get_data()
        self.events.emit(EventType.DATA_LOADED, {'data': df})
        
        # Generate signal
        signal = self.generate_signal(df)
        if signal:
            event = self.events.emit(EventType.SIGNAL_GENERATED, {'signal': signal})
            
            # Check if event was cancelled by a listener
            if event.cancelled:
                self.logger.info("Signal cancelled by event listener")
                return
            
            # Open position
            self.open_position(signal)
            self.events.emit(EventType.POSITION_OPENED, {
                'signal': signal,
                'ticket': self.current_trade.ticket
            })
        
        # Emit cycle end event
        self.events.emit(EventType.CYCLE_END, {'bot': self})

# User customization (no core code changes):
def log_all_signals(event_data: EventData):
    """Log all signals to custom file"""
    signal = event_data.data['signal']
    with open('my_signals.log', 'a') as f:
        f.write(f"{event_data.timestamp}: {signal}\n")

def notify_on_trade(event_data: EventData):
    """Send Telegram notification on trade"""
    import requests
    ticket = event_data.data['ticket']
    signal = event_data.data['signal']
    
    message = f" New trade opened!\nTicket: {ticket}\nType: {signal['type']}"
    # Send to Telegram
    # requests.post(...)

def filter_low_confidence_signals(event_data: EventData):
    """Cancel signals with low confidence"""
    signal = event_data.data['signal']
    if signal.get('confidence', 0) < 0.7:
        event_data.cancel()  # Prevent trade
        print(f"Cancelled low confidence signal: {signal}")

# Register event listeners
bot = ICTBot(config)
bot.events.on(EventType.SIGNAL_GENERATED, log_all_signals)
bot.events.on(EventType.POSITION_OPENED, notify_on_trade)
bot.events.on(EventType.SIGNAL_GENERATED, filter_low_confidence_signals, priority=100)  # High priority
```

---

## 🔌 EXTENSION POINTS

### **Define Clear Extension Points**

```python
# File: core/extension_points.py
"""
Extension points for customizing bot behavior.

These are the designed extension points where users can
add custom functionality without modifying core code.
"""

class ExtensionPoint:
    """Base class for extension points"""
    pass

# 1. INDICATOR EXTENSION POINT
class IndicatorExtension(ExtensionPoint):
    """Add custom indicators"""
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate and add indicators to dataframe.
        
        Args:
            df: OHLCV dataframe
        
        Returns:
            DataFrame with added indicator columns
        """
        raise NotImplementedError

# Example user extension:
class MyCustomIndicator(IndicatorExtension):
    def calculate(self, df):
        import talib
        df['my_indicator'] = talib.RSI(df['close']) + talib.MACD(df['close'])[0]
        return df

# 2. SIGNAL FILTER EXTENSION POINT
class SignalFilterExtension(ExtensionPoint):
    """Filter trading signals"""
    
    def filter(self, signal: Dict, df: pd.DataFrame) -> bool:
        """
        Determine if signal should be traded.
        
        Args:
            signal: Generated signal
            df: Current market data
        
        Returns:
            True if signal passes filter
        """
        raise NotImplementedError

# Example: Volume filter
class VolumeFilter(SignalFilterExtension):
    def __init__(self, min_volume_multiplier=1.5):
        self.min_volume_multiplier = min_volume_multiplier
    
    def filter(self, signal, df):
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        return current_volume > (avg_volume * self.min_volume_multiplier)

# 3. RISK MANAGEMENT EXTENSION POINT
class RiskManagerExtension(ExtensionPoint):
    """Custom risk management"""
    
    def calculate_position_size(self, balance: float, risk: float, 
                                 entry: float, sl: float) -> float:
        """Calculate position size"""
        raise NotImplementedError
    
    def validate_trade(self, signal: Dict) -> bool:
        """Validate if trade meets risk criteria"""
        raise NotImplementedError

# Example: Kelly Criterion
class KellyCriterionRisk(RiskManagerExtension):
    def __init__(self, win_rate: float, avg_win: float, avg_loss: float):
        self.win_rate = win_rate
        self.avg_win = avg_win
        self.avg_loss = avg_loss
    
    def calculate_position_size(self, balance, risk, entry, sl):
        # Kelly formula: f* = (p*b - q) / b
        # where p = win rate, q = 1-p, b = avg_win/avg_loss
        b = self.avg_win / self.avg_loss
        kelly = (self.win_rate * b - (1 - self.win_rate)) / b
        
        # Use fraction of Kelly (safer)
        fractional_kelly = kelly * 0.25  # 25% of Kelly
        
        # Calculate position size
        risk_per_trade = balance * fractional_kelly
        distance_to_sl = abs(entry - sl)
        
        # ... calculate lots
        return lots

# 4. NOTIFICATION EXTENSION POINT
class NotificationExtension(ExtensionPoint):
    """Send notifications"""
    
    def send(self, message: str, level: str = "info"):
        """Send notification"""
        raise NotImplementedError

# Example: Telegram notifier
class TelegramNotifier(NotificationExtension):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send(self, message, level="info"):
        import requests
        emoji = {"info": "", "warning": "", "error": "", "success": ""}
        formatted = f"{emoji.get(level, '')} {message}"
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        requests.post(url, json={"chat_id": self.chat_id, "text": formatted})

# 5. DATA SOURCE EXTENSION POINT
class DataSourceExtension(ExtensionPoint):
    """Alternative data sources"""
    
    def fetch_data(self, symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        """Fetch OHLCV data"""
        raise NotImplementedError

# Example: Alpha Vantage data source
class AlphaVantageDataSource(DataSourceExtension):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def fetch_data(self, symbol, timeframe, bars):
        # Fetch from Alpha Vantage API
        # ...
        return df

# Usage in bot:
class ExtensibleBot(BaseTradingBot):
    def __init__(self, config):
        super().__init__(config)
        self.indicator_extensions: List[IndicatorExtension] = []
        self.filter_extensions: List[SignalFilterExtension] = []
        self.risk_extensions: List[RiskManagerExtension] = []
        self.notification_extensions: List[NotificationExtension] = []
    
    def add_indicator(self, indicator: IndicatorExtension):
        """Add custom indicator"""
        self.indicator_extensions.append(indicator)
    
    def add_filter(self, filter_ext: SignalFilterExtension):
        """Add signal filter"""
        self.filter_extensions.append(filter_ext)
    
    def add_risk_manager(self, risk_ext: RiskManagerExtension):
        """Add risk manager"""
        self.risk_extensions.append(risk_ext)
    
    def add_notifier(self, notifier: NotificationExtension):
        """Add notification handler"""
        self.notification_extensions.append(notifier)
    
    def calculate_indicators(self, df):
        # Apply all custom indicators
        for indicator in self.indicator_extensions:
            df = indicator.calculate(df)
        return df
    
    def _should_trade(self, signal):
        # Apply all filters
        for filter_ext in self.filter_extensions:
            if not filter_ext.filter(signal, self.last_data):
                return False
        return True
    
    def _notify(self, message, level="info"):
        # Send to all notifiers
        for notifier in self.notification_extensions:
            notifier.send(message, level)

# User customization (no core changes):
bot = ExtensibleBot(config)

# Add custom indicator
bot.add_indicator(MyCustomIndicator())

# Add filters
bot.add_filter(VolumeFilter(min_volume_multiplier=2.0))
bot.add_filter(TimeFilter(start_hour=8, end_hour=20))

# Add notifications
bot.add_notifier(TelegramNotifier(bot_token="xxx", chat_id="yyy"))
bot.add_notifier(DiscordNotifier(webhook_url="zzz"))

# Run bot with all extensions
bot.run()
```

---

##  IMPLEMENTATION ROADMAP

### **Phase 1: Foundation** (2-3 weeks)
```yaml
Week 1-2: Core Architecture
 Create BaseTradingBot abstract class
 Implement StrategyRegistry
 Add basic hook system
 Refactor existing bots to inherit from base

Week 3: Configuration
 Implement ConfigManager
 Add YAML support
 Add environment variable support
 Add profile support (dev/prod)

Deliverables:
- base_bot.py
- strategy_registry.py
- config_manager.py
- Updated ICTBot and SuperTrendBot
```

### **Phase 2: Extensions** (2-3 weeks)
```yaml
Week 4-5: Plugin System
 Implement PluginManager
 Create plugin base classes
 Add auto-discovery
 Create example plugins

Week 6: Extension Points
 Define extension point interfaces
 Add extension point support to bots
 Create extension examples

Deliverables:
- plugin_system.py
- extension_points.py
- Example plugins (3-5)
- Documentation
```

### **Phase 3: Templates & Tools** (1-2 weeks)
```yaml
Week 7: Strategy Templates
 Create template files
 Add template documentation
 Create template generator CLI

Week 8: Event System
 Implement EventManager
 Add events to bot lifecycle
 Create event examples

Deliverables:
- 5+ strategy templates
- events.py
- Template generator tool
- Event usage examples
```

### **Phase 4: Documentation & Examples** (1 week)
```yaml
Week 9: Documentation
 Write customization guide
 Create video tutorials
 Add inline documentation
 Update README

Deliverables:
- CUSTOMIZATION_GUIDE.md
- VIDEO_TUTORIALS.md
- Updated docs/
- 10+ examples
```

---

## 📚 EXAMPLES

### **Example 1: Simple Custom Strategy**
```python
# File: my_strategies/rsi_sma_strategy.py
from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import talib

@StrategyRegistry.register("rsi_sma")
class RSISMAStrategy(BaseTradingBot):
    """Simple RSI + SMA crossover strategy"""
    
    def calculate_indicators(self, df):
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['sma_fast'] = talib.SMA(df['close'], timeperiod=10)
        df['sma_slow'] = talib.SMA(df['close'], timeperiod=30)
        return df
    
    def generate_signal(self, df):
        df = self.calculate_indicators(df)
        
        rsi = df['rsi'].iloc[-1]
        sma_fast = df['sma_fast'].iloc[-1]
        sma_slow = df['sma_slow'].iloc[-1]
        price = df['close'].iloc[-1]
        
        # Buy: RSI < 30 and fast SMA crosses above slow SMA
        if rsi < 30 and sma_fast > sma_slow:
            return {
                'type': 'BUY',
                'price': price,
                'atr': talib.ATR(df['high'], df['low'], df['close']).iloc[-1]
            }
        
        # Sell: RSI > 70 and fast SMA crosses below slow SMA
        elif rsi > 70 and sma_fast < sma_slow:
            return {
                'type': 'SELL',
                'price': price,
                'atr': talib.ATR(df['high'], df['low'], df['close']).iloc[-1]
            }
        
        return None

# Usage:
from core.strategy_registry import StrategyRegistry
bot = StrategyRegistry.create_bot("rsi_sma", config)
bot.run()
```

### **Example 2: Adding Telegram Notifications**
```python
# File: plugins/telegram_notifier.py
from core.plugin_system import NotificationPlugin

class TelegramNotifier(NotificationPlugin):
    @property
    def name(self):
        return "Telegram Notifier"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, bot):
        self.bot = bot
        self.bot_token = bot.config.telegram_bot_token
        self.chat_id = bot.config.telegram_chat_id
        
        # Register event listeners
        bot.events.on(EventType.POSITION_OPENED, self._on_position_opened)
        bot.events.on(EventType.POSITION_CLOSED, self._on_position_closed)
    
    def on_load(self):
        print("📱 Telegram notifications enabled")
    
    def on_unload(self):
        print("📱 Telegram notifications disabled")
    
    def notify(self, message, level="info"):
        import requests
        emoji = {"info": "", "warning": "", "error": "", "success": ""}
        formatted = f"{emoji.get(level, '')} {message}"
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        requests.post(url, json={"chat_id": self.chat_id, "text": formatted})
    
    def _on_position_opened(self, event_data):
        signal = event_data.data['signal']
        message = f"""
 *New Position Opened*

Symbol: {self.bot.config.symbol}
Type: {signal['type']}
Entry: {signal['price']:.5f}
SL: {signal.get('sl', 'N/A')}
TP: {signal.get('tp', 'N/A')}
"""
        self.notify(message, "success")
    
    def _on_position_closed(self, event_data):
        profit = event_data.data['profit']
        emoji = "" if profit > 0 else ""
        message = f"""
{emoji} *Position Closed*

Profit: ${profit:.2f}
"""
        self.notify(message, "success" if profit > 0 else "warning")

# Usage: Plugin auto-loaded from plugins/ directory
# Or manually:
plugin_manager.register_plugin(TelegramNotifier())
```

### **Example 3: Custom Risk Manager**
```python
# File: extensions/volatility_risk.py
from core.extension_points import RiskManagerExtension
import numpy as np

class VolatilityAdjustedRisk(RiskManagerExtension):
    """Adjust position size based on volatility"""
    
    def __init__(self, base_risk=1.0, volatility_window=20):
        self.base_risk = base_risk
        self.volatility_window = volatility_window
    
    def calculate_position_size(self, balance, risk, entry, sl):
        # Get recent volatility
        df = self.bot.last_data
        returns = df['close'].pct_change()
        volatility = returns.rolling(self.volatility_window).std().iloc[-1]
        
        # Calculate average volatility
        avg_volatility = returns.rolling(100).std().mean()
        
        # Adjust risk based on volatility
        # Higher volatility = lower position size
        volatility_multiplier = avg_volatility / volatility
        adjusted_risk = self.base_risk * volatility_multiplier
        
        # Clamp to reasonable range
        adjusted_risk = np.clip(adjusted_risk, 0.5, 2.0)
        
        # Calculate position size
        risk_amount = balance * (adjusted_risk / 100)
        distance_to_sl = abs(entry - sl)
        
        # ... standard position size calculation
        return position_size
    
    def validate_trade(self, signal):
        # Don't trade in extreme volatility
        df = self.bot.last_data
        returns = df['close'].pct_change()
        current_volatility = returns.rolling(20).std().iloc[-1]
        avg_volatility = returns.rolling(100).std().mean()
        
        if current_volatility > (avg_volatility * 2):
            self.bot.logger.warning("Volatility too high, skipping trade")
            return False
        
        return True

# Usage:
bot = ExtensibleBot(config)
bot.add_risk_manager(VolatilityAdjustedRisk(base_risk=1.0))
```

### **Example 4: Time-Based Filter**
```python
# File: extensions/time_filter.py
from core.extension_points import SignalFilterExtension
from datetime import datetime, time

class TradingHoursFilter(SignalFilterExtension):
    """Only trade during specific hours"""
    
    def __init__(self, start_hour=8, end_hour=20, timezone='UTC'):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.timezone = timezone
    
    def filter(self, signal, df):
        current_time = datetime.now()
        current_hour = current_time.hour
        
        if not (self.start_hour <= current_hour < self.end_hour):
            return False
        
        # Don't trade on weekends
        if current_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        return True

# Usage:
bot.add_filter(TradingHoursFilter(start_hour=8, end_hour=20))
```

---

##  BENEFITS OF THESE IMPROVEMENTS

### **For Users:**
```yaml
 Easy to customize without touching core code
 Can add features via plugins
 Multiple strategies in one codebase
 Better documentation and examples
 Community can share extensions
 Lower learning curve
```

### **For Developers:**
```yaml
 Clear extension points
 Less merge conflicts
 Easier to maintain
 Better testing (mock plugins)
 More modular architecture
 Easier to add features
```

### **For Project:**
```yaml
 More contributors
 Larger ecosystem (plugins)
 Better adoption
 More use cases
 Community growth
 Long-term sustainability
```

---

##  CUSTOMIZATION MATRIX

### **What Users Can Customize:**

| Feature | Current | After Improvements | Difficulty |
|---------|---------|-------------------|------------|
| Parameters |  config.json |  YAML + env vars |  Easy |
| Indicators |  Edit code |  Plugin system |  Easy |
| Filters |  Edit code |  Extension points |  Easy |
| Notifications |  Not supported |  Plugins |  Easy |
| Risk Logic |  Edit code |  Extension points |  Moderate |
| Strategy |  New bot |  Templates + Registry |  Moderate |
| Data Sources |  MT5 only |  Data plugins |  Advanced |
| Core Logic |  Edit core |  Event hooks |  Expert |

---

##  RELATED DOCUMENTS

- [PROJECT_SCOPE.md](PROJECT_SCOPE.md) - Project scope and boundaries
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture overview (to be created)
- [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md) - Plugin development guide (to be created)
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation (to be created)

---

##  CONCLUSION

Implementing these improvements will transform the project from a collection of trading bots into a **flexible trading framework** that users can customize without modifying core code.

### **Priority Recommendations:**

**HIGH PRIORITY** (Implement First):
1.  Abstract Base Class (BaseTradingBot)
2.  Strategy Registry
3.  Enhanced Configuration (YAML + env vars)
4.  Strategy Templates

**MEDIUM PRIORITY** (Implement Second):
5.  Event System
6.  Extension Points
7.  Plugin System (basic)

**LOW PRIORITY** (Nice to Have):
8.  Advanced plugin features
9.  Plugin marketplace
10.  GUI configuration tool

---

**Start small, iterate quickly, and gather feedback from users! **

---

**End of Document**
