#!/usr/bin/env python3
"""
Interactive test script for BTC buy/sell orders
Tests dual order strategy with realistic parameters
"""

import MetaTrader5 as mt5
import json
import sys
from datetime import datetime
from pathlib import Path


def load_config():
    """Load configuration"""
    config_path = Path('config/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def connect_mt5(demo_config):
    """Connect to MT5"""
    if not mt5.initialize():
        print("[ERROR] MT5 initialization failed")
        return False
    
    if not mt5.login(
        demo_config['login'],
        password=demo_config['password'],
        server=demo_config['server']
    ):
        print(f"[ERROR] Login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    return True


def is_crypto(symbol_name):
    """Check if symbol is crypto"""
    crypto_symbols = ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']
    return any(crypto in symbol_name.upper() for crypto in crypto_symbols)


def calculate_crypto_lot_size(balance, risk_percent, sl_distance, contract_size):
    """Calculate lot size for crypto (USD-based)"""
    risk_amount = balance * (risk_percent / 100)
    lot_size = risk_amount / (sl_distance * contract_size)
    lot_size = round(lot_size, 2)
    return lot_size


def place_dual_orders_crypto(symbol, order_type, balance, symbol_config):
    """Place dual orders for crypto (RR 1:1 + Main RR)"""
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"[ERROR] Symbol {symbol} not found")
        return False
    
    # Enable symbol if needed
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"[ERROR] Failed to get tick for {symbol}")
        return False
    
    # Get config values
    risk_percent = symbol_config.get('risk_percent', 0.5)
    sl_multiplier = symbol_config.get('sl_multiplier', 2.0)
    tp_multiplier = symbol_config.get('tp_multiplier', 8.0)
    
    # Calculate SL/TP distances in USD
    # For crypto, we use price-based distances
    if order_type == "BUY":
        entry_price = tick.ask
        # Estimate ATR-based SL (simplified - using 3% of price as proxy)
        atr_estimate = entry_price * 0.03
        sl_distance = atr_estimate * sl_multiplier
        
        sl_price = entry_price - sl_distance
        tp1_distance = sl_distance  # RR 1:1
        tp2_distance = sl_distance * (tp_multiplier / sl_multiplier)  # Main RR
        
        tp1_price = entry_price + tp1_distance
        tp2_price = entry_price + tp2_distance
        
    else:  # SELL
        entry_price = tick.bid
        atr_estimate = entry_price * 0.03
        sl_distance = atr_estimate * sl_multiplier
        
        sl_price = entry_price + sl_distance
        tp1_distance = sl_distance
        tp2_distance = sl_distance * (tp_multiplier / sl_multiplier)
        
        tp1_price = entry_price - tp1_distance
        tp2_price = entry_price - tp2_distance
    
    # Calculate lot sizes (each order risks risk_percent/2)
    contract_size = symbol_info.trade_contract_size
    lot_size_per_order = calculate_crypto_lot_size(
        balance,
        risk_percent / 2,  # Split risk between 2 orders
        sl_distance,
        contract_size
    )
    
    # Ensure minimum lot size
    lot_size_per_order = max(symbol_info.volume_min, lot_size_per_order)
    
    # Display order details
    print()
    print("="*70)
    print(f"DUAL ORDER SETUP - {symbol}")
    print("="*70)
    print(f"Order Type: {order_type}")
    print(f"Entry Price: ${entry_price:,.2f}")
    print(f"Stop Loss: ${sl_price:,.2f} (${sl_distance:,.2f} distance)")
    print()
    print(f"ORDER 1 (RR 1:1 - Quick Profit):")
    print(f"  Lot Size: {lot_size_per_order}")
    print(f"  Take Profit: ${tp1_price:,.2f} (${tp1_distance:,.2f} distance)")
    print(f"  Risk: ${balance * (risk_percent/2) / 100:.2f} ({risk_percent/2}%)")
    print(f"  Potential Profit: ${tp1_distance * contract_size * lot_size_per_order:.2f}")
    print()
    print(f"ORDER 2 (RR {tp_multiplier/sl_multiplier:.1f}:1 - Main Target):")
    print(f"  Lot Size: {lot_size_per_order}")
    print(f"  Take Profit: ${tp2_price:,.2f} (${tp2_distance:,.2f} distance)")
    print(f"  Risk: ${balance * (risk_percent/2) / 100:.2f} ({risk_percent/2}%)")
    print(f"  Potential Profit: ${tp2_distance * contract_size * lot_size_per_order:.2f}")
    print()
    print(f"TOTAL RISK: ${balance * risk_percent / 100:.2f} ({risk_percent}%)")
    print(f"TOTAL POTENTIAL (if both hit TP): ${(tp1_distance + tp2_distance) * contract_size * lot_size_per_order:.2f}")
    print("="*70)
    print()
    
    # Confirm
    confirm = input("Place these orders? (yes/no): ")
    if confirm.lower() != 'yes':
        print("[CANCELLED] Orders not placed")
        return False
    
    # Place Order 1 (RR 1:1)
    print()
    print("[SENDING] Placing Order 1 (RR 1:1)...")
    
    request1 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size_per_order,
        "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": entry_price,
        "sl": sl_price,
        "tp": tp1_price,
        "deviation": 20,
        "magic": 123456,
        "comment": "Dual Order 1 - RR 1:1",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result1 = mt5.order_send(request1)
    
    if result1.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Order 1 failed!")
        print(f"        Retcode: {result1.retcode}")
        print(f"        Comment: {result1.comment}")
        return False
    
    print(f"[SUCCESS] Order 1 placed - Ticket: {result1.order}")
    
    # Place Order 2 (Main RR)
    print()
    print(f"[SENDING] Placing Order 2 (RR {tp_multiplier/sl_multiplier:.1f}:1)...")
    
    request2 = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size_per_order,
        "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": entry_price,
        "sl": sl_price,
        "tp": tp2_price,
        "deviation": 20,
        "magic": 123456,
        "comment": f"Dual Order 2 - RR {tp_multiplier/sl_multiplier:.1f}:1",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result2 = mt5.order_send(request2)
    
    if result2.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Order 2 failed!")
        print(f"        Retcode: {result2.retcode}")
        print(f"        Comment: {result2.comment}")
        
        # Rollback: Close Order 1
        print("[ROLLBACK] Closing Order 1...")
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": result1.order,
            "symbol": symbol,
            "volume": lot_size_per_order,
            "type": mt5.ORDER_TYPE_SELL if order_type == "BUY" else mt5.ORDER_TYPE_BUY,
            "price": tick.bid if order_type == "BUY" else tick.ask,
            "deviation": 20,
            "magic": 123456,
            "comment": "Rollback - Order 2 failed",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(close_request)
        return False
    
    print(f"[SUCCESS] Order 2 placed - Ticket: {result2.order}")
    
    # Display positions
    print()
    print("="*70)
    print("POSITIONS OPENED")
    print("="*70)
    
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            if pos.ticket in [result1.order, result2.order]:
                order_num = "1 (RR 1:1)" if pos.ticket == result1.order else f"2 (RR {tp_multiplier/sl_multiplier:.1f}:1)"
                print(f"\nOrder {order_num}:")
                print(f"  Ticket: {pos.ticket}")
                print(f"  Time: {datetime.fromtimestamp(pos.time)}")
                print(f"  Type: {'BUY' if pos.type == 0 else 'SELL'}")
                print(f"  Volume: {pos.volume}")
                print(f"  Entry: ${pos.price_open:,.2f}")
                print(f"  Current: ${pos.price_current:,.2f}")
                print(f"  SL: ${pos.sl:,.2f}")
                print(f"  TP: ${pos.tp:,.2f}")
                print(f"  Profit: ${pos.profit:.2f}")
    
    print()
    print("="*70)
    print("[OK] Dual orders placed successfully!")
    print("="*70)
    
    return True


def main():
    print()
    print("="*70)
    print("CRYPTO DUAL ORDERS TEST - BTC/ETH")
    print("="*70)
    print()
    
    # Load config
    config = load_config()
    demo_config = config['accounts']['demo']
    
    # Connect to MT5
    print("Connecting to MT5...")
    if not connect_mt5(demo_config):
        sys.exit(1)
    
    account_info = mt5.account_info()
    print(f"[OK] Connected to {account_info.server}")
    print(f"     Account: {account_info.login}")
    print(f"     Balance: ${account_info.balance:.2f}")
    print()
    
    # Get available crypto symbols
    symbols_config = config.get('symbols', {})
    crypto_symbols = {
        name: cfg for name, cfg in symbols_config.items()
        if is_crypto(name) and cfg.get('enabled', False)
    }
    
    if not crypto_symbols:
        print("[ERROR] No crypto symbols enabled in config")
        mt5.shutdown()
        sys.exit(1)
    
    print("Available crypto symbols:")
    for i, symbol in enumerate(crypto_symbols.keys(), 1):
        print(f"  {i}. {symbol}")
    print()
    
    # Select symbol
    choice = input(f"Select symbol (1-{len(crypto_symbols)}): ")
    try:
        idx = int(choice) - 1
        symbol_name = list(crypto_symbols.keys())[idx]
        symbol_config = crypto_symbols[symbol_name]
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection")
        mt5.shutdown()
        sys.exit(1)
    
    # Select order type
    print()
    print("Order type:")
    print("  1. BUY")
    print("  2. SELL")
    order_choice = input("Select order type (1-2): ")
    
    order_type = "BUY" if order_choice == "1" else "SELL"
    
    # Place dual orders
    success = place_dual_orders_crypto(
        symbol_name,
        order_type,
        account_info.balance,
        symbol_config
    )
    
    # Cleanup
    mt5.shutdown()
    
    print()
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed or cancelled")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
