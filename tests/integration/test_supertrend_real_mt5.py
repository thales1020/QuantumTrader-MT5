"""
Test SuperTrendBot with Real MT5 Connection
Test SuperTrend strategy on actual market data
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

# Import SuperTrendBot
from core.supertrend_bot import SuperTrendBot, SuperTrendConfig

def test_mt5_connection():
    """Test if MT5 is available and connected"""
    print("\n" + "="*80)
    print("Testing MT5 Connection")
    print("="*80)
    
    if not mt5.initialize():
        print(" MT5 not initialized. Please ensure:")
        print("   1. MetaTrader 5 is installed")
        print("   2. MT5 terminal is running")
        print("   3. You're logged into a demo/live account")
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        print(" Not logged into MT5 account")
        mt5.shutdown()
        return False
    
    print(f" MT5 Connected Successfully")
    print(f"   Account: {account_info.login}")
    print(f"   Server: {account_info.server}")
    print(f"   Balance: ${account_info.balance:.2f}")
    print(f"   Equity: ${account_info.equity:.2f}")
    
    return True

def get_real_market_data(symbol: str, timeframe, bars: int = 500):
    """Fetch real market data from MT5"""
    print(f"\nFetching {bars} bars of {symbol} data...")
    
    # Enable symbol if not visible
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"  Symbol {symbol} not found!")
        return None
    
    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            print(f"  Failed to enable symbol {symbol}")
            return None
    
    # Get data
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    
    if rates is None or len(rates) == 0:
        print(f"  Failed to get market data for {symbol}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    print(f"  Retrieved {len(df)} bars")
    print(f"  From: {df['time'].iloc[0]}")
    print(f"  To: {df['time'].iloc[-1]}")
    
    return df

def test_supertrend_bot_on_real_data(symbol: str = "AUDUSDm"):
    """Test SuperTrendBot on real market data"""
    print("\n" + "="*80)
    print(f"Testing SuperTrendBot on {symbol}")
    print("="*80)
    
    df = get_real_market_data(symbol, mt5.TIMEFRAME_H1, 500)
    if df is None:
        return None
    
    # Initialize SuperTrend Bot
    print("\nInitializing SuperTrend Bot...")
    config = SuperTrendConfig(
        symbol=symbol,
        timeframe=mt5.TIMEFRAME_H1,
        risk_percent=1.0,
        atr_period=10,
        min_factor=1.0,
        max_factor=5.0,
        factor_step=0.5,
        volume_ma_period=20,
        volume_multiplier=1.2,
        use_trailing=True,
        move_sl_to_breakeven=True
    )
    bot = SuperTrendBot(config)
    
    # Calculate indicators
    print("\nRunning SuperTrend Analysis...")
    df_with_indicators = bot.calculate_indicators(df)
    signal = bot.generate_signal(df_with_indicators)
    
    # Get results
    results = {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'data_bars': len(df),
        'has_supertrend': 'supertrend' in df_with_indicators.columns,
        'has_atr': 'atr' in df_with_indicators.columns,
        'current_trend': df_with_indicators['supertrend'].iloc[-1] if 'supertrend' in df_with_indicators.columns else None,
        'current_price': df_with_indicators['close'].iloc[-1],
        'signal': signal
    }
    
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\nData:")
    print(f"   Bars analyzed: {results['data_bars']}")
    print(f"   Current price: {results['current_price']:.5f}")
    
    print(f"\nIndicators:")
    print(f"   SuperTrend calculated: {results['has_supertrend']}")
    print(f"   ATR calculated: {results['has_atr']}")
    if results['current_trend'] is not None:
        trend_direction = "BULLISH" if results['current_trend'] > 0 else "BEARISH"
        print(f"   Current trend: {trend_direction}")
    
    print(f"\nSignal:")
    if signal:
        sig_type = signal.get('type', 'Unknown')
        print(f"   Type: {sig_type}")
        print(f"   Entry: {signal.get('price', 0):.5f}")
        print(f"   SL: {signal.get('stop_loss', 0):.5f}")
        print(f"   TP: {signal.get('take_profit', 0):.5f}")
        if 'confidence' in signal:
            print(f"   Confidence: {signal.get('confidence', 0):.1f}%")
    else:
        print(f"   No signal generated")
    
    return results

def save_results(results, filename="supertrend_real_test"):
    """Save test results to JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    filepath = reports_dir / f"{filename}_{timestamp}.json"
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {filepath}")
    return filepath

def main():
    """Run complete test suite"""
    print("="*80)
    print("SuperTrendBot Real MT5 Test Suite")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: MT5 Connection
    if not test_mt5_connection():
        print("\nCannot proceed without MT5 connection")
        return
    
    # Test 2: Test on main symbols
    symbols_to_test = ["AUDUSDm", "EURUSDm", "XAUUSDm"]
    all_results = []
    
    for symbol in symbols_to_test:
        print(f"\n{'='*80}")
        print(f"Testing {symbol}")
        print(f"{'='*80}")
        
        try:
            results = test_supertrend_bot_on_real_data(symbol)
            if results:
                all_results.append(results)
        except Exception as e:
            print(f"\nError testing {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save combined results
    if all_results:
        combined_results = {
            'test_date': datetime.now().isoformat(),
            'symbols_tested': len(all_results),
            'results': all_results
        }
        save_results(combined_results, "supertrend_multi_symbol_test")
    
    # Cleanup
    mt5.shutdown()
    
    print("\n" + "="*80)
    print("Test Suite Complete")
    print("="*80)

if __name__ == "__main__":
    main()
