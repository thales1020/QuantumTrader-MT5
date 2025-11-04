# Plugin Examples

This directory contains comprehensive plugin examples demonstrating how to extend the trading system with custom functionality.

## 📚 Available Plugins

### 1. Advanced Risk Manager
**File:** `advanced_risk_manager.py`  
**Difficulty:** ⭐⭐⭐ Advanced  
**Hooks Used:** `before_trade`, `after_trade`, `on_position_close`, `daily_start`

Advanced risk management with:
- **Daily Loss Limits** - Stop trading when daily loss exceeds threshold
- **Maximum Drawdown Protection** - Halt trading if drawdown limit hit
- **Volatility-Based Sizing** - Adjust position size based on ATR
- **Time-Based Filters** - Reduce risk during high-volatility hours
- **Streak Adjustment** - Scale size based on winning/losing streaks

**Features:**
- ✅ Dynamic position sizing (0.5x to 1.5x based on conditions)
- ✅ Real-time risk tracking
- ✅ Equity curve monitoring
- ✅ High-risk hour detection (London/US open)
- ✅ Comprehensive status reporting

```python
config = {
    'max_daily_loss_percent': 2.0,  # Stop at 2% daily loss
    'max_drawdown_percent': 10.0,   # Max 10% drawdown
    'avoid_news_hours': True,       # Reduce risk during news
    'scale_on_streak': True,        # Adjust on win/loss streaks
}
risk_manager = AdvancedRiskManager(config)
```

---

### 2. Trade Analytics
**File:** `trade_analytics.py`  
**Difficulty:** ⭐⭐ Intermediate  
**Hooks Used:** `after_trade`, `on_position_close`, `daily_end`

Comprehensive trade tracking and analysis:
- **Performance Metrics** - Win rate, profit factor, expectancy
- **Best/Worst Trades** - Identify largest wins and losses
- **Time-Based Analysis** - Best hours and days for trading
- **Symbol Performance** - Per-symbol statistics
- **Report Export** - JSON export for external analysis

**Metrics Tracked:**
- ✅ Win rate and profit factor
- ✅ Average win/loss ratio
- ✅ Trade expectancy
- ✅ Best trading hours (hourly breakdown)
- ✅ Best trading days (day of week analysis)
- ✅ Symbol-specific performance

```python
config = {
    'track_time_performance': True,   # Analyze by hour/day
    'track_symbol_performance': True, # Per-symbol stats
    'export_daily_report': True,      # Auto-export daily
    'report_path': './reports/',      # Export directory
}
analytics = TradeAnalytics(config)
```

---

### 3. Telegram Notifier
**File:** `telegram_notifier.py`  
**Difficulty:** ⭐⭐ Intermediate  
**Hooks Used:** `after_trade`, `on_position_close`, `daily_start`, `daily_end`, `on_error`

Real-time notifications via Telegram:
- **Trade Alerts** - Entry and exit notifications with full details
- **Daily Summaries** - End-of-day performance reports
- **Risk Warnings** - Immediate alerts for risk limit violations
- **Error Notifications** - System error alerts
- **Emoji Support** - Visual indicators for quick scanning

**Notification Types:**
- 🟢 Trade opened (BUY)
- 🔴 Trade opened (SELL)
- 💰 Trade closed (PROFIT)
- 📉 Trade closed (LOSS)
- ⚠️ Risk warnings
- ❌ Error alerts
- 📊 Daily summaries

```python
config = {
    'bot_token': 'YOUR_BOT_TOKEN',    # From @BotFather
    'chat_id': 'YOUR_CHAT_ID',        # Your Telegram chat ID
    'notify_trades': True,             # Trade entry/exit alerts
    'notify_daily': True,              # Daily performance
    'notify_errors': True,             # Error alerts
    'use_emojis': True,                # Visual indicators
}
notifier = TelegramNotifier(config)
```

---

## 🎯 Usage

### Basic Plugin Integration

1. **Import the plugin:**
   ```python
   from examples.plugins.advanced_risk_manager import AdvancedRiskManager
   ```

2. **Configure the plugin:**
   ```python
   config = {
       'max_daily_loss_percent': 2.0,
       'max_drawdown_percent': 10.0,
   }
   ```

3. **Initialize the plugin:**
   ```python
   risk_manager = AdvancedRiskManager(config)
   ```

4. **Integrate with bot:**
   ```python
   from core.plugin_system import PluginManager
   
   # Add to plugin manager
   plugin_manager = PluginManager()
   plugin_manager.register_plugin(risk_manager)
   
   # Or use with bot directly
   bot.add_plugin(risk_manager)
   ```

### Using Multiple Plugins

Combine plugins for comprehensive trading system:

```python
# Risk management
risk_manager = AdvancedRiskManager({
    'max_daily_loss_percent': 2.0,
})

# Analytics tracking
analytics = TradeAnalytics({
    'track_time_performance': True,
})

# Notifications
notifier = TelegramNotifier({
    'bot_token': 'YOUR_TOKEN',
    'chat_id': 'YOUR_CHAT_ID',
})

# Add all to bot
bot.add_plugin(risk_manager)
bot.add_plugin(analytics)
bot.add_plugin(notifier)
```

### Testing Plugins

Run the test suite to verify all plugins work:

```bash
python scripts/test_plugin_examples.py
```

---

## 🔧 Creating Custom Plugins

### Plugin Template

```python
from core.plugin_system import BasePlugin
from typing import Dict

class MyCustomPlugin(BasePlugin):
    """Your custom plugin description"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.my_setting = config.get('my_setting', 'default')
    
    def get_name(self) -> str:
        return "MyCustomPlugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    # Implement hooks you need
    def before_trade(self, context: Dict) -> Dict:
        """Called before opening a trade"""
        # Your logic here
        return context
    
    def after_trade(self, context: Dict) -> Dict:
        """Called after opening a trade"""
        # Your logic here
        return context
    
    def on_position_close(self, context: Dict) -> Dict:
        """Called when position closes"""
        # Your logic here
        return context
```

### Available Hooks

All plugins can implement these hooks:

| Hook | When Called | Use Case |
|------|-------------|----------|
| `before_trade` | Before opening position | Validate trade, modify parameters |
| `after_trade` | After opening position | Record trade, send notification |
| `on_position_close` | When position closes | Update metrics, calculate P&L |
| `daily_start` | Start of trading day | Reset counters, send status |
| `daily_end` | End of trading day | Generate reports, export data |
| `on_error` | When error occurs | Log errors, send alerts |

### Hook Context

Each hook receives a context dictionary with relevant data:

**before_trade / after_trade:**
```python
{
    'symbol': 'EURUSD',
    'type': 'BUY',
    'price': 1.10000,
    'position_size': 0.1,
    'stop_loss': 1.09500,
    'take_profit': 1.10500,
    'atr': 0.0015,
    'account_balance': 10000,
}
```

**on_position_close:**
```python
{
    'ticket': 12345,
    'symbol': 'EURUSD',
    'price': 1.10300,
    'profit': 30.00,
    'exit_reason': 'take_profit',
    'duration_minutes': 45,
    'account_balance': 10030,
}
```

---

## 📊 Comparison

| Plugin | Purpose | Complexity | Real-time | Notifications |
|--------|---------|------------|-----------|---------------|
| Risk Manager | Protect capital | High | Yes | Risk warnings |
| Analytics | Track performance | Medium | Yes | Daily reports |
| Telegram | Communicate | Medium | Yes | All events |

**Recommended Combinations:**
- **Conservative**: Risk Manager + Analytics
- **Active Trader**: All three plugins
- **Automated**: Risk Manager + Telegram
- **Analysis**: Analytics only

---

## 🚀 Advanced Features

### 1. Plugin Communication

Plugins can access each other through the plugin manager:

```python
def before_trade(self, context: Dict) -> Dict:
    # Get analytics from another plugin
    analytics = self.plugin_manager.get_plugin('TradeAnalytics')
    win_rate = analytics.calculate_win_rate()
    
    # Adjust decision based on win rate
    if win_rate < 40:
        # Reduce risk
        context['position_size'] *= 0.5
    
    return context
```

### 2. State Persistence

Save and load plugin state:

```python
def save_state(self, filename: str):
    """Save plugin state to file"""
    state = {
        'trades': self.trades,
        'total_profit': self.total_profit,
        'best_trade': self.best_trade,
    }
    with open(filename, 'w') as f:
        json.dump(state, f)

def load_state(self, filename: str):
    """Load plugin state from file"""
    with open(filename, 'r') as f:
        state = json.load(f)
    self.trades = state['trades']
    self.total_profit = state['total_profit']
```

### 3. Async Operations

For plugins that need async (like Telegram):

```python
async def send_notification_async(self, message: str):
    """Send notification asynchronously"""
    await self.bot.send_message(
        chat_id=self.chat_id,
        text=message
    )

def after_trade(self, context: Dict) -> Dict:
    """Hook with async call"""
    message = self.format_message(context)
    asyncio.run(self.send_notification_async(message))
    return context
```

---

## 📚 Related Documentation

- [Plugin System Guide](../../docs/PLUGIN_QUICK_START.md) - Complete plugin system documentation
- [Phase 2 Summary](../../docs/PHASE_2_COMPLETE.md) - Plugin system implementation details
- [Use Cases](../use_cases/README.md) - Real-world plugin usage examples
- [Strategy Examples](../strategies/README.md) - Strategies that use plugins

---

## ✅ Testing

All examples have been tested and verified:

```
✅ Advanced Risk Manager - Import, instantiation, risk validation
✅ Trade Analytics - Import, instantiation, tracking, reporting
✅ Telegram Notifier - Import, instantiation, notifications (demo mode)

Test Suite: 3/3 tests passed (100%)
```

---

## 💡 Tips

1. **Start Simple** - Begin with one plugin, understand how hooks work
2. **Test Thoroughly** - Use demo mode to test without real trading
3. **Log Everything** - Use Python logging for debugging
4. **Handle Errors** - Always use try/except in hook methods
5. **Document Well** - Future you will thank present you

### Common Patterns

**Before modifying trades:**
```python
def before_trade(self, context: Dict) -> Dict:
    # Always validate inputs
    if context.get('position_size', 0) <= 0:
        return context
    
    # Make your modifications
    context['position_size'] *= 0.8
    
    # Always return context
    return context
```

**Recording data:**
```python
def on_position_close(self, context: Dict) -> Dict:
    # Extract what you need
    profit = context.get('profit', 0)
    
    # Update your tracking
    self.total_profit += profit
    
    # Return unmodified (or modified) context
    return context
```

---

## 🤝 Contributing

Have a useful plugin? Share it!

1. Follow the plugin template structure
2. Include comprehensive docstrings
3. Add usage example in main block
4. Test with test suite
5. Document in README

---

**Created**: November 4, 2025  
**Author**: QuantumTrader-MT5 Team  
**Version**: 1.0.0
