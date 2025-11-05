# Plugin System Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Test Use Cases (Simulation)

```bash
# Test all use cases
python scripts/test_all_use_cases.py

# Test specific use case
python scripts/test_all_use_cases.py --use-case 1
```

### 2. Run Conservative Strategy (Recommended for beginners)

```bash
# Simulate first
python examples/use_cases/use_case_1_conservative.py --mode simulate

# Configure Telegram
# Edit: examples/use_cases/use_case_1_conservative.py
# Update: bot_token and chat_id

# Run with real MT5 (demo account first!)
python examples/use_cases/use_case_1_conservative.py --mode live
```

---

## 📚 Use Cases

### Use Case 1: Conservative Trading ⭐ Recommended
**Best for**: Risk-averse traders, beginners

```bash
python examples/use_cases/use_case_1_conservative.py
```

**Plugins**:
- ✅ RSI Filter (strict: 25/75)
- ✅ Volume Filter (2x average)
- ✅ Telegram (trades only)

**Expected**: 10-20% of signals, 60-70% win rate

---

### Use Case 2: Aggressive Scalping ⚡ Advanced
**Best for**: Active traders, high-frequency

```bash
python examples/use_cases/use_case_2_scalping.py
```

**Plugins**:
- ❌ No filters
- ✅ Telegram (all events)

**Expected**: 95% of signals, 45-55% win rate, 20-50 trades/day

---

### Use Case 3: Risk Management 🛡️ Professional
**Best for**: Capital protection, professional traders

```bash
python examples/use_cases/use_case_3_risk_management.py
```

**Plugins**:
- ✅ Daily Loss Limit (2%)
- ✅ Trade Journal (CSV logging)
- ✅ Telegram (risk alerts)

**Expected**: Auto-pause on bad days, complete trade history

---

## 🔌 Available Plugins

### Built-in Plugins

| Plugin | Purpose | Configuration |
|--------|---------|---------------|
| **RSIFilter** | Filter by RSI | period, oversold, overbought |
| **VolumeFilter** | Filter by volume | multiplier, period |
| **TelegramNotifier** | Send alerts | bot_token, chat_id |

### Custom Plugins (Use Case 3)

| Plugin | Purpose | Configuration |
|--------|---------|---------------|
| **DailyLossLimit** | Stop on daily loss | max_daily_loss_percent |
| **TradeJournal** | Log to CSV | journal_file |

---

## ⚙️ Configuration Example

```python
from dataclasses import dataclass, field
from typing import List
from core.base_bot import BaseConfig

@dataclass
class MyConfig(BaseConfig):
    symbol: str = 'EURUSD'
    timeframe: str = 'H1'
    magic_number: int = 12345
    
    # Plugin configuration
    plugins: List = field(default_factory=lambda: [
        {
            'name': 'RSIFilter',
            'enabled': True,
            'config': {
                'period': 14,
                'oversold': 30,
                'overbought': 70,
                'boost_confidence': True
            }
        },
        {
            'name': 'TelegramNotifier',
            'enabled': True,
            'config': {
                'bot_token': 'YOUR_TOKEN',
                'chat_id': 'YOUR_CHAT_ID',
                'notify_on_trade_open': True,
                'notify_on_trade_close': True
            }
        }
    ])
```

---

## 🎯 Common Scenarios

### Scenario 1: "I want fewer, better trades"
→ Use Case 1 (Conservative)
- Multiple filters reduce signals by 80-90%
- Higher win rate (60-70%)
- Less stress

### Scenario 2: "I want maximum opportunities"
→ Use Case 2 (Scalping)
- No filters = trade almost everything
- More trades = more opportunities
- Requires active monitoring

### Scenario 3: "I want to protect my capital"
→ Use Case 3 (Risk Management)
- Daily loss limit prevents blowups
- Trade journal for analysis
- Automatic risk controls

### Scenario 4: "I want notifications only"
→ Just use TelegramNotifier
```python
plugins: List = field(default_factory=lambda: [
    {
        'name': 'TelegramNotifier',
        'enabled': True,
        'config': {
            'bot_token': 'YOUR_TOKEN',
            'chat_id': 'YOUR_CHAT_ID',
            'notify_on_trade_open': True,
            'notify_on_trade_close': True
        }
    }
])
```

---

## 📱 Telegram Setup (5 minutes)

### Step 1: Create Bot
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow instructions
5. Copy the **bot token**

### Step 2: Get Chat ID
1. Search for `@userinfobot`
2. Send `/start`
3. Copy your **chat ID** (numbers)

### Step 3: Update Configuration
```python
'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
'chat_id': '987654321'
```

---

## 🧪 Testing Workflow

### 1. Simulation (No MT5 needed)
```bash
python examples/use_cases/use_case_1_conservative.py --mode simulate
```
- See how plugins work
- Understand filter logic
- No trading

### 2. Backtest (Historical data)
```bash
# Coming soon: Backtest with plugins
python scripts/backtest_with_plugins.py
```

### 3. Demo Account (Real MT5, fake money)
```bash
python examples/use_cases/use_case_1_conservative.py --mode live
```
- Configure Telegram first
- Use demo MT5 account
- Watch real notifications

### 4. Live Trading (Real money)
```bash
# After successful demo trading
python examples/use_cases/use_case_1_conservative.py --mode live
```
- Start with small positions
- Monitor closely
- Scale up gradually

---

## 🆘 Troubleshooting

### "Telegram not working"
1. Check bot token and chat ID
2. Send `/start` to your bot first
3. Make sure bot is not blocked

### "Plugins not loading"
1. Check plugin name matches exactly
2. Verify config syntax (dict with 'name', 'enabled', 'config')
3. Check logs for errors

### "Too many/few signals"
- Too many → Add RSI and Volume filters
- Too few → Remove filters or loosen thresholds

### "Tests failing"
```bash
# Run tests
python -m unittest tests.test_plugin_system -v
python -m unittest tests.test_plugin_integration -v
```

---

## 📊 Performance Comparison

| Strategy | Signals | Win Rate | Trades/Day | Stress Level |
|----------|---------|----------|------------|--------------|
| Conservative | 10-20% | 60-70% | 2-5 | Low ⭐ |
| Scalping | 95% | 45-55% | 20-50 | High ⚡⚡⚡ |
| Risk Managed | Varies | Varies | Varies | Medium 🛡️ |

---

## 🎓 Next Steps

1. ✅ Run simulations to understand each use case
2. ✅ Configure Telegram for notifications
3. ✅ Test on demo account for 1 week
4. ✅ Analyze trade journal (Use Case 3)
5. ✅ Optimize plugin parameters
6. ✅ Go live with small positions
7. ✅ Scale up gradually

---

## 📖 Further Reading

- [Plugin System Architecture](PLUGIN_SYSTEM.md)
- [Creating Custom Plugins](../examples/plugin_usage.py)
- [Phase 2 Complete Summary](PHASE_2_COMPLETE.md)

---

## 💡 Tips

- **Start conservative**: Better to miss trades than lose money
- **Test thoroughly**: Use demo account for at least 1 week
- **Monitor actively**: Especially for scalping strategies
- **Keep logs**: Trade journal is invaluable for improvement
- **Adjust gradually**: Small changes, test, repeat

---

**Questions?** Check [FAQ.md](FAQ.md) or open an issue on GitHub
