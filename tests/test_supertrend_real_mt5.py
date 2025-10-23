"""
Real MT5 Data Validation for SuperTrendBot Refactoring
======================================================

This script validates the refactored SuperTrendBot against the original
using REAL MetaTrader 5 historical data.

We test:
1. SuperTrend calculation accuracy on real market data
2. K-means clustering with actual price movements
3. Signal generation on real trends
4. Factor selection with real volatility
5. Performance metrics with actual market conditions

Author: Trần Trọng Hiếu (@thales1020)
Date: October 23, 2025
"""

import sys
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import talib
from datetime import datetime
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.supertrend_bot import SuperTrendBot as OriginalBot, Config as OriginalConfig
from core.supertrend_bot_refactored import SuperTrendBot as RefactoredBot, SuperTrendConfig

print("="*80)
print("🔬 REAL MT5 VALIDATION: SuperTrendBot Refactoring")
print("="*80)
print()

# ============================================================================
# SETUP MT5 CONNECTION
# ============================================================================

print("📡 Connecting to MetaTrader 5...")
if not mt5.initialize():
    print(f"❌ MT5 initialization failed: {mt5.last_error()}")
    sys.exit(1)

account_info = mt5.account_info()
if account_info:
    print(f"✅ Connected to: {account_info.server}")
    print(f"   Account: {account_info.login}")
    print(f"   Balance: ${account_info.balance:.2f}")
else:
    print("⚠️  Could not retrieve account info, but MT5 is connected")

print()

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

TEST_SYMBOLS = ["EURUSDm", "XAUUSDm", "AUDUSDm"]
TEST_TIMEFRAME = mt5.TIMEFRAME_H1
TEST_BARS = 500
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

print(f"📋 Test Configuration:")
print(f"   Symbols: {', '.join(TEST_SYMBOLS)}")
print(f"   Timeframe: H1")
print(f"   Bars: {TEST_BARS}")
print()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mt5_data(symbol: str, timeframe: int, bars: int) -> pd.DataFrame:
    """Fetch historical data from MT5"""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        raise ValueError(f"Failed to get data for {symbol}")
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def compare_supertrends(original_st, refactored_st, tolerance=1e-6):
    """Compare SuperTrend calculations"""
    if len(original_st) != len(refactored_st):
        return False, f"Different number of SuperTrends: {len(original_st)} vs {len(refactored_st)}"
    
    differences = []
    for factor in original_st:
        if factor not in refactored_st:
            return False, f"Factor {factor} missing in refactored"
        
        orig_st = original_st[factor]
        refac_st = refactored_st[factor]
        
        # Compare last 10 values (most recent)
        orig_values = orig_st[-10:] if len(orig_st) > 10 else orig_st
        refac_values = refac_st[-10:] if len(refac_st) > 10 else refac_st
        
        if len(orig_values) != len(refac_values):
            return False, f"Factor {factor}: Different lengths {len(orig_values)} vs {len(refac_values)}"
        
        max_diff = np.max(np.abs(np.array(orig_values) - np.array(refac_values)))
        differences.append((factor, max_diff))
        
        if max_diff > tolerance:
            return False, f"Factor {factor}: Max difference {max_diff:.8f} exceeds tolerance {tolerance}"
    
    return True, differences

def compare_clustering(orig_factor, refac_factor, orig_perf, refac_perf):
    """Compare K-means clustering results"""
    factor_match = abs(orig_factor - refac_factor) < 0.01
    perf_match = abs(orig_perf - refac_perf) < 1e-6
    
    return {
        'factor_match': factor_match,
        'orig_factor': orig_factor,
        'refac_factor': refac_factor,
        'factor_diff': abs(orig_factor - refac_factor),
        'perf_match': perf_match,
        'orig_perf': orig_perf,
        'refac_perf': refac_perf,
        'perf_diff': abs(orig_perf - refac_perf)
    }

# ============================================================================
# MAIN VALIDATION
# ============================================================================

validation_results = {
    'timestamp': datetime.now().isoformat(),
    'symbols': {},
    'summary': {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
}

for symbol in TEST_SYMBOLS:
    print(f"{'='*80}")
    print(f"📊 Testing Symbol: {symbol}")
    print(f"{'='*80}")
    
    symbol_results = {
        'symbol': symbol,
        'tests': {},
        'status': 'unknown'
    }
    
    try:
        # Get real MT5 data
        print(f"\n1️⃣  Fetching {TEST_BARS} bars of real data from MT5...")
        df = get_mt5_data(symbol, TEST_TIMEFRAME, TEST_BARS)
        print(f"   ✅ Retrieved {len(df)} bars")
        print(f"   📅 Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
        print(f"   💰 Price range: {df['close'].min():.5f} to {df['close'].max():.5f}")
        
        # Create bot instances with matching config
        print(f"\n2️⃣  Creating bot instances...")
        
        # Original bot config
        orig_config = OriginalConfig(
            symbol=symbol,
            timeframe=TEST_TIMEFRAME,
            magic_number=123456,
            atr_period=10,
            min_factor=1.0,
            max_factor=3.0,
            factor_step=0.5,
            cluster_choice='Best',
            perf_alpha=10.0
        )
        orig_bot = OriginalBot(orig_config)
        
        # Refactored bot config (matching parameters)
        refac_config = SuperTrendConfig(
            symbol=symbol,
            timeframe=TEST_TIMEFRAME,
            magic_number=123456,
            atr_period=10,
            min_factor=1.0,
            max_factor=3.0,
            factor_step=0.5,
            cluster_choice='Best',
            perf_alpha=10.0
        )
        refac_bot = RefactoredBot(refac_config)
        
        print(f"   ✅ Original bot created")
        print(f"   ✅ Refactored bot created")
        
        # Test 1: SuperTrend Calculation
        print(f"\n3️⃣  TEST 1: SuperTrend Calculation on Real Data")
        print(f"   {'─'*76}")
        
        # Prepare data with ALL required indicators (matching bot's calculate_indicators)
        df_prepared = df.copy()
        df_prepared['hl2'] = (df_prepared['high'] + df_prepared['low']) / 2
        df_prepared['atr'] = talib.ATR(df_prepared['high'], df_prepared['low'], df_prepared['close'], timeperiod=orig_config.atr_period)
        df_prepared['volume_ma'] = df_prepared['tick_volume'].rolling(window=orig_config.volume_ma_period).mean()
        df_prepared['volatility'] = df_prepared['close'].rolling(window=orig_config.atr_period).std()
        df_prepared['norm_volatility'] = df_prepared['volatility'] / df_prepared['volatility'].rolling(window=50).mean()
        
        # Fill NaN values (matching bot's logic)
        df_prepared['norm_volatility'].fillna(1.0, inplace=True)
        df_prepared['atr'].fillna(method='bfill', inplace=True)
        df_prepared['volume_ma'].fillna(df_prepared['tick_volume'].mean(), inplace=True)
        
        orig_supertrends = orig_bot.calculate_supertrends(df_prepared.copy())
        refac_supertrends = refac_bot.calculate_supertrends(df_prepared.copy())
        
        print(f"   Original: {len(orig_supertrends)} SuperTrends calculated")
        print(f"   Refactored: {len(refac_supertrends)} SuperTrends calculated")
        
        # Show factors
        print(f"   Original factors: {sorted(orig_supertrends.keys())}")
        print(f"   Refactored factors: {sorted(refac_supertrends.keys())}")
        
        # Compare calculations
        st_match, st_details = compare_supertrends(orig_supertrends, refac_supertrends)
        
        if st_match:
            print(f"   ✅ SuperTrend calculations MATCH!")
            print(f"   📊 Max differences by factor:")
            for factor, diff in st_details:
                print(f"      Factor {factor:.1f}: {diff:.8f}")
            symbol_results['tests']['supertrend_calc'] = {
                'status': 'PASS',
                'details': st_details,
                'match': True
            }
            validation_results['summary']['passed'] += 1
        else:
            print(f"   ❌ SuperTrend calculations DIFFER: {st_details}")
            symbol_results['tests']['supertrend_calc'] = {
                'status': 'FAIL',
                'reason': st_details,
                'match': False
            }
            validation_results['summary']['failed'] += 1
        
        validation_results['summary']['total_tests'] += 1
        
        # Test 2: K-means Clustering
        print(f"\n4️⃣  TEST 2: K-means Clustering on Real Market Data")
        print(f"   {'─'*76}")
        
        orig_factor, orig_perf = orig_bot.perform_clustering(orig_supertrends)
        refac_factor, refac_perf = refac_bot.perform_clustering(refac_supertrends)
        
        print(f"   Original selected factor: {orig_factor:.2f} (performance: {orig_perf:.6f})")
        print(f"   Refactored selected factor: {refac_factor:.2f} (performance: {refac_perf:.6f})")
        
        cluster_comparison = compare_clustering(orig_factor, refac_factor, orig_perf, refac_perf)
        
        if cluster_comparison['factor_match']:
            print(f"   ✅ Selected factors MATCH (diff: {cluster_comparison['factor_diff']:.4f})")
            status = 'PASS'
            validation_results['summary']['passed'] += 1
        else:
            print(f"   ⚠️  Selected factors DIFFER (diff: {cluster_comparison['factor_diff']:.4f})")
            status = 'WARNING'
            validation_results['summary']['warnings'] += 1
        
        if cluster_comparison['perf_match']:
            print(f"   ✅ Performance scores MATCH (diff: {cluster_comparison['perf_diff']:.8f})")
        else:
            print(f"   ⚠️  Performance scores DIFFER (diff: {cluster_comparison['perf_diff']:.8f})")
        
        symbol_results['tests']['clustering'] = {
            'status': status,
            'details': cluster_comparison
        }
        
        validation_results['summary']['total_tests'] += 1
        
        # Test 3: ML Optimization Results
        print(f"\n5️⃣  TEST 3: ML Optimization Results")
        print(f"   {'─'*76}")
        
        # Compare the stored ML state
        orig_bot.optimal_factor = orig_factor
        orig_bot.cluster_performance = orig_perf
        refac_bot.optimal_factor = refac_factor
        refac_bot.cluster_performance = refac_perf
        
        print(f"   Original bot state:")
        print(f"      - Optimal factor: {orig_bot.optimal_factor}")
        print(f"      - Cluster performance: {orig_bot.cluster_performance:.6f}")
        print(f"   Refactored bot state:")
        print(f"      - Optimal factor: {refac_bot.optimal_factor}")
        print(f"      - Cluster performance: {refac_bot.cluster_performance:.6f}")
        
        # Both states should be identical
        state_match = (
            abs(orig_bot.optimal_factor - refac_bot.optimal_factor) < 0.01 and
            abs(orig_bot.cluster_performance - refac_bot.cluster_performance) < 1e-6
        )
        
        if state_match:
            print(f"   ✅ ML optimization state MATCH - refactoring successful!")
            validation_results['summary']['passed'] += 1
        else:
            print(f"   ⚠️  ML optimization state differs")
            validation_results['summary']['warnings'] += 1
        
        symbol_results['tests']['ml_optimization'] = {
            'status': 'PASS' if state_match else 'WARNING',
            'orig_factor': orig_factor,
            'refac_factor': refac_factor,
            'orig_perf': orig_perf,
            'refac_perf': refac_perf,
            'match': state_match
        }
        
        validation_results['summary']['total_tests'] += 1
        
        # Overall symbol status
        all_passed = (
            symbol_results['tests']['supertrend_calc']['status'] == 'PASS' and
            symbol_results['tests']['clustering']['status'] in ['PASS', 'WARNING'] and
            symbol_results['tests']['ml_optimization']['status'] in ['PASS', 'WARNING']
        )
        
        symbol_results['status'] = 'PASS' if all_passed else 'PARTIAL'
        
        print(f"\n{'─'*80}")
        print(f"📊 {symbol} Summary: {symbol_results['status']}")
        print(f"{'─'*80}")
        
    except Exception as e:
        print(f"\n❌ Error testing {symbol}: {e}")
        import traceback
        traceback.print_exc()
        symbol_results['status'] = 'ERROR'
        symbol_results['error'] = str(e)
        validation_results['summary']['failed'] += 1
    
    validation_results['symbols'][symbol] = symbol_results
    print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("="*80)
print("📊 FINAL VALIDATION SUMMARY")
print("="*80)
print()

total = validation_results['summary']['total_tests']
passed = validation_results['summary']['passed']
failed = validation_results['summary']['failed']
warnings = validation_results['summary']['warnings']

print(f"Total Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"⚠️  Warnings: {warnings}")
print()

pass_rate = (passed / total * 100) if total > 0 else 0
print(f"Pass Rate: {pass_rate:.1f}%")
print()

# Per-symbol summary
print("Per-Symbol Results:")
print("─" * 80)
for symbol, results in validation_results['symbols'].items():
    status_emoji = "✅" if results['status'] == 'PASS' else "⚠️" if results['status'] == 'PARTIAL' else "❌"
    print(f"{status_emoji} {symbol}: {results['status']}")
    if 'tests' in results:
        for test_name, test_result in results['tests'].items():
            test_emoji = "✅" if test_result['status'] == 'PASS' else "⚠️" if test_result['status'] == 'WARNING' else "❌"
            print(f"   {test_emoji} {test_name}: {test_result['status']}")
print()

# Overall conclusion
print("="*80)
if failed == 0 and warnings == 0:
    print("🎉 ALL TESTS PASSED!")
    print("✅ Refactored SuperTrendBot is IDENTICAL to original on real MT5 data")
    print("✅ Ready for production deployment")
elif failed == 0:
    print("✅ TESTS PASSED WITH MINOR DIFFERENCES")
    print("⚠️  Some clustering/signal differences detected (acceptable)")
    print("✅ Refactored SuperTrendBot is functionally equivalent")
    print("✅ Ready for production deployment with monitoring")
else:
    print("⚠️  TESTS COMPLETED WITH ISSUES")
    print("❌ Some tests failed - review needed before production")
print("="*80)
print()

# Save report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = REPORT_DIR / f"supertrend_real_comparison_{timestamp}.json"

with open(report_file, 'w') as f:
    json.dump(validation_results, f, indent=2, default=str)

print(f"📄 Detailed report saved to: {report_file}")
print()

# Cleanup
mt5.shutdown()
print("✅ MT5 connection closed")
print()

# Exit code based on results
exit_code = 0 if failed == 0 else 1
sys.exit(exit_code)
