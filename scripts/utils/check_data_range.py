#!/usr/bin/env python3
"""
Check available historical data range for symbols
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
print(f"Account Type: Demo")
print()

symbols = ['XAUUSDm', 'EURUSDm', 'GBPUSDm', 'USDJPYm']

print("="*70)
print("CHECKING HISTORICAL DATA AVAILABILITY")
print("="*70)

for symbol in symbols:
    print(f"\n{'='*70}")
    print(f"Symbol: {symbol}")
    print(f"{'='*70}")
    
    # Enable symbol
    mt5.symbol_select(symbol, True)
    
    # Test different date ranges
    test_periods = [
        ("Last 30 days", datetime.now() - timedelta(days=30), datetime.now()),
        ("Last 90 days", datetime.now() - timedelta(days=90), datetime.now()),
        ("Last 180 days", datetime.now() - timedelta(days=180), datetime.now()),
        ("Last 365 days", datetime.now() - timedelta(days=365), datetime.now()),
        ("2024 Full Year", datetime(2024, 1, 1), datetime(2024, 12, 31)),
        ("2024 H1", datetime(2024, 1, 1), datetime(2024, 6, 30)),
        ("2024 H2", datetime(2024, 7, 1), datetime(2024, 12, 31)),
        ("2025 Q1", datetime(2025, 1, 1), datetime(2025, 3, 31)),
        ("2025 Q2", datetime(2025, 4, 1), datetime(2025, 6, 30)),
        ("2025 Q3", datetime(2025, 7, 1), datetime(2025, 9, 30)),
    ]
    
    available_ranges = []
    
    for period_name, start_date, end_date in test_periods:
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start_date, end_date)
        
        if rates is not None and len(rates) > 0:
            first_bar = datetime.fromtimestamp(rates[0]['time'])
            last_bar = datetime.fromtimestamp(rates[-1]['time'])
            
            status = "✓"
            available_ranges.append(period_name)
            
            print(f"  {status} {period_name:<20} {len(rates):>6,} bars  ({first_bar.strftime('%Y-%m-%d')} to {last_bar.strftime('%Y-%m-%d')})")
        else:
            print(f"  ✗ {period_name:<20} No data available")
    
    if available_ranges:
        print(f"\n  Available periods: {', '.join(available_ranges)}")
        
        # Find earliest available data
        print(f"\n  Finding earliest available data...")
        for months_back in [12, 9, 6, 3, 2, 1]:
            start = datetime.now() - timedelta(days=months_back*30)
            rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start, datetime.now())
            if rates is not None and len(rates) > 0:
                earliest = datetime.fromtimestamp(rates[0]['time'])
                print(f"  → Earliest data: {earliest.strftime('%Y-%m-%d')} ({months_back} months back)")
                break
    else:
        print(f"\n  ⚠️  No historical data available for {symbol}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print()
print("Demo accounts typically have limited historical data:")
print("  • Standard demo: 3-6 months")
print("  • Premium demo: 6-12 months")
print("  • Live accounts: Usually have more historical data")
print()
print("RECOMMENDATION:")
print("  1. For 2024 data: Use a live account or broker with longer history")
print("  2. For demo: Use recent date ranges (last 3-6 months)")
print("  3. Current optimal range: 2025-04-01 to 2025-10-16")

mt5.shutdown()
