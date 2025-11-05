"""
Memory Leak Test for Backtest System
======================================

Test memory usage during long backtest to detect leaks

Author: QuantumTrader Team
"""

import psutil
import os
import gc
from datetime import datetime
import MetaTrader5 as mt5

from engines.base_backtest_engine import BaseBacktestEngine
from engines.broker_simulator import BrokerConfig
from examples.working_backtest import SimpleSMAStrategy


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB


def test_memory_leak():
    """Test for memory leaks during backtest"""
    
    print("="*70)
    print("MEMORY LEAK TEST")
    print("="*70)
    
    # Initial memory
    gc.collect()
    initial_memory = get_memory_usage()
    print(f"\n📊 Initial Memory: {initial_memory:.2f} MB")
    
    # Initialize MT5
    if not mt5.initialize():
        raise Exception("MT5 init failed")
    
    # Create strategy and broker once
    strategy = SimpleSMAStrategy(fast=10, slow=30)
    broker = BrokerConfig(
        spread_pips=1.5,
        commission_per_lot=7.0,
        swap_long=-5.0,
        swap_short=-5.0
    )
    
    memory_checkpoints = []
    
    # Run backtest multiple times on different periods
    test_periods = [
        ('2025-01-01', '2025-03-31', 'Q1 2025'),
        ('2025-04-01', '2025-06-30', 'Q2 2025'),
        ('2025-07-01', '2025-09-30', 'Q3 2025'),
        ('2025-10-01', '2025-11-05', 'Q4 2025'),
    ]
    
    print("\n🔄 Running multiple backtests to check memory...")
    
    for idx, (start, end, label) in enumerate(test_periods, 1):
        print(f"\n--- Test {idx}/4: {label} ---")
        
        # Memory before
        gc.collect()
        mem_before = get_memory_usage()
        
        # Run backtest
        engine = BaseBacktestEngine(
            strategy=strategy,
            broker_config=broker,
            initial_balance=10000
        )
        
        metrics = engine.run_backtest(
            symbol='EURUSDm',
            start_date=datetime.fromisoformat(start),
            end_date=datetime.fromisoformat(end),
            timeframe=mt5.TIMEFRAME_H1,
            export_excel=False  # Don't export to save time
        )
        
        # Memory after
        gc.collect()
        mem_after = get_memory_usage()
        mem_diff = mem_after - mem_before
        
        memory_checkpoints.append({
            'test': label,
            'before': mem_before,
            'after': mem_after,
            'diff': mem_diff,
            'trades': metrics.total_trades
        })
        
        print(f"   Memory Before:  {mem_before:.2f} MB")
        print(f"   Memory After:   {mem_after:.2f} MB")
        print(f"   Difference:     {mem_diff:+.2f} MB")
        print(f"   Trades:         {metrics.total_trades}")
        
        # Delete engine to free memory
        del engine
        del metrics
        gc.collect()
    
    mt5.shutdown()
    
    # Final memory check
    gc.collect()
    final_memory = get_memory_usage()
    total_growth = final_memory - initial_memory
    
    # Analysis
    print("\n" + "="*70)
    print("MEMORY ANALYSIS")
    print("="*70)
    
    print(f"\n📊 Memory Summary:")
    print(f"   Initial:        {initial_memory:.2f} MB")
    print(f"   Final:          {final_memory:.2f} MB")
    print(f"   Total Growth:   {total_growth:+.2f} MB")
    
    # Check for leak pattern
    print(f"\n📈 Per-Test Growth:")
    for cp in memory_checkpoints:
        print(f"   {cp['test']:12} {cp['diff']:+7.2f} MB  ({cp['trades']} trades)")
    
    avg_growth = sum(cp['diff'] for cp in memory_checkpoints) / len(memory_checkpoints)
    
    # Verdict
    print(f"\n🔍 Analysis:")
    print(f"   Average Growth per Test: {avg_growth:+.2f} MB")
    
    # Memory leak indicators
    leak_detected = False
    warnings = []
    
    if total_growth > 100:
        warnings.append(f"⚠️  Large total growth: {total_growth:.2f} MB")
        leak_detected = True
    
    if avg_growth > 20:
        warnings.append(f"⚠️  High average growth: {avg_growth:.2f} MB/test")
        leak_detected = True
    
    # Check if memory keeps growing
    growths = [cp['diff'] for cp in memory_checkpoints]
    if all(g > 5 for g in growths):
        warnings.append("⚠️  Memory grows on every test")
        leak_detected = True
    
    if leak_detected:
        print("\n❌ POTENTIAL MEMORY LEAK DETECTED!")
        for warning in warnings:
            print(f"   {warning}")
        print("\n💡 Recommendations:")
        print("   1. Check if DataFrames are being accumulated")
        print("   2. Ensure positions/trades are cleared between runs")
        print("   3. Verify logging handlers are not duplicated")
        print("   4. Check for circular references")
    else:
        print("\n✅ NO SIGNIFICANT MEMORY LEAK DETECTED")
        print("   Memory growth is within acceptable range for:")
        print("   - Caching of compiled code")
        print("   - Pandas/NumPy internal buffers")
        print("   - Python interpreter overhead")
    
    # Memory efficiency
    total_trades = sum(cp['trades'] for cp in memory_checkpoints)
    if total_trades > 0:
        mb_per_trade = total_growth / total_trades
        print(f"\n📊 Memory Efficiency:")
        print(f"   Total Trades Executed: {total_trades}")
        print(f"   Memory per Trade: {mb_per_trade*1024:.2f} KB")
        
        if mb_per_trade > 0.1:  # >100KB per trade
            print("   ⚠️  High memory per trade - consider optimization")
        else:
            print("   ✅ Good memory efficiency")
    
    return not leak_detected


def test_single_large_backtest():
    """Test memory during single large backtest"""
    
    print("\n" + "="*70)
    print("LARGE BACKTEST MEMORY TEST (2020-2025)")
    print("="*70)
    
    gc.collect()
    initial = get_memory_usage()
    print(f"\n📊 Initial Memory: {initial:.2f} MB")
    
    if not mt5.initialize():
        raise Exception("MT5 init failed")
    
    strategy = SimpleSMAStrategy(fast=10, slow=30)
    broker = BrokerConfig(spread_pips=1.5, commission_per_lot=7.0)
    
    print("\n🔄 Running backtest on 5 years of data...")
    
    engine = BaseBacktestEngine(
        strategy=strategy,
        broker_config=broker,
        initial_balance=10000
    )
    
    # Track memory during execution
    print("\n📊 Memory checkpoints during execution:")
    
    metrics = engine.run_backtest(
        symbol='EURUSDm',
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2025, 11, 5),
        timeframe=mt5.TIMEFRAME_H1,
        export_excel=False
    )
    
    gc.collect()
    final = get_memory_usage()
    growth = final - initial
    
    print(f"\n📊 Memory Summary:")
    print(f"   Initial:  {initial:.2f} MB")
    print(f"   Final:    {final:.2f} MB")
    print(f"   Growth:   {growth:+.2f} MB")
    print(f"   Trades:   {metrics.total_trades}")
    
    if metrics.total_trades > 0:
        kb_per_trade = (growth * 1024) / metrics.total_trades
        print(f"   Per Trade: {kb_per_trade:.2f} KB")
    
    del engine
    del metrics
    gc.collect()
    
    cleanup_mem = get_memory_usage()
    recovered = final - cleanup_mem
    
    print(f"\n🧹 After cleanup:")
    print(f"   Memory:    {cleanup_mem:.2f} MB")
    print(f"   Recovered: {recovered:.2f} MB")
    
    mt5.shutdown()
    
    if growth < 200:  # Less than 200MB for 36K bars
        print("\n✅ Memory usage is reasonable for dataset size")
        return True
    else:
        print("\n⚠️  High memory usage - may need optimization")
        return False


if __name__ == "__main__":
    print("\n🧪 Starting Memory Leak Tests...\n")
    
    # Test 1: Multiple small backtests
    test1_passed = test_memory_leak()
    
    # Test 2: Single large backtest
    test2_passed = test_single_large_backtest()
    
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    
    if test1_passed and test2_passed:
        print("\n✅ ALL TESTS PASSED - No significant memory leaks detected!")
        print("\n💡 The system is safe for:")
        print("   - Long-running backtests")
        print("   - Multiple consecutive backtests")
        print("   - Production usage")
    else:
        print("\n⚠️  ATTENTION NEEDED")
        if not test1_passed:
            print("   - Memory accumulates across multiple runs")
        if not test2_passed:
            print("   - High memory usage on large datasets")
        print("\n   Consider optimization before production use")
