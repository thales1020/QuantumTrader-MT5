#!/usr/bin/env python3
"""
Test script to check if a symbol is available in MT5
"""

import MetaTrader5 as mt5
import json

# Load config
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Get credentials
demo_config = config['accounts']['demo']

# Initialize and login
if not mt5.initialize():
    print("[ERROR] MT5 initialization failed")
    exit(1)

if not mt5.login(demo_config['login'], password=demo_config['password'], server=demo_config['server']):
    print(f"[ERROR] Login failed: {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

print(f"[OK] Connected to {mt5.account_info().server}")
print(f"   Account: {mt5.account_info().login}")
print()

# Test XAUUSD
symbol = "XAUUSD"
print(f"Testing symbol: {symbol}")
print("-" * 50)

# Check symbol info
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"[ERROR] Symbol {symbol} not found!")
    print("\nTrying alternative names...")
    
    # Try common variations
    alternatives = ["XAUUSDm", "XAUUSD.", "GOLD", "XAU/USD", "XAUUSD.i"]
    for alt in alternatives:
        info = mt5.symbol_info(alt)
        if info is not None:
            print(f"[OK] Found: {alt}")
            symbol = alt
            symbol_info = info
            break
else:
    print(f"[OK] Symbol found: {symbol}")

if symbol_info is not None:
    print(f"\nSymbol Details:")
    print(f"  Name: {symbol_info.name}")
    print(f"  Description: {symbol_info.description}")
    print(f"  Visible: {symbol_info.visible}")
    print(f"  Select: {symbol_info.select}")
    print(f"  Digits: {symbol_info.digits}")
    print(f"  Point: {symbol_info.point}")
    
    # Try to enable in Market Watch
    if not symbol_info.visible or not symbol_info.select:
        print(f"\n[WARNING] Symbol not in Market Watch, enabling...")
        if mt5.symbol_select(symbol, True):
            print(f"[OK] Symbol enabled successfully")
        else:
            print(f"[ERROR] Failed to enable symbol")
    
    # Try to get rates
    print(f"\nTrying to load historical data...")
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
    
    if rates is None or len(rates) == 0:
        print(f"[ERROR] No data available: {mt5.last_error()}")
    else:
        print(f"[OK] Successfully loaded {len(rates)} bars")
        print(f"   Latest bar: {rates[-1]}")

# List all available symbols with "XAU" or "GOLD"
print("\n" + "="*50)
print("Available Gold/XAU symbols on this broker:")
print("="*50)

all_symbols = mt5.symbols_get()
gold_symbols = [s for s in all_symbols if 'XAU' in s.name.upper() or 'GOLD' in s.name.upper()]

if gold_symbols:
    for s in gold_symbols:
        print(f"  {s.name:20} - {s.description}")
else:
    print("  No gold symbols found")

mt5.shutdown()
print("\n[OK] Test complete")
