# Dual Orders Implementation - RR 1:1 + Main RR

## Overview
All trading strategies now implement **Dual Orders** feature where each signal opens TWO positions:
- **Order 1**: Quick profit with RR 1:1 (Risk:Reward = 1:1)
- **Order 2**: Main profit with configured RR ratio (e.g., RR 2:1, RR 3:1)

This strategy allows capturing quick profits while maintaining exposure to larger moves.

## Affected Bots

###  1. SuperTrend Bot (`core/supertrend_bot.py`)
**Implementation**: NEW - Added in this update

**Key Changes**:
- Added `place_dual_orders()` method
- Updated BUY/SELL signal handling in `run_cycle()`
- Order comments: `ST_BUY_RR1`, `ST_BUY_RR2`, `ST_SELL_RR1`, `ST_SELL_RR2`

**Example**:
```python
# BUY Signal with ATR=50 pips, SL Multiplier=1.5, TP Multiplier=3.0
Entry: 1.1000
SL: 1.0925 (50 * 1.5 = 75 pips below)
TP1: 1.1075 (RR 1:1 - same 75 pips above) ← Order 1
TP2: 1.1150 (RR 2:1 - 150 pips above)    ← Order 2
```

###  2. ICT Bot SMC (`core/ict_bot_smc.py`)
**Implementation**: EXISTING - Already has dual orders

**Features**:
- Dual orders with RR 1:1 + RR 3:1
- Order comments: `ICT_BUY_QUICK`, `ICT_BUY_MAIN`, etc.
- Advanced Smart Money Concepts (SMC) integration

###  3. ICT Bot (`core/ict_bot.py`)
**Implementation**: NEW - Added in this update

**Key Changes**:
- Updated `open_position()` method to place dual orders
- Order comments: `ICT_BUY_RR1`, `ICT_BUY_RR2`, `ICT_SELL_RR1`, `ICT_SELL_RR2`
- Rollback mechanism if Order 2 fails (closes Order 1)

**Example**:
```python
# SELL Signal with Order Block, RR Ratio=2.0
Entry: 1.1000
SL: 1.1080 (above order block)
TP1: 1.0920 (RR 1:1 - 80 pips below) ← Order 1
TP2: 1.0840 (RR 2:1 - 160 pips below) ← Order 2
```

## Backtest Engine Update

### Updated: `engines/backtest_engine.py`
**Key Changes**:
1. **Dual Position Tracking**:
   - `open_position` now stores `order1` and `order2` separately
   - Each order has its own TP and active status
   - Shared SL for both orders

2. **New Method**: `_close_single_order()`
   - Closes individual orders (Order 1 or Order 2)
   - Records each order's P&L separately
   - Adds `order_type` field: `'RR_1:1'` or `'Main_RR'`

3. **Updated Methods**:
   - `_open_position()`: Opens dual orders with TP1 (RR 1:1) and TP2 (Main RR)
   - `_update_position()`: Checks SL/TP for both orders independently
   - `_close_position()`: Closes all remaining active orders
   - `_calculate_equity()`: Sums unrealized P&L from both active orders

4. **Enhanced Reporting**:
   - Separates RR 1:1 vs Main RR statistics
   - Shows win rate for each order type
   - Displays total P&L contribution from each strategy

**Example Backtest Output**:
```
Total Trades: 100 (Dual Orders Strategy)
  - RR 1:1 Orders: 50
  - Main RR Orders: 50

--- RR 1:1 Orders Performance ---
Wins/Losses: 35/15
Win Rate: 70.00%
Total P&L: $1,250.00

--- Main RR Orders Performance ---
Wins/Losses: 25/25
Win Rate: 50.00%
Total P&L: $2,500.00
```

## Risk Management Considerations

###  CRITICAL: Double Risk per Signal
Each signal now opens **2 orders**, which means:
- **Total Risk = 2 × risk_percent**
- If `risk_percent = 1.0%`, total exposure per signal = **2.0%**
- If `risk_percent = 2.0%`, total exposure per signal = **4.0%**

### Recommended Settings
For conservative trading with dual orders:
```json
{
  "risk_percent": 0.5,  // 0.5% per order = 1.0% total
  "max_daily_loss": 2.0, // Stop trading if daily loss > 2%
  "max_positions": 1     // One signal = 2 orders
}
```

For moderate trading:
```json
{
  "risk_percent": 1.0,  // 1.0% per order = 2.0% total
  "max_daily_loss": 3.0,
  "max_positions": 1
}
```

### Risk Warnings Logged
All bots now log total risk warnings:
```
[2025-01-16 14:30:00] [DUAL OPEN] BUY at 1.10000, SL: 1.09250
  Order 1: TP1=1.10750 (RR 1:1), Size=0.05, Ticket=12345
  Order 2: TP2=1.11500 (RR 2:1), Size=0.05, Ticket=12346
  Total Risk: 2.00% (2 orders)  ← WARNING
```

## Testing

### Unit Tests Needed
- [x] Backtest engine dual orders tracking 
- [ ] SuperTrend Bot dual orders placement
- [ ] ICT Bot dual orders placement
- [ ] Total risk calculation verification
- [ ] Order rollback mechanism (ICT Bot)

### Test Scenarios
1. **Both Orders Hit TP**:
   - Order 1 hits TP1 (RR 1:1)  Closes with profit
   - Order 2 hits TP2 (Main RR)  Closes with larger profit
   - Total P&L = P&L1 + P&L2 

2. **Order 1 Hits TP, Order 2 Hits SL**:
   - Order 1 hits TP1  Small profit
   - Order 2 hits SL  Loss
   - Net P&L = Small profit - Loss (usually small loss or breakeven)

3. **Both Orders Hit SL**:
   - Both orders hit SL simultaneously
   - Total Loss = 2 × risk_amount
   - Risk management limits should catch this 

## Advantages

### 1. Profit Optimization
- Secure quick profits with RR 1:1
- Maintain exposure to larger moves with Main RR
- Reduces psychological pressure of "what if I close too early"

### 2. Better Win Rate
- RR 1:1 has higher hit probability (~60-70%)
- Main RR has lower hit probability (~40-50%)
- Combined strategy balances win rate vs profit size

### 3. Reduced Regret
- If price reverses after small profit, Order 1 already secured gains
- If price continues trending, Order 2 captures larger moves
- "Best of both worlds" approach

## Disadvantages

### 1. Doubled Risk per Signal
- Each signal risks **2 × risk_percent**
- Requires halving risk_percent to maintain same exposure
- Must update risk management settings 

### 2. More Commission/Spread
- 2 orders = 2× spread cost
- 2 orders = 2× commission
- Can reduce profitability on tight markets

### 3. Complexity
- More orders to track in live trading
- More complex backtest results
- Requires careful position management

## Migration Guide

### For Existing Users

**Step 1**: Update Configuration
```json
{
  "risk_percent": 0.5,  // Halve your previous risk_percent
  "max_daily_loss": 2.0, // Adjust accordingly
  "max_positions": 1     // Keep as is (1 signal = 2 orders now)
}
```

**Step 2**: Run Backtest
```bash
python run_backtest.py
```
Check the new dual orders statistics in the output.

**Step 3**: Test on Demo Account
```bash
python run_bot.py  # SuperTrend Bot
# or
python run_ict_bot.py  # ICT Bot
```
Verify that dual orders are placed correctly.

**Step 4**: Monitor Initial Trades
- Check MT5 to confirm 2 orders per signal
- Verify comments: `ST_BUY_RR1`, `ST_BUY_RR2`, etc.
- Monitor total risk exposure
- Ensure risk limits are working

## Configuration Examples

### Conservative Dual Orders (1% total risk)
```json
{
  "symbol": "EURUSD",
  "risk_percent": 0.5,      // 0.5% × 2 = 1% total
  "tp_multiplier": 3.0,     // Main RR = 2:1 (TP=3.0, SL=1.5)
  "sl_multiplier": 1.5,
  "max_daily_loss": 2.0,
  "max_positions": 1
}
```

### Aggressive Dual Orders (4% total risk) 
```json
{
  "symbol": "XAUUSD",
  "risk_percent": 2.0,      // 2.0% × 2 = 4% total 
  "tp_multiplier": 4.0,     // Main RR = 3:1 (TP=4.0, SL=1.33)
  "sl_multiplier": 1.33,
  "max_daily_loss": 5.0,
  "max_positions": 1
}
```

## Logging Format

### SuperTrend Bot
```
[2025-01-16 14:30:00] [DUAL OPEN] BUY at 1.10000, SL: 1.09250
  Order 1: TP1=1.10750 (RR 1:1), Size=0.05
  Order 2: TP2=1.11500 (RR 2:1), Size=0.05
  Total Risk: 2.00% (2 orders)

[2025-01-16 15:15:00] [CLOSE] BUY RR_1:1 at 1.10750, P&L: $37.50 (75.0 pips) - Take Profit - Order 1 (RR 1:1) | Balance: $10,037.50
[2025-01-16 16:30:00] [CLOSE] BUY Main_RR at 1.11500, P&L: $75.00 (150.0 pips) - Take Profit - Order 2 (Main RR) | Balance: $10,112.50
```

### ICT Bot
```
[2025-01-16 14:30:00] [DUAL OPEN] SELL at 1.10000, SL: 1.10800, Conditions: 4
  Order 1: TP1=1.09200 (RR 1:1), Size=0.05, Ticket=12345
  Order 2: TP2=1.08400 (RR 2.0:1), Size=0.05, Ticket=12346
  Total Risk: 2.00% (2 orders)
```

## Future Enhancements

### Planned Features
- [ ] Configurable RR 1:1 vs custom RR for Order 1
- [ ] Optional trailing stop for Order 2
- [ ] Partial close strategies (close 50% at RR 1:1, trail the rest)
- [ ] Dynamic lot sizing per order (e.g., 70% Order 1, 30% Order 2)

### Analysis Tools
- [ ] Separate Order 1 vs Order 2 P&L analysis
- [ ] Optimal RR ratio finder
- [ ] Commission impact calculator

## Summary

 **All bots now support dual orders**:
- SuperTrend Bot: NEW implementation
- ICT Bot SMC: Already supported
- ICT Bot: NEW implementation

 **Backtest engine updated**:
- Tracks dual orders separately
- Shows RR 1:1 vs Main RR statistics
- Calculates combined P&L correctly

 **Risk management updated**:
- Total risk = 2 × risk_percent per signal
- Adjust configuration accordingly
- Monitor total exposure carefully

 **Testing recommended**:
- Run backtests to verify performance
- Test on demo account first
- Monitor initial live trades closely

## Questions or Issues?

See:
- `tests/test_live_trading.py` - Live trading tests
- `tests/LIVE_TRADING_TESTS.md` - Test documentation
- `PERFORMANCE.md` - Performance guidelines
- `FAQ.md` - Frequently asked questions
