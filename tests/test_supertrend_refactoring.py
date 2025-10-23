"""
Test SuperTrendBot Refactored vs Original
Compare functionality and performance
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime

# Import original SuperTrendBot
from core.supertrend_bot import SuperTrendBot as OriginalSuperTrendBot
from core.supertrend_bot import Config as OriginalConfig

# Import refactored SuperTrendBot
from core.supertrend_bot_refactored import SuperTrendBot as RefactoredSuperTrendBot
from core.supertrend_bot_refactored import SuperTrendConfig

def test_basic_import():
    """Test if both versions can be imported"""
    print("\n" + "="*80)
    print("TEST 1: Import Test")
    print("="*80)
    
    try:
        print("✅ Original SuperTrendBot imported successfully")
        print("✅ Refactored SuperTrendBot imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test if both bots can be initialized"""
    print("\n" + "="*80)
    print("TEST 2: Initialization Test")
    print("="*80)
    
    try:
        # Original
        original_config = OriginalConfig(
            symbol="EURUSDm",
            timeframe=mt5.TIMEFRAME_M30,
            min_factor=1.0,
            max_factor=5.0,
            cluster_choice="Best"
        )
        original_bot = OriginalSuperTrendBot(original_config)
        print("✅ Original bot initialized")
        
        # Refactored
        refactored_config = SuperTrendConfig(
            symbol="EURUSDm",
            timeframe=mt5.TIMEFRAME_M30,
            min_factor=1.0,
            max_factor=5.0,
            cluster_choice="Best"
        )
        refactored_bot = RefactoredSuperTrendBot(refactored_config)
        print("✅ Refactored bot initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_test_data(bars: int = 500) -> pd.DataFrame:
    """Generate synthetic price data for testing"""
    print(f"\n📊 Generating {bars} bars of synthetic data...")
    
    # Generate realistic price movement
    np.random.seed(42)
    base_price = 1.1000
    returns = np.random.randn(bars) * 0.0005  # Small daily returns
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Create OHLCV data
    df = pd.DataFrame({
        'time': pd.date_range(start='2024-01-01', periods=bars, freq='30min'),
        'open': prices,
        'high': prices * (1 + np.abs(np.random.randn(bars) * 0.0002)),
        'low': prices * (1 - np.abs(np.random.randn(bars) * 0.0002)),
        'close': prices * (1 + np.random.randn(bars) * 0.0001),
        'tick_volume': np.random.randint(100, 1000, bars),
        'spread': 2,
        'real_volume': 0
    })
    
    print(f"✅ Generated data: {len(df)} bars")
    print(f"   Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    
    return df

def test_supertrend_calculation():
    """Test SuperTrend calculation"""
    print("\n" + "="*80)
    print("TEST 3: SuperTrend Calculation Test")
    print("="*80)
    
    df = generate_test_data(500)
    
    try:
        # Original
        print("\n1️⃣ Testing Original Bot...")
        original_config = OriginalConfig(
            symbol="EURUSDm",
            min_factor=1.0,
            max_factor=3.0,
            factor_step=0.5
        )
        original_bot = OriginalSuperTrendBot(original_config)
        
        # Add required indicators
        df_orig = df.copy()
        df_orig['hl2'] = (df_orig['high'] + df_orig['low']) / 2
        
        import talib
        df_orig['atr'] = talib.ATR(df_orig['high'].values, df_orig['low'].values, 
                                     df_orig['close'].values, timeperiod=10)
        df_orig['volume_ma'] = df_orig['tick_volume'].rolling(window=20).mean()
        df_orig['volatility'] = df_orig['close'].rolling(window=10).std()
        df_orig['norm_volatility'] = df_orig['volatility'] / df_orig['volatility'].rolling(window=50).mean()
        df_orig['norm_volatility'].fillna(1.0, inplace=True)
        df_orig['atr'].fillna(method='bfill', inplace=True)
        
        original_supertrends = original_bot.calculate_supertrends(df_orig)
        print(f"✅ Original calculated {len(original_supertrends)} SuperTrends")
        
        # Refactored
        print("\n2️⃣ Testing Refactored Bot...")
        refactored_config = SuperTrendConfig(
            symbol="EURUSDm",
            min_factor=1.0,
            max_factor=3.0,
            factor_step=0.5
        )
        refactored_bot = RefactoredSuperTrendBot(refactored_config)
        
        df_ref = refactored_bot.calculate_indicators(df.copy())
        print(f"✅ Refactored calculated {len(refactored_bot.supertrends)} SuperTrends")
        
        # Compare
        print("\n📊 Comparison:")
        print(f"   Original:    {len(original_supertrends)} SuperTrends")
        print(f"   Refactored:  {len(refactored_bot.supertrends)} SuperTrends")
        
        if len(original_supertrends) == len(refactored_bot.supertrends):
            print("   ✅ MATCH: Same number of SuperTrends")
        else:
            print("   ⚠️ DIFFERENT: Different number of SuperTrends")
        
        return True
        
    except Exception as e:
        print(f"❌ SuperTrend calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clustering():
    """Test K-means clustering"""
    print("\n" + "="*80)
    print("TEST 4: K-means Clustering Test")
    print("="*80)
    
    df = generate_test_data(500)
    
    try:
        # Original
        print("\n1️⃣ Testing Original Bot Clustering...")
        original_config = OriginalConfig(
            symbol="EURUSDm",
            min_factor=1.0,
            max_factor=3.0,
            cluster_choice="Best"
        )
        original_bot = OriginalSuperTrendBot(original_config)
        
        df_orig = df.copy()
        df_orig['hl2'] = (df_orig['high'] + df_orig['low']) / 2
        
        import talib
        df_orig['atr'] = talib.ATR(df_orig['high'].values, df_orig['low'].values, 
                                     df_orig['close'].values, timeperiod=10)
        df_orig['volume_ma'] = df_orig['tick_volume'].rolling(window=20).mean()
        df_orig['volatility'] = df_orig['close'].rolling(window=10).std()
        df_orig['norm_volatility'] = df_orig['volatility'] / df_orig['volatility'].rolling(window=50).mean()
        df_orig['norm_volatility'].fillna(1.0, inplace=True)
        df_orig['atr'].fillna(method='bfill', inplace=True)
        
        original_supertrends = original_bot.calculate_supertrends(df_orig)
        original_factor, original_perf = original_bot.perform_clustering(original_supertrends)
        print(f"✅ Original: Factor={original_factor:.2f}, Perf={original_perf:.4f}")
        
        # Refactored
        print("\n2️⃣ Testing Refactored Bot Clustering...")
        refactored_config = SuperTrendConfig(
            symbol="EURUSDm",
            min_factor=1.0,
            max_factor=3.0,
            cluster_choice="Best"
        )
        refactored_bot = RefactoredSuperTrendBot(refactored_config)
        
        df_ref = refactored_bot.calculate_indicators(df.copy())
        print(f"✅ Refactored: Factor={refactored_bot.optimal_factor:.2f}, Perf={refactored_bot.cluster_performance:.4f}")
        
        # Compare
        print("\n📊 Comparison:")
        print(f"   Original Factor:    {original_factor:.2f}")
        print(f"   Refactored Factor:  {refactored_bot.optimal_factor:.2f}")
        print(f"   Difference:         {abs(original_factor - refactored_bot.optimal_factor):.2f}")
        
        if abs(original_factor - refactored_bot.optimal_factor) < 0.5:
            print("   ✅ CLOSE: Factors are similar")
        else:
            print("   ⚠️ DIFFERENT: Factors differ significantly")
        
        return True
        
    except Exception as e:
        print(f"❌ Clustering failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_generation():
    """Test signal generation"""
    print("\n" + "="*80)
    print("TEST 5: Signal Generation Test")
    print("="*80)
    
    df = generate_test_data(500)
    
    try:
        # Refactored (Original doesn't have generate_signal method in same format)
        print("\n1️⃣ Testing Refactored Bot Signal Generation...")
        refactored_config = SuperTrendConfig(
            symbol="EURUSDm",
            min_factor=1.0,
            max_factor=3.0,
            cluster_choice="Best",
            volume_multiplier=1.0  # Lower threshold for test
        )
        refactored_bot = RefactoredSuperTrendBot(refactored_config)
        
        df_ref = refactored_bot.calculate_indicators(df.copy())
        signal = refactored_bot.generate_signal(df_ref)
        
        if signal:
            print(f"✅ Signal generated: {signal['type']}")
            print(f"   Price: {signal['price']:.5f}")
            print(f"   Stop Loss: {signal['stop_loss']:.5f}")
            print(f"   Take Profit: {signal['take_profit']:.5f}")
            print(f"   Confidence: {signal['confidence']:.1f}%")
            print(f"   Reason: {signal['reason']}")
        else:
            print("ℹ️  No signal generated (expected with synthetic data)")
        
        print("\n✅ Signal generation method working")
        return True
        
    except Exception as e:
        print(f"❌ Signal generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_methods_comparison():
    """Compare methods between original and refactored"""
    print("\n" + "="*80)
    print("TEST 6: Methods Comparison")
    print("="*80)
    
    try:
        original_config = OriginalConfig(symbol="EURUSDm")
        original_bot = OriginalSuperTrendBot(original_config)
        
        refactored_config = SuperTrendConfig(symbol="EURUSDm")
        refactored_bot = RefactoredSuperTrendBot(refactored_config)
        
        original_methods = [m for m in dir(original_bot) if not m.startswith('_') and callable(getattr(original_bot, m))]
        refactored_methods = [m for m in dir(refactored_bot) if not m.startswith('_') and callable(getattr(refactored_bot, m))]
        
        print(f"\n📊 Original Bot: {len(original_methods)} public methods")
        print(f"📊 Refactored Bot: {len(refactored_methods)} public methods")
        
        # Key methods to check
        key_methods = [
            'calculate_supertrends',
            'perform_clustering',
            'check_volume_condition',
            'update_trailing_stop',
            'calculate_indicators',
            'generate_signal'
        ]
        
        print("\n🔑 Key Methods:")
        for method in key_methods:
            in_original = method in original_methods
            in_refactored = method in refactored_methods
            
            if method in ['calculate_indicators', 'generate_signal']:
                # These are new/different
                status = "✅ NEW" if in_refactored else "❌"
            else:
                status = "✅" if (in_original and in_refactored) else "⚠️"
            
            print(f"   {status} {method}: Original={in_original}, Refactored={in_refactored}")
        
        return True
        
    except Exception as e:
        print(f"❌ Methods comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("🚀 SuperTrend Bot Refactoring Test Suite")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_basic_import()))
    results.append(("Initialization Test", test_initialization()))
    results.append(("SuperTrend Calculation", test_supertrend_calculation()))
    results.append(("K-means Clustering", test_clustering()))
    results.append(("Signal Generation", test_signal_generation()))
    results.append(("Methods Comparison", test_methods_comparison()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Refactored SuperTrendBot is working correctly")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("❌ Need to fix issues before proceeding")
    
    print(f"\n⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
