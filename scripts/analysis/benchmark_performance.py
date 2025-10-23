#!/usr/bin/env python3
"""
Performance Benchmark Script
Compare backtest performance before and after optimization
"""

import time
import psutil
import os
from datetime import datetime

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def benchmark_backtest():
    """Run backtest with performance monitoring"""
    print("="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    start_time = time.time()
    start_memory = get_memory_usage()
    
    print(f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Start Memory: {start_memory:.2f} MB")
    print()
    
    # Import here to measure import time
    import_start = time.time()
    try:
        import MetaTrader5 as mt5
        from core.ict_bot import ICTBot, Config
        from engines.ict_backtest_engine import ICTBacktestEngine
        import json
        from datetime import datetime as dt, timedelta
    except ImportError as e:
        print(f"Error importing modules: {e}")
        return
    
    import_time = time.time() - import_start
    print(f"Import Time: {import_time:.2f}s")
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
    
    # Load config
    with open('config/config.json', 'r') as f:
        config_data = json.load(f)
    
    # Setup bot
    symbol = "XAUUSDm"
    config = Config(
        symbol=symbol,
        timeframe=mt5.TIMEFRAME_M5,
        risk_percent=1.0,
        rr_ratio=6.0,
    )
    
    bot = ICTBot(config)
    
    # Connect to account
    account = config_data['accounts']['demo']
    if not bot.connect(account['login'], account['password'], account['server']):
        print("Connection failed")
        mt5.shutdown()
        return
    
    print(f"Connected to MT5")
    memory_after_connect = get_memory_usage()
    print(f"Memory after connect: {memory_after_connect:.2f} MB")
    print()
    
    # Run backtest
    backtest_start = time.time()
    
    engine = ICTBacktestEngine(bot, initial_balance=10000)
    
    start_date = dt(2025, 1, 1)
    end_date = dt(2025, 10, 1)
    
    print("Running backtest...")
    result = engine.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        timeframe=mt5.TIMEFRAME_M5
    )
    
    backtest_time = time.time() - backtest_start
    
    # Final measurements
    end_time = time.time()
    end_memory = get_memory_usage()
    total_time = end_time - start_time
    
    print()
    print("="*60)
    print("PERFORMANCE RESULTS")
    print("="*60)
    print(f"Total Time: {total_time:.2f}s ({total_time/60:.2f} min)")
    print(f"Backtest Time: {backtest_time:.2f}s ({backtest_time/60:.2f} min)")
    print(f"Start Memory: {start_memory:.2f} MB")
    print(f"Peak Memory: {end_memory:.2f} MB")
    print(f"Memory Growth: {end_memory - start_memory:.2f} MB")
    print()
    
    if result:
        print("BACKTEST SUMMARY")
        print("-"*60)
        print(f"Total Trades: {result.get('total_trades', 0)}")
        print(f"Win Rate: {result.get('win_rate', 0):.2f}%")
        print(f"Profit Factor: {result.get('profit_factor', 0):.2f}")
        print(f"Final Balance: ${result.get('final_balance', 0):,.2f}")
        print(f"Total Return: {result.get('total_return', 0):.2f}%")
        print()
        
        # Calculate performance metrics
        bars_processed = result.get('total_bars', 52988)
        bars_per_second = bars_processed / backtest_time
        trades_per_minute = (result.get('total_trades', 0) / backtest_time) * 60
        
        print("PERFORMANCE METRICS")
        print("-"*60)
        print(f"Bars Processed: {bars_processed:,}")
        print(f"Bars/Second: {bars_per_second:.2f}")
        print(f"Trades/Minute: {trades_per_minute:.2f}")
        print(f"Memory/Bar: {(end_memory - start_memory) / bars_processed * 1000:.4f} KB")
    
    mt5.shutdown()
    print("="*60)

if __name__ == "__main__":
    benchmark_backtest()
