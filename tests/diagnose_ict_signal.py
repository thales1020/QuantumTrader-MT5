"""
Deep dive diagnostic: Why is refactored ICTBot not generating signals?
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

from core.ict_bot import ICTBot as OriginalICTBot
from core.ict_bot import Config as OriginalConfig
from core.ict_bot_refactored import ICTBot as RefactoredICTBot
from core.ict_bot_refactored import ICTConfig

def diagnose_signal_generation():
    """Step-by-step diagnosis of signal generation"""
    
    print("="*80)
    print("🔍 DIAGNOSTIC: Signal Generation Logic")
    print("="*80)
    
    # Connect to MT5
    if not mt5.initialize():
        print("❌ MT5 not initialized")
        return
    
    symbol = "EURUSDm"
    
    # Get data
    print(f"\n📊 Fetching {symbol} data...")
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 500)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    print(f"✅ Got {len(df)} bars")
    
    # Test Original Bot
    print("\n" + "="*80)
    print("1️⃣  ORIGINAL BOT - Step by Step")
    print("="*80)
    
    original_config = OriginalConfig(symbol=symbol, use_order_blocks=True, use_fvg=True)
    original_bot = OriginalICTBot(original_config)
    
    print("\n📍 Step 1: Market Structure")
    original_bot.identify_market_structure(df)
    print(f"   Trend: {original_bot.market_structure.get('trend', 'N/A')}")
    print(f"   Highs: {len(original_bot.market_structure.get('highs', []))}")
    print(f"   Lows: {len(original_bot.market_structure.get('lows', []))}")
    
    print("\n📍 Step 2: Order Blocks")
    original_bot.identify_order_blocks(df)
    print(f"   Found: {len(original_bot.order_blocks)} order blocks")
    if original_bot.order_blocks:
        latest_ob = original_bot.order_blocks[0]
        print(f"   Latest: {latest_ob.direction} @ {latest_ob.price_low:.5f}-{latest_ob.price_high:.5f}")
    
    print("\n📍 Step 3: Fair Value Gaps")
    original_bot.identify_fair_value_gaps(df)
    print(f"   Found: {len(original_bot.fair_value_gaps)} FVGs")
    if original_bot.fair_value_gaps:
        latest_fvg = original_bot.fair_value_gaps[0]
        print(f"   Latest: {latest_fvg.direction} @ {latest_fvg.bottom:.5f}-{latest_fvg.top:.5f}")
    
    print("\n📍 Step 4: Generate Signal")
    original_signal = original_bot.generate_signal(df)
    if original_signal:
        print(f"   ✅ SIGNAL GENERATED: {original_signal.get('type', original_signal.get('direction'))}")
        print(f"   Price: {original_signal.get('price', 0):.5f}")
        print(f"   Conditions: {original_signal.get('conditions', 'N/A')}")
    else:
        print(f"   ❌ NO SIGNAL")
    
    # Test Refactored Bot
    print("\n" + "="*80)
    print("2️⃣  REFACTORED BOT - Step by Step")
    print("="*80)
    
    refactored_config = ICTConfig(symbol=symbol, use_order_blocks=True, use_fvg=True)
    refactored_bot = RefactoredICTBot(refactored_config)
    
    print("\n📍 Step 1: Calculate Indicators (calls all methods)")
    refactored_bot.calculate_indicators(df)
    
    print(f"\n📍 After calculate_indicators():")
    print(f"   Market Structure Trend: {refactored_bot.market_structure.get('trend', 'N/A')}")
    print(f"   Order Blocks: {len(refactored_bot.order_blocks)}")
    print(f"   Fair Value Gaps: {len(refactored_bot.fair_value_gaps)}")
    
    if refactored_bot.order_blocks:
        print(f"\n📍 Order Blocks Details:")
        for i, ob in enumerate(refactored_bot.order_blocks[:3], 1):
            print(f"      {i}. {ob.direction} @ {ob.price_low:.5f}-{ob.price_high:.5f} (strength: {ob.strength:.2f})")
    
    if refactored_bot.fair_value_gaps:
        print(f"\n📍 FVG Details:")
        for i, fvg in enumerate(refactored_bot.fair_value_gaps[:3], 1):
            print(f"      {i}. {fvg.direction} @ {fvg.bottom:.5f}-{fvg.top:.5f}")
    else:
        print(f"\n⚠️  No FVGs found")
    
    print("\n📍 Step 2: Generate Signal")
    refactored_signal = refactored_bot.generate_signal(df)
    if refactored_signal:
        print(f"   ✅ SIGNAL GENERATED: {refactored_signal.get('type')}")
        print(f"   Price: {refactored_signal.get('price', 0):.5f}")
        print(f"   Confidence: {refactored_signal.get('confidence', 0):.1f}%")
        print(f"   Reason: {refactored_signal.get('reason', 'N/A')}")
        if 'metadata' in refactored_signal:
            meta = refactored_signal['metadata']
            print(f"   Metadata:")
            print(f"      - Order Block: {meta.get('order_block', 'None')}")
            print(f"      - FVG: {meta.get('fvg', 'None')}")
            print(f"      - Setup: {meta.get('setup_type', 'N/A')}")
    else:
        print(f"   ❌ NO SIGNAL")
        print(f"\n   🔍 Debugging generate_signal():")
        
        # Check current price
        current_price = df['close'].iloc[-1]
        print(f"      Current price: {current_price:.5f}")
        
        # Check what generate_signal needs
        print(f"      Config:")
        print(f"         - use_order_blocks: {refactored_bot.config.use_order_blocks}")
        print(f"         - use_fvg: {refactored_bot.config.use_fvg}")
        print(f"         - use_market_structure: {refactored_bot.config.use_market_structure}")
        
        # Manually check conditions
        trend = refactored_bot.market_structure.get('trend')
        print(f"      Trend: {trend}")
        
        if trend == 'bullish':
            print(f"      ✅ Bullish trend detected")
            # Check if there are bullish order blocks
            bullish_obs = [ob for ob in refactored_bot.order_blocks if ob.direction == 'bullish']
            print(f"      Bullish OBs: {len(bullish_obs)}")
            if bullish_obs:
                ob = bullish_obs[0]
                ob_price = (ob.price_low + ob.price_high) / 2
                print(f"         Latest OB: {ob_price:.5f}, Current: {current_price:.5f}")
                if current_price >= ob.price_low * 0.9999:  # Near OB
                    print(f"         ✅ Price near OB")
                else:
                    print(f"         ❌ Price NOT near OB (too far)")
            else:
                print(f"         ❌ No bullish OBs")
        elif trend == 'bearish':
            print(f"      ✅ Bearish trend detected")
            bearish_obs = [ob for ob in refactored_bot.order_blocks if ob.direction == 'bearish']
            print(f"      Bearish OBs: {len(bearish_obs)}")
        else:
            print(f"      ❌ Neutral trend - no signal")
    
    # Compare
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("="*80)
    
    print(f"\n🔷 Order Blocks:")
    print(f"   Original:    {len(original_bot.order_blocks)}")
    print(f"   Refactored:  {len(refactored_bot.order_blocks)}")
    
    print(f"\n🔷 Fair Value Gaps:")
    print(f"   Original:    {len(original_bot.fair_value_gaps)}")
    print(f"   Refactored:  {len(refactored_bot.fair_value_gaps)}")
    
    print(f"\n🔷 Market Structure:")
    orig_trend = original_bot.market_structure.get('trend', 'unknown')
    ref_trend = refactored_bot.market_structure.get('trend', 'unknown')
    print(f"   Original:    {orig_trend}")
    print(f"   Refactored:  {ref_trend}")
    print(f"   Match: {'✅' if orig_trend == ref_trend else '❌'}")
    
    print(f"\n🔷 Signal Generation:")
    orig_sig = "Generated" if original_signal else "None"
    ref_sig = "Generated" if refactored_signal else "None"
    print(f"   Original:    {orig_sig}")
    print(f"   Refactored:  {ref_sig}")
    print(f"   Match: {'✅' if (bool(original_signal) == bool(refactored_signal)) else '❌'}")
    
    mt5.shutdown()
    
    print("\n" + "="*80)
    print("✅ DIAGNOSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    diagnose_signal_generation()
