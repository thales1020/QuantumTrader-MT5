# Plugin System Use Cases

This directory contains real-world use cases demonstrating the plugin system capabilities.

## Use Cases Overview

### 1. Conservative Trading (use_case_1_conservative.py)
**Scenario**: Risk-averse trader wants multiple filters before trading
- RSI filter (only trade in extreme conditions)
- Volume filter (require high volume)
- Time filter (avoid news hours)
- **Goal**: Reduce false signals, improve win rate

### 2. Aggressive Scalping (use_case_2_scalping.py)
**Scenario**: Active trader wants quick notifications and tight filters
- Quick Telegram alerts on every signal
- Momentum filter (only strong trends)
- No additional filters (fast execution)
- **Goal**: Maximize trading opportunities

### 3. Risk Management (use_case_3_risk_management.py)
**Scenario**: Professional trader with strict risk controls
- Maximum drawdown monitor
- Daily loss limit
- Position size calculator
- Trade journal logger
- **Goal**: Protect capital, track performance

### 4. Multi-Strategy Portfolio (use_case_4_multi_strategy.py)
**Scenario**: Run multiple bots with different plugins
- SuperTrend bot with RSI filter
- ICT bot with volume filter
- Different Telegram channels for each
- **Goal**: Diversify strategies, reduce correlation

### 5. Custom Indicator Integration (use_case_5_custom_indicator.py)
**Scenario**: Trader wants to add proprietary indicator
- Custom MACD divergence plugin
- Custom support/resistance plugin
- Combine with existing strategies
- **Goal**: Enhance edge with custom signals

### 6. Notification Hub (use_case_6_notifications.py)
**Scenario**: Monitor multiple bots from one place
- Telegram notifications
- Discord webhooks
- Email alerts
- SMS notifications (Twilio)
- **Goal**: Never miss important events

## Running Use Cases

Each use case has its own script:

```bash
# Use Case 1: Conservative Trading
python examples/use_cases/use_case_1_conservative.py

# Use Case 2: Aggressive Scalping
python examples/use_cases/use_case_2_scalping.py

# Use Case 3: Risk Management
python examples/use_cases/use_case_3_risk_management.py

# Use Case 4: Multi-Strategy Portfolio
python examples/use_cases/use_case_4_multi_strategy.py

# Use Case 5: Custom Indicator
python examples/use_cases/use_case_5_custom_indicator.py

# Use Case 6: Notification Hub
python examples/use_cases/use_case_6_notifications.py
```

## Configuration

Each use case includes:
- ✅ Complete configuration example
- ✅ Plugin setup code
- ✅ Expected behavior description
- ✅ Performance expectations

## Testing

Run all use cases in test mode:
```bash
python scripts/test_all_use_cases.py
```

This will simulate each use case without live trading.
