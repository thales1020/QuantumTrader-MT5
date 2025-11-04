#!/usr/bin/env python3
"""
Test which timeframes have data for XAUUSDm
"""

import MetaTrader5 as mt5
import json
from datetime import datetime, timedelta

# Load config
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    exit(1)

# Connect to account
account = config['accounts']['demo']
if not mt5.login(account['login'], password=account['password'], server=account['server']):
    print(f"Login failed: {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

symbol = "XAUUSDm"

# Make sure symbol is selected
mt5.symbol_select(symbol, True)

print(f"Testing timeframes for {symbol}")
print(f"Period: 2025-01-01 to 2025-10-01")
print("="*60)

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 10, 1)

timeframes = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1
}

for name, tf in timeframes.items():
    print(f"\nTimeframe: {name}")
    
    rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
    
    if rates is not None and len(rates) > 0:
        print(f"   Data available: {len(rates):,} bars")
        print(f"    First: {datetime.fromtimestamp(rates[0]['time'])}")
        print(f"    Last:  {datetime.fromtimestamp(rates[-1]['time'])}")
        
        # Estimate memory
        memory_mb = len(rates) * 104 / 1024 / 1024  # ~104 bytes per bar
        print(f"    Est. memory: {memory_mb:.2f} MB")
    else:
        error = mt5.last_error()
        print(f"   No data available")
        print(f"    Error: {error}")

print()
print("="*60)
print("RECOMMENDATION")
print("="*60)
print("For 9-month backtest period:")
print("   M5-H4: Recommended (reasonable data size)")
print("  ⚠ M1: May be too much data or not available")
print("  ⚠ D1: Too few bars for detailed analysis")

mt5.shutdown()
