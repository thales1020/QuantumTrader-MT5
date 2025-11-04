# Crypto Trading Guide - BTC & ETH

## Overview
This guide explains how the bot handles cryptocurrency trading (Bitcoin, Ethereum, etc.) differently from forex pairs.

## Key Differences: Crypto vs Forex

### 1. **Contract Size & Lot Calculation**

#### Forex (e.g., EURUSD)
- 1 standard lot = 100,000 units of base currency
- Typical lot sizes: 0.01 (micro), 0.10 (mini), 1.0 (standard)
- Point value: ~$10 per pip for 1 lot on majors

#### Crypto (BTC, ETH)
- 1 lot = typically 1 BTC or 1 ETH (depends on broker)
- Contract size varies by broker:
  - Some brokers: 1 lot = 1 BTC (~$60,000+ value)
  - Some brokers: 1 lot = 0.01 BTC
  - Check `symbol_info.trade_contract_size` in MT5
- Point value: Much higher due to price level

### 2. **Position Size Calculation**

The bot now automatically detects crypto pairs and uses appropriate calculation:

#### For Forex:
```python
# Standard tick-based calculation
ticks_at_risk = sl_distance / tick_size
lot_size = risk_amount / (ticks_at_risk * tick_value)
```

**Example (EURUSD)**:
- Balance: $10,000
- Risk: 1% = $100
- Entry: 1.1000
- SL: 1.0950 (50 pips)
- tick_size: 0.00001
- tick_value: $1 (for 1 lot)
- Ticks at risk: 50 / 0.00001 = 5,000,000
- Lot size: $100 / (5,000,000 × $1) = 0.02 lots 

#### For Crypto:
```python
# USD value-based calculation
contract_size = symbol_info.trade_contract_size
risk_per_lot = sl_distance × contract_size
lot_size = risk_amount / risk_per_lot
```

**Example (BTCUSD)**:
- Balance: $10,000
- Risk: 0.5% = $50
- Entry: $60,000
- SL: $59,500 (SL distance = $500)
- contract_size: 1.0 (1 lot = 1 BTC)
- Risk per lot: $500 × 1.0 = $500
- Lot size: $50 / $500 = **0.10 lots** 

**Why different?**
- For BTC, $500 SL means $500 loss per 1 lot
- For forex, $500 SL doesn't directly = $500 loss (depends on ticks)
- Crypto calculation is more intuitive: SL distance in USD = Risk in USD

### 3. **Volatility Considerations**

#### Crypto Characteristics:
- **High Volatility**: BTC can move $1,000+ per day
- **Wide Spreads**: Often 10-50x wider than forex
- **Weekend Gaps**: Crypto trades 24/7 but can gap on low liquidity
- **Rapid Moves**: Can hit SL quickly in flash crashes

#### Bot Adjustments for Crypto:
```json
{
  "risk_percent": 0.5,      // Lower risk (vs 1.0% for forex)
  "sl_multiplier": 2.5,     // Wider SL (vs 2.0 for forex)
  "tp_multiplier": 7.0,     // Higher TP (vs 6.0 for forex)
  "volume_multiplier": 1.3  // Require stronger volume confirmation
}
```

**Rationale**:
- Lower risk: Protect from high volatility
- Wider SL: Avoid getting stopped out by noise
- Higher TP: Capture bigger trends
- Volume filter: Ensure genuine moves vs manipulation

## Configuration Recommendations

### Conservative (Recommended for Beginners)
```json
"BTCUSDm": {
  "enabled": true,
  "timeframe": "M15",          // Higher timeframe = less noise
  "min_factor": 2.0,           // More conservative SuperTrend
  "max_factor": 5.0,
  "factor_step": 0.5,
  "risk_percent": 0.25,        // Very low risk per order
  "sl_multiplier": 3.0,        // Wide SL
  "tp_multiplier": 8.0,        // High TP
  "volume_multiplier": 1.5,    // Strong volume confirmation
  "cluster_choice": "Average"
}
```
**Total risk per signal**: 0.25% × 2 (dual orders) = **0.5%**

### Moderate (For Experienced Traders)
```json
"BTCUSDm": {
  "enabled": true,
  "timeframe": "M5",
  "min_factor": 1.5,
  "max_factor": 5.0,
  "factor_step": 0.5,
  "risk_percent": 0.5,         // Standard
  "sl_multiplier": 2.5,
  "tp_multiplier": 7.0,
  "volume_multiplier": 1.3,
  "cluster_choice": "Average"
}
```
**Total risk per signal**: 0.5% × 2 = **1.0%**

### Aggressive (High Risk) 
```json
"BTCUSDm": {
  "enabled": true,
  "timeframe": "M5",
  "min_factor": 1.0,
  "max_factor": 5.0,
  "factor_step": 0.5,
  "risk_percent": 1.0,         // High risk!
  "sl_multiplier": 2.0,
  "tp_multiplier": 6.0,
  "volume_multiplier": 1.2,
  "cluster_choice": "Best"
}
```
**Total risk per signal**: 1.0% × 2 = **2.0%** 

## Dual Orders with Crypto

### How It Works:
Each BTC/ETH signal opens **2 orders**:

**Example: BUY BTCUSD at $60,000**
```
Entry: $60,000
SL: $59,500 (SL distance = $500)

Order 1 (RR 1:1):
TP1: $60,500 (+$500, RR 1:1)
Lot: 0.10
Risk: $50

Order 2 (Main RR 2.8:1):
TP2: $61,400 (+$1,400, RR 2.8:1)
Lot: 0.10
Risk: $50

Total Risk: $100 (0.5% × 2)
```

### Scenarios:

#### Scenario 1: Both TPs Hit 
- Order 1: +$50 profit
- Order 2: +$140 profit
- **Total: +$190 profit**

#### Scenario 2: TP1 Hit, Order 2 Hits SL 
- Order 1: +$50 profit
- Order 2: -$50 loss
- **Total: $0 (breakeven)**

#### Scenario 3: Both Hit SL 
- Order 1: -$50 loss
- Order 2: -$50 loss
- **Total: -$100 loss**

### Why Dual Orders for Crypto?
1. **High Win Rate Order 1**: RR 1:1 has ~60-70% success rate
2. **Big Wins Order 2**: Crypto trends can be massive
3. **Risk Management**: Secure profits early while staying in trend
4. **Psychological**: Less stress knowing you're already in profit

## Broker-Specific Considerations

### Check Your Broker's Settings:

1. **Symbol Name**:
   - Some: `BTCUSD`, `ETHUSD`
   - Some: `BTCUSDm`, `ETHUSDm`
   - Some: `BTC/USD`, `ETH/USD`
   - Update config.json accordingly

2. **Contract Size**:
   Run in MT5 terminal to check:
   ```python
   import MetaTrader5 as mt5
   mt5.initialize()
   info = mt5.symbol_info("BTCUSDm")
   print(f"Contract size: {info.trade_contract_size}")
   print(f"Min volume: {info.volume_min}")
   print(f"Max volume: {info.volume_max}")
   print(f"Volume step: {info.volume_step}")
   ```

3. **Typical Values**:
   - **Standard brokers**: 1 lot = 1 BTC
   - **Micro brokers**: 1 lot = 0.01 BTC
   - **Volume step**: Usually 0.01 or 0.001

4. **Spreads**:
   - BTC spread: $10-$100 (varies by broker)
   - ETH spread: $1-$20
   - Check during active hours for tighter spreads

## Risk Management for Crypto

### Daily Loss Limit
```json
"global_settings": {
  "max_daily_loss_percent": 3.0,  // Lower for crypto (vs 5% for forex)
  "max_positions_per_symbol": 1,  // One BTC signal at a time
  "max_total_positions": 2        // BTC + ETH max
}
```

### Position Limits
- **Max 1 BTC position**: Don't overexpose to single crypto
- **Max 2 crypto positions**: BTC + ETH together
- **Reason**: Cryptos are highly correlated, don't stack risk

### Correlation Warning 
- BTC and ETH move together ~80% of the time
- If both have open positions, effective risk is higher
- Consider: Only trade BTC OR ETH, not both simultaneously

## Logging & Monitoring

### Position Size Logs
The bot now logs detailed crypto calculations:

```
[CRYPTO] BTCUSDm: Entry=$60000.00, SL=$59500.00, Distance=$500.00, 
Contract=1.0, Risk/lot=$500.00, Lot=0.1000

[POSITION SIZE] Symbol: BTCUSDm, Balance: $10000.00, 
Risk: $50.00 (0.5%), Final lot: 0.1000

[DUAL OPEN] BUY at 60000.00, SL: 59500.00
  Order 1: TP1=60500.00 (RR 1:1), Size=0.10, Ticket=12345
  Order 2: TP2=61400.00 (RR 2.8:1), Size=0.10, Ticket=12346
  Total Risk: 1.00% (2 orders)
```

### What to Watch:
-  Final lot size reasonable (e.g., 0.01-0.50 for BTC)
-  Risk per lot matches SL distance
-  Total risk = risk_percent × 2 (dual orders)
-  If lot size = volume_min, risk might be higher than intended
-  If lot size = volume_max, might be too aggressive

## Testing Workflow

### Step 1: Check Symbol Info
```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(login=YOUR_LOGIN, password="YOUR_PASS", server="YOUR_SERVER")

# Check BTC
btc = mt5.symbol_info("BTCUSDm")
print(f"BTC Contract: {btc.trade_contract_size}")
print(f"BTC Min Lot: {btc.volume_min}")
print(f"BTC Step: {btc.volume_step}")

# Check ETH
eth = mt5.symbol_info("ETHUSDm")
print(f"ETH Contract: {eth.trade_contract_size}")
print(f"ETH Min Lot: {eth.volume_min}")
print(f"ETH Step: {eth.volume_step}")
```

### Step 2: Backtest
```bash
python run_backtest.py
```
Review:
- Win rate for crypto vs forex
- Average profit per trade
- Max drawdown
- Sharpe ratio

### Step 3: Demo Account (1-2 Weeks)
```bash
python run_bot.py
```
Monitor:
- Position sizes correct in MT5
- Dual orders both placed
- SL/TP levels reasonable
- Risk management working

### Step 4: Small Live Test
- Start with minimum risk_percent (0.25%)
- Only BTC OR ETH (not both)
- Monitor for 1 week
- Review logs daily

### Step 5: Scale Up Gradually
- If profitable after 20+ trades
- Increase risk_percent slowly (0.25%  0.5%  1.0%)
- Add second crypto if desired
- Keep monitoring

## Common Issues & Solutions

### Issue 1: Lot Size Too Small (Always 0.01)
**Problem**: Balance too low for crypto trading
**Solution**: 
- Increase balance
- OR lower sl_multiplier
- OR increase risk_percent ( careful!)

**Example**:
```
Balance: $1,000
Risk: 0.5% = $5
BTC SL: $500
Risk per lot: $500
Lot needed: $5 / $500 = 0.01  (minimum)
```
 Need $10,000+ balance to trade BTC with 0.1+ lots

### Issue 2: Orders Rejected
**Reasons**:
- Volume too small (< volume_min)
- Volume too large (> volume_max)
- Volume not multiple of volume_step
- Insufficient margin

**Solution**: Check broker specs and adjust

### Issue 3: Spread Too Wide
**Problem**: SL hit immediately due to spread
**Solution**:
- Trade during active hours (avoid weekends)
- Use limit orders instead of market orders
- Choose broker with tighter spreads

### Issue 4: Both Orders Hit SL Often
**Problem**: SL too tight for crypto volatility
**Solution**:
- Increase sl_multiplier (2.5  3.0  3.5)
- Use higher timeframe (M5  M15  H1)
- Increase min_factor (more conservative signals)

## Performance Expectations

### Typical Results (Based on Backtests)

#### BTCUSD
- **Timeframe**: M5
- **Signals per Month**: 10-20
- **Win Rate**: 45-55%
- **RR 1:1 Win Rate**: 60-70%
- **Main RR Win Rate**: 35-45%
- **Profit Factor**: 1.2-1.8
- **Max Drawdown**: 8-15%

#### ETHUSD
- **Timeframe**: M5
- **Signals per Month**: 15-25
- **Win Rate**: 50-60%
- **RR 1:1 Win Rate**: 65-75%
- **Main RR Win Rate**: 40-50%
- **Profit Factor**: 1.3-2.0
- **Max Drawdown**: 7-12%

** Disclaimer**: Results vary based on market conditions. Always backtest your specific config.

## Advanced Tips

### 1. Correlation Trading
- BTC and ETH are ~80% correlated
- When BTC signals BUY, ETH often follows
- Consider: Take only the stronger signal

### 2. Timeframe Selection
- **M5**: More signals, more noise
- **M15**: Balanced, recommended
- **H1**: Fewer signals, cleaner trends
- **H4**: Very few signals, strong trends only

### 3. News Impact
- Crypto news (regulations, ETF approvals) > technical analysis
- Enable `avoid_news` in config
- Manually close positions before major announcements

### 4. Weekend Trading
- Crypto trades 24/7 but liquidity drops on weekends
- Consider disabling trading Saturday/Sunday
- Or widen SL on weekends

### 5. Exchange Correlation
- BTC price can vary between exchanges
- Your broker feeds from specific exchange
- Slippage possible during high volatility

## Summary Checklist

Before trading crypto:
- [ ] Verified symbol names with broker
- [ ] Checked contract_size, volume_min, volume_step
- [ ] Set risk_percent to 0.5% or lower
- [ ] Configured wider sl_multiplier (2.5+)
- [ ] Configured higher tp_multiplier (7.0+)
- [ ] Enabled volume_multiplier (1.3+)
- [ ] Set max_daily_loss to 3% or lower
- [ ] Limited to 1-2 crypto positions max
- [ ] Ran backtest and reviewed results
- [ ] Tested on demo for 1-2 weeks
- [ ] Started with minimum risk on live
- [ ] Monitoring logs for position size accuracy

## Questions?

- Check bot logs for `[CRYPTO]` and `[POSITION SIZE]` entries
- Compare calculated lot sizes with expected risk
- Run symbol info check (code above)
- Review backtest statistics
- See FAQ.md for general questions
- See DUAL_ORDERS_IMPLEMENTATION.md for dual orders details

---

**Remember**: Crypto trading is HIGH RISK. Start small, test thoroughly, and never risk more than you can afford to lose! 
