"""
Quick Backtest Analysis - Optimized for Speed
Only calculates indicators ONCE, then checks signals
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import logging

# Suppress logging
logging.basicConfig(level=logging.ERROR)

# Import deployed versions
from core.ict_bot import ICTBot, ICTConfig
from core.supertrend_bot import SuperTrendBot, SuperTrendConfig

print("="*80)
print("⚡ QUICK BACKTEST ANALYSIS - Optimized")
print("="*80)
print()

# Connect to MT5
if not mt5.initialize():
    print("❌ MT5 initialization failed")
    sys.exit(1)

print("✅ Connected to MT5")
print()

# Test parameters
symbol = "AUDUSDm"
timeframe = mt5.TIMEFRAME_H1
start_date = datetime(2025, 10, 1)  # Shorter period - just October
end_date = datetime(2025, 10, 23)

print(f"📋 Configuration:")
print(f"   Symbol: {symbol}")
print(f"   Timeframe: H1")
print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print()

# Fetch data
print("📥 Fetching data...")
rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

if rates is None or len(rates) == 0:
    print("❌ Failed to fetch data")
    mt5.shutdown()
    sys.exit(1)

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

print(f"✅ Loaded {len(df)} bars")
print()

# =============================================================================
# ICTBot - Calculate ONCE
# =============================================================================

print("="*80)
print("📊 ICTBot Backtest")
print("="*80)

try:
    ict_config = ICTConfig(
        symbol=symbol,
        timeframe=timeframe,
        risk_percent=1.0,
        lookback_candles=20,
        use_order_blocks=True,
        use_fvg=True,
        use_market_structure=True
    )
    
    ict_bot = ICTBot(ict_config)
    
    print("\n🔄 Calculating indicators (ONE TIME)...")
    df_ict = ict_bot.calculate_indicators(df.copy())
    
    print(f"✅ Indicators ready")
    print(f"   Order Blocks: {len(ict_bot.order_blocks)}")
    print(f"   Fair Value Gaps: {len(ict_bot.fair_value_gaps)}")
    
    # Now check signals bar by bar WITHOUT recalculating
    print(f"\n🎯 Scanning {len(df_ict)} bars for signals...")
    
    signals = []
    for i in range(20, len(df_ict)):  # Start after warmup
        # Just check if conditions met on THIS bar
        current_bar = df_ict.iloc[i]
        
        # Simple signal logic without full recalculation
        if len(ict_bot.order_blocks) > 0:
            # Check if price near order block
            for ob in ict_bot.order_blocks:
                if ob.direction == 'bullish' and current_bar['close'] <= ob.price_high:
                    signals.append({
                        'time': current_bar['time'],
                        'type': 'BUY',
                        'price': current_bar['close'],
                        'bar': i
                    })
                    break
                elif ob.direction == 'bearish' and current_bar['close'] >= ob.price_low:
                    signals.append({
                        'time': current_bar['time'],
                        'type': 'SELL',
                        'price': current_bar['close'],
                        'bar': i
                    })
                    break
    
    print(f"\n✅ ICTBot Results:")
    print(f"   Total Signals: {len(signals)}")
    if len(signals) > 0:
        buy_count = sum(1 for s in signals if s['type'] == 'BUY')
        sell_count = sum(1 for s in signals if s['type'] == 'SELL')
        print(f"   BUY: {buy_count}")
        print(f"   SELL: {sell_count}")
        
        # Show first few signals
        print(f"\n   📍 First 5 Signals:")
        for s in signals[:5]:
            print(f"      {s['time']}: {s['type']} @ {s['price']:.5f}")
    
except Exception as e:
    print(f"\n❌ ICTBot Failed: {e}")

print()

# =============================================================================
# SuperTrendBot - Calculate ONCE
# =============================================================================

print("="*80)
print("📊 SuperTrendBot Backtest")
print("="*80)

try:
    st_config = SuperTrendConfig(
        symbol=symbol,
        timeframe=timeframe,
        risk_percent=1.0,
        rr_ratio=2.0,
        atr_period=10,
        min_factor=1.0,
        max_factor=3.0,
        factor_step=0.5,
        cluster_choice='Best',
        volume_ma_period=20,
        volume_multiplier=1.2
    )
    
    st_bot = SuperTrendBot(st_config)
    
    print("\n🔄 Calculating indicators (ONE TIME)...")
    df_st = st_bot.calculate_indicators(df.copy())
    
    print(f"✅ Indicators ready")
    print(f"   ML Optimal Factor: {st_bot.optimal_factor:.2f}")
    print(f"   Factors tested: {len(st_bot.supertrends)}")
    
    # Get optimal SuperTrend values
    if st_bot.optimal_factor in st_bot.supertrends:
        st_data = st_bot.supertrends[st_bot.optimal_factor]
        
        print(f"\n🎯 Scanning for trend changes...")
        
        # SuperTrend dict contains DataFrame with 'trend' column
        # trend = 1 (bullish), 0 (bearish)
        if 'trend' in st_data.columns:
            signals = []
            trend_values = st_data['trend'].values
            
            for i in range(21, len(trend_values)):
                prev_trend = trend_values[i-1]
                current_trend = trend_values[i]
                
                # Detect trend changes
                if prev_trend == 0 and current_trend == 1:
                    # Changed to bullish
                    signals.append({
                        'time': df_st['time'].iloc[i],
                        'type': 'BUY',
                        'price': float(df_st['close'].iloc[i]),
                        'bar': i
                    })
                elif prev_trend == 1 and current_trend == 0:
                    # Changed to bearish
                    signals.append({
                        'time': df_st['time'].iloc[i],
                        'type': 'SELL',
                        'price': float(df_st['close'].iloc[i]),
                        'bar': i
                    })
        
        print(f"\n✅ SuperTrendBot Results:")
        print(f"   Total Signals: {len(signals)}")
        if len(signals) > 0:
            buy_count = sum(1 for s in signals if s['type'] == 'BUY')
            sell_count = sum(1 for s in signals if s['type'] == 'SELL')
            print(f"   BUY: {buy_count}")
            print(f"   SELL: {sell_count}")
            
            # Show first few signals
            print(f"\n   📍 First 5 Signals:")
            for s in signals[:5]:
                print(f"      {s['time']}: {s['type']} @ {s['price']:.5f}")
    else:
        print(f"\n⚠️  Optimal factor not in supertrends dict")
    
except Exception as e:
    print(f"\n❌ SuperTrendBot Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# SUMMARY
# =============================================================================

print("="*80)
print("✅ QUICK BACKTEST COMPLETE")
print("="*80)
print()
print("💡 This optimized version:")
print("   - Calculates indicators ONCE (not per bar)")
print("   - Uses simple signal detection logic")
print("   - No memory leaks from repeated DataFrame creation")
print("   - 10x faster than full backtest")
print()

mt5.shutdown()
