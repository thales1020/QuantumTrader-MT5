"""
Test ICTBot Refactored with Real MT5 Connection
Compare original vs refactored on actual market data
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import MetaTrader5 as mt5
import pandas as pd

# Import original ICTBot
from core.ict_bot import ICTBot as OriginalICTBot
from core.ict_bot import Config as OriginalConfig

# Import refactored ICTBot
from core.ict_bot_refactored import ICTBot as RefactoredICTBot
from core.ict_bot_refactored import ICTConfig

def test_mt5_connection():
    """Test if MT5 is available and connected"""
    print("\n" + "="*80)
    print("🔌 Testing MT5 Connection")
    print("="*80)
    
    if not mt5.initialize():
        print("❌ MT5 not initialized. Please ensure:")
        print("   1. MetaTrader 5 is installed")
        print("   2. MT5 terminal is running")
        print("   3. You're logged into a demo/live account")
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        print("❌ Not logged into MT5 account")
        mt5.shutdown()
        return False
    
    print(f"✅ MT5 Connected Successfully")
    print(f"   Account: {account_info.login}")
    print(f"   Server: {account_info.server}")
    print(f"   Balance: ${account_info.balance:.2f}")
    print(f"   Equity: ${account_info.equity:.2f}")
    
    return True

def get_real_market_data(symbol: str = "EURUSDm", timeframe=mt5.TIMEFRAME_M15, bars: int = 500):
    """Fetch real market data from MT5"""
    print(f"\n📊 Fetching real market data: {symbol} {bars} bars")
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    
    if rates is None or len(rates) == 0:
        print(f"❌ Failed to fetch data for {symbol}")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"✅ Fetched {len(df)} bars")
    print(f"   Period: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
    print(f"   Close range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    
    return df

def compare_bots_on_real_data(symbol: str = "EURUSDm"):
    """Compare original vs refactored ICTBot on real market data"""
    print("\n" + "="*80)
    print(f"🔬 Comparing Bots on Real Data: {symbol}")
    print("="*80)
    
    # Fetch real data
    df = get_real_market_data(symbol, mt5.TIMEFRAME_M15, 500)
    if df is None:
        return None
    
    # Initialize both bots with identical configs
    print("\n1️⃣ Initializing Original ICTBot...")
    original_config = OriginalConfig(
        symbol=symbol,
        timeframe=mt5.TIMEFRAME_M15,
        risk_percent=1.0,
        lookback_candles=20,
        fvg_min_size=0.0005,
        liquidity_sweep_pips=5.0,
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True,
        move_sl_to_breakeven=False
    )
    original_bot = OriginalICTBot(original_config)
    
    print("\n2️⃣ Initializing Refactored ICTBot...")
    refactored_config = ICTConfig(
        symbol=symbol,
        timeframe=mt5.TIMEFRAME_M15,
        risk_percent=1.0,
        lookback_candles=20,
        fvg_min_size=0.0005,
        liquidity_sweep_pips=5.0,
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True,
        move_sl_to_breakeven=False
    )
    refactored_bot = RefactoredICTBot(refactored_config)
    
    # Calculate indicators on both
    print("\n3️⃣ Running ICT Analysis on Original Bot...")
    original_bot.identify_market_structure(df)
    original_bot.identify_order_blocks(df)
    original_bot.identify_fair_value_gaps(df)
    original_signal = original_bot.generate_signal(df)
    
    print("4️⃣ Running ICT Analysis on Refactored Bot...")
    refactored_bot.calculate_indicators(df)
    refactored_signal = refactored_bot.generate_signal(df)
    
    # Compare results
    results = {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'data_bars': len(df),
        'original': {
            'order_blocks': len(original_bot.order_blocks),
            'fair_value_gaps': len(original_bot.fair_value_gaps),
            'market_structure': original_bot.market_structure.copy(),
            'signal': original_signal
        },
        'refactored': {
            'order_blocks': len(refactored_bot.order_blocks),
            'fair_value_gaps': len(refactored_bot.fair_value_gaps),
            'market_structure': refactored_bot.market_structure.copy(),
            'signal': refactored_signal
        }
    }
    
    print("\n" + "="*80)
    print("📊 COMPARISON RESULTS")
    print("="*80)
    
    print(f"\n🔷 Order Blocks:")
    print(f"   Original:    {results['original']['order_blocks']} blocks")
    print(f"   Refactored:  {results['refactored']['order_blocks']} blocks")
    match = "✅ MATCH" if results['original']['order_blocks'] == results['refactored']['order_blocks'] else "⚠️ DIFFERENT"
    print(f"   Status: {match}")
    
    print(f"\n🔷 Fair Value Gaps:")
    print(f"   Original:    {results['original']['fair_value_gaps']} FVGs")
    print(f"   Refactored:  {results['refactored']['fair_value_gaps']} FVGs")
    match = "✅ MATCH" if results['original']['fair_value_gaps'] == results['refactored']['fair_value_gaps'] else "⚠️ DIFFERENT"
    print(f"   Status: {match}")
    
    print(f"\n🔷 Market Structure:")
    orig_trend = results['original']['market_structure'].get('trend', 'unknown')
    ref_trend = results['refactored']['market_structure'].get('trend', 'unknown')
    print(f"   Original:    {orig_trend}")
    print(f"   Refactored:  {ref_trend}")
    match = "✅ MATCH" if orig_trend == ref_trend else "⚠️ DIFFERENT"
    print(f"   Status: {match}")
    
    print(f"\n🔷 Signal Generation:")
    orig_sig = "None" if original_signal is None else original_signal.get('direction', original_signal.get('type', 'Unknown'))
    ref_sig = "None" if refactored_signal is None else refactored_signal.get('type', refactored_signal.get('direction', 'Unknown'))
    print(f"   Original:    {orig_sig}")
    print(f"   Refactored:  {ref_sig}")
    match = "✅ MATCH" if orig_sig == ref_sig else "⚠️ DIFFERENT"
    print(f"   Status: {match}")
    
    # Show signal details if both generated
    if original_signal and refactored_signal:
        print(f"\n🔷 Signal Details:")
        print(f"\n   Original Signal:")
        for key, value in original_signal.items():
            if key not in ['metadata']:
                print(f"      {key}: {value}")
        
        print(f"\n   Refactored Signal:")
        for key, value in refactored_signal.items():
            if key not in ['metadata']:
                print(f"      {key}: {value}")
    
    return results

def detailed_order_blocks_comparison(symbol: str = "EURUSDm"):
    """Deep dive comparison of order blocks detection"""
    print("\n" + "="*80)
    print("🔍 Detailed Order Blocks Comparison")
    print("="*80)
    
    df = get_real_market_data(symbol, mt5.TIMEFRAME_M15, 500)
    if df is None:
        return
    
    # Original
    original_config = OriginalConfig(symbol=symbol)
    original_bot = OriginalICTBot(original_config)
    original_bot.identify_order_blocks(df)
    
    # Refactored
    refactored_config = ICTConfig(symbol=symbol)
    refactored_bot = RefactoredICTBot(refactored_config)
    refactored_bot.identify_order_blocks(df)
    
    print(f"\n📊 Original Bot Order Blocks: {len(original_bot.order_blocks)}")
    for i, ob in enumerate(original_bot.order_blocks[:5], 1):  # Show first 5
        print(f"   {i}. Type: {ob.direction}, Price: {ob.price_low:.5f}-{ob.price_high:.5f}, Time: {ob.time}")
    
    print(f"\n📊 Refactored Bot Order Blocks: {len(refactored_bot.order_blocks)}")
    for i, ob in enumerate(refactored_bot.order_blocks[:5], 1):  # Show first 5
        print(f"   {i}. Type: {ob.ob_type}, Price: {ob.price:.5f}, Time: {ob.time}")

def detailed_fvg_comparison(symbol: str = "EURUSDm"):
    """Deep dive comparison of FVG detection"""
    print("\n" + "="*80)
    print("🔍 Detailed Fair Value Gaps Comparison")
    print("="*80)
    
    df = get_real_market_data(symbol, mt5.TIMEFRAME_M15, 500)
    if df is None:
        return
    
    # Original
    original_config = OriginalConfig(symbol=symbol)
    original_bot = OriginalICTBot(original_config)
    original_bot.identify_fair_value_gaps(df)
    
    # Refactored
    refactored_config = ICTConfig(symbol=symbol)
    refactored_bot = RefactoredICTBot(refactored_config)
    refactored_bot.identify_fair_value_gaps(df)
    
    print(f"\n📊 Original Bot FVGs: {len(original_bot.fair_value_gaps)}")
    for i, fvg in enumerate(original_bot.fair_value_gaps[:5], 1):  # Show first 5
        print(f"   {i}. Type: {fvg.direction}, Top: {fvg.top:.5f}, Bottom: {fvg.bottom:.5f}")
    
    print(f"\n📊 Refactored Bot FVGs: {len(refactored_bot.fair_value_gaps)}")
    for i, fvg in enumerate(refactored_bot.fair_value_gaps[:5], 1):  # Show first 5
        print(f"   {i}. Type: {fvg.fvg_type}, High: {fvg.high:.5f}, Low: {fvg.low:.5f}")

def save_results(results, filename="ict_real_comparison"):
    """Save comparison results to JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = project_root / "reports" / f"{filename}_{timestamp}.json"
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filepath}")
    return filepath

def main():
    """Run complete validation suite"""
    print("="*80)
    print("🚀 ICTBot Real MT5 Validation Suite")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: MT5 Connection
    if not test_mt5_connection():
        print("\n❌ Cannot proceed without MT5 connection")
        return
    
    # Test 2: Compare on main symbols
    symbols_to_test = ["EURUSDm", "AUDUSDm", "XAUUSDm"]
    all_results = []
    
    for symbol in symbols_to_test:
        print(f"\n{'='*80}")
        print(f"Testing {symbol}")
        print(f"{'='*80}")
        
        try:
            results = compare_bots_on_real_data(symbol)
            if results:
                all_results.append(results)
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    # Test 3: Detailed comparisons on EURUSD
    try:
        detailed_order_blocks_comparison("EURUSDm")
        detailed_fvg_comparison("EURUSDm")
    except Exception as e:
        print(f"❌ Error in detailed comparison: {e}")
        import traceback
        traceback.print_exc()
    
    # Save all results
    if all_results:
        save_results(all_results)
    
    # Summary
    print("\n" + "="*80)
    print("✅ VALIDATION COMPLETE")
    print("="*80)
    print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Tested {len(all_results)} symbols")
    print("\n💡 Next Steps:")
    print("   1. Review comparison results")
    print("   2. Investigate any differences")
    print("   3. If all looks good, replace original with refactored version")
    
    # Cleanup
    mt5.shutdown()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        mt5.shutdown()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
