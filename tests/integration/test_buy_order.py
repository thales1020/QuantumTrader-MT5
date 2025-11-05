#!/usr/bin/env python3
"""
Test script to place a BUY order for XAUUSDm
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

# Load config
with open('config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Get credentials
demo_config = config['accounts']['demo']

print("="*60)
print("XAUUSDm BUY Order Test")
print("="*60)

# Initialize and login
if not mt5.initialize():
    print("[ERROR] MT5 initialization failed")
    exit(1)

print("[OK] MT5 initialized")

if not mt5.login(demo_config['login'], password=demo_config['password'], server=demo_config['server']):
    print(f"[ERROR] Login failed: {mt5.last_error()}")
    mt5.shutdown()
    exit(1)

print(f"[OK] Logged in to {mt5.account_info().server}")
print(f"     Account: {mt5.account_info().login}")
print(f"     Balance: ${mt5.account_info().balance:.2f}")
print()

# Symbol setup
symbol = "XAUUSDm"

# Get symbol info
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"[ERROR] Symbol {symbol} not found")
    mt5.shutdown()
    exit(1)

# Enable symbol in Market Watch if needed
if not symbol_info.visible:
    if not mt5.symbol_select(symbol, True):
        print(f"[ERROR] Failed to select {symbol}")
        mt5.shutdown()
        exit(1)
    print(f"[OK] Symbol {symbol} enabled in Market Watch")

# Get current price
tick = mt5.symbol_info_tick(symbol)
if tick is None:
    print(f"[ERROR] Failed to get tick for {symbol}")
    mt5.shutdown()
    exit(1)

print(f"[INFO] Current Price:")
print(f"       Ask: {tick.ask}")
print(f"       Bid: {tick.bid}")
print()

# Calculate order parameters
volume = 0.01  # Minimum lot size
price = tick.ask
point = symbol_info.point

# Calculate SL and TP (based on pips)
sl_pips = 50  # 50 pips stop loss
tp_pips = 100  # 100 pips take profit

# For XAUUSDm, 1 pip = 0.01 (depends on broker)
pip_size = 0.01 if symbol_info.digits == 3 else 0.1

sl = price - (sl_pips * pip_size)
tp = price + (tp_pips * pip_size)

print(f"[INFO] Order Parameters:")
print(f"       Type: BUY")
print(f"       Volume: {volume}")
print(f"       Entry Price: {price}")
print(f"       Stop Loss: {sl} ({sl_pips} pips)")
print(f"       Take Profit: {tp} ({tp_pips} pips)")
print(f"       Risk: ~${volume * sl_pips * pip_size / point * symbol_info.trade_tick_value:.2f}")
print()

# Confirm
confirm = input("Do you want to place this order? (yes/no): ")
if confirm.lower() != 'yes':
    print("[CANCELLED] Order not placed")
    mt5.shutdown()
    exit(0)

# Prepare order request
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": volume,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": sl,
    "tp": tp,
    "deviation": 20,
    "magic": 234567,  # Test magic number
    "comment": "Test BUY order",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

print("[SENDING] Placing order...")
result = mt5.order_send(request)

# Check result
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"[ERROR] Order failed!")
    print(f"        Retcode: {result.retcode}")
    print(f"        Comment: {result.comment}")
    print(f"        Request: {result.request}")
else:
    print("[SUCCESS] Order placed successfully!")
    print(f"          Order ticket: {result.order}")
    print(f"          Volume: {result.volume}")
    print(f"          Price: {result.price}")
    print(f"          Bid: {result.bid}")
    print(f"          Ask: {result.ask}")
    print()
    
    # Get position info
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            if pos.ticket == result.order:
                print(f"[POSITION] Details:")
                print(f"           Ticket: {pos.ticket}")
                print(f"           Time: {datetime.fromtimestamp(pos.time)}")
                print(f"           Type: {'BUY' if pos.type == 0 else 'SELL'}")
                print(f"           Volume: {pos.volume}")
                print(f"           Price: {pos.price_open}")
                print(f"           Current: {pos.price_current}")
                print(f"           SL: {pos.sl}")
                print(f"           TP: {pos.tp}")
                print(f"           Profit: ${pos.profit:.2f}")
                print(f"           Swap: ${pos.swap:.2f}")

# Cleanup
mt5.shutdown()
print()
print("="*60)
print("[OK] Test complete")
print("="*60)
