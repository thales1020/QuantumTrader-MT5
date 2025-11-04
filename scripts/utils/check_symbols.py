#!/usr/bin/env python3
"""
Check available symbols and their data
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
print(f"Account: {mt5.account_info().login}")
print()

# Check symbols with GOLD/XAU in name
print("="*60)
print("SEARCHING FOR GOLD/XAU SYMBOLS")
print("="*60)

symbols = mt5.symbols_get()
gold_symbols = [s for s in symbols if 'XAU' in s.name or 'GOLD' in s.name.upper()]

if not gold_symbols:
    print("No gold symbols found!")
    print("\nTrying to find all available symbols with 'm' suffix:")
    m_symbols = [s for s in symbols if s.name.endswith('m')]
    for sym in m_symbols[:20]:
        print(f"  {sym.name}")
else:
    print(f"Found {len(gold_symbols)} gold symbols:\n")
    
    for sym in gold_symbols:
        print(f"Symbol: {sym.name}")
        print(f"  Description: {sym.description}")
        print(f"  Visible: {sym.visible}")
        print(f"  Selected: {sym.select}")
        print(f"  Currency: {sym.currency_base}/{sym.currency_profit}")
        print(f"  Digits: {sym.digits}")
        print(f"  Point: {sym.point}")
        print(f"  Trade Mode: {sym.trade_mode}")
        print(f"  Contract Size: {sym.trade_contract_size}")
        print(f"  Tick Size: {sym.trade_tick_size}")
        print(f"  Tick Value: {sym.trade_tick_value}")
        
        # Try to enable symbol
        if not sym.visible:
            print(f"  Attempting to enable...")
            if mt5.symbol_select(sym.name, True):
                print(f"   Enabled successfully")
            else:
                print(f"   Failed to enable")
        
        # Try to get data
        print(f"  Checking historical data...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        rates = mt5.copy_rates_range(sym.name, mt5.TIMEFRAME_M5, start_date, end_date)
        
        if rates is not None and len(rates) > 0:
            print(f"   Data available: {len(rates)} bars (last 30 days)")
            print(f"    Last bar time: {datetime.fromtimestamp(rates[-1]['time'])}")
        else:
            print(f"   No data available")
            print(f"    Error: {mt5.last_error()}")
        
        print()

# Try common symbol variations
print("="*60)
print("TRYING COMMON GOLD SYMBOL VARIATIONS")
print("="*60)

variations = [
    'XAUUSD',
    'XAUUSDm',
    'XAUUSD.m',
    'XAUUSD_m',
    'GOLD',
    'GOLDm',
    'GOLD.m'
]

for sym_name in variations:
    print(f"\nTrying: {sym_name}")
    
    # Try to select
    if mt5.symbol_select(sym_name, True):
        print(f"   Symbol found and selected")
        
        # Get info
        info = mt5.symbol_info(sym_name)
        if info:
            print(f"  Description: {info.description}")
            print(f"  Digits: {info.digits}")
            
            # Try to get data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            rates = mt5.copy_rates_range(sym_name, mt5.TIMEFRAME_M5, start_date, end_date)
            
            if rates is not None and len(rates) > 0:
                print(f"   Has data: {len(rates)} bars")
                print(f"   USE THIS SYMBOL: {sym_name}")
            else:
                print(f"   No data: {mt5.last_error()}")
    else:
        print(f"   Symbol not found")

mt5.shutdown()

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("Update your config.json with the correct symbol name")
print("Example:")
print('  "XAUUSDm": { ... }    "XAUUSD": { ... }')
