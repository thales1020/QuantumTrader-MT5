#!/usr/bin/env python3
"""
Test historical data retrieval for XAUUSDm
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

print(f"Connected to {mt5.account_info().server}")
print()

symbol = "XAUUSDm"

# Make sure symbol is selected
if not mt5.symbol_select(symbol, True):
    print(f"Failed to select {symbol}")
    mt5.shutdown()
    exit(1)

print(f"Testing symbol: {symbol}")
print()

# Test 1: Get last 100 bars
print("Test 1: copy_rates_from_pos (last 100 bars)")
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
if rates is not None and len(rates) > 0:
    print(f" Success: {len(rates)} bars")
    print(f"  First: {datetime.fromtimestamp(rates[0]['time'])}")
    print(f"  Last:  {datetime.fromtimestamp(rates[-1]['time'])}")
else:
    print(f" Failed: {mt5.last_error()}")
print()

# Test 2: Get data from specific date range (short period)
print("Test 2: copy_rates_range (last 7 days)")
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start_date, end_date)
if rates is not None and len(rates) > 0:
    print(f" Success: {len(rates)} bars")
    print(f"  First: {datetime.fromtimestamp(rates[0]['time'])}")
    print(f"  Last:  {datetime.fromtimestamp(rates[-1]['time'])}")
else:
    print(f" Failed: {mt5.last_error()}")
print()

# Test 3: Get data from longer period (like backtest)
print("Test 3: copy_rates_range (2025-01-01 to 2025-10-01)")
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 10, 1)
print(f"  Start: {start_date}")
print(f"  End: {end_date}")
rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start_date, end_date)
if rates is not None and len(rates) > 0:
    print(f" Success: {len(rates)} bars")
    print(f"  First: {datetime.fromtimestamp(rates[0]['time'])}")
    print(f"  Last:  {datetime.fromtimestamp(rates[-1]['time'])}")
else:
    print(f" Failed: {mt5.last_error()}")
    print()
    print("ISSUE: Demo account may not have historical data that far back!")
    print()
    
    # Try to find available data range
    print("Finding available data range...")
    
    # Try recent dates
    for days_back in [30, 60, 90, 120, 150, 180]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start_date, end_date)
        if rates is not None and len(rates) > 0:
            print(f"   Last {days_back} days: {len(rates)} bars available")
        else:
            print(f"   Last {days_back} days: No data")

print()
print("="*60)
print("RECOMMENDATION")
print("="*60)
print("For demo accounts, historical data is limited.")
print("Use a shorter backtest period, for example:")
print("  Start: 2025-09-01 (or last 30-60 days)")
print("  End: 2025-10-16 (today)")

mt5.shutdown()
