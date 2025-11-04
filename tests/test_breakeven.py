#!/usr/bin/env python3
"""
Test script để demo tính năng Move SL to Breakeven
"""

import MetaTrader5 as mt5
from core.ict_bot import ICTBot, Config
import json
import time
from datetime import datetime

def load_config():
    with open('config/config.json', 'r') as f:
        return json.load(f)

def main():
    print("="*70)
    print("TEST TÍNH NĂNG MOVE SL TO BREAKEVEN")
    print("="*70)
    
    # Load config
    config_data = load_config()
    account_config = config_data['accounts']['demo']
    
    # Use AUDUSDm symbol
    symbol_name = 'AUDUSDm'
    symbol_config = config_data['symbols'].get(symbol_name, {})
    
    # Create bot config with breakeven enabled
    bot_config = Config(
        symbol=symbol_name,
        timeframe=getattr(mt5, f"TIMEFRAME_{symbol_config.get('timeframe', 'M5')}"),
        risk_percent=symbol_config.get('risk_percent', 1.0),
        rr_ratio=symbol_config.get('rr_ratio', 2.0),
        move_sl_to_breakeven=True,  #  BẬT tính năng
        max_positions=1,
        magic_number=123457
    )
    
    print(f"\n Configuration:")
    print(f"  Symbol: {bot_config.symbol}")
    print(f"  Risk: {bot_config.risk_percent}%")
    print(f"  RR Ratio: {bot_config.rr_ratio}:1")
    print(f"  Move SL to Breakeven: {bot_config.move_sl_to_breakeven} ")
    
    # Create bot
    bot = ICTBot(bot_config)
    
    # Connect to MT5
    print(f"\n🔌 Connecting to {account_config['server']}...")
    if not bot.connect(
        login=account_config['login'],
        password=account_config['password'],
        server=account_config['server']
    ):
        print(" Connection failed!")
        return
    
    print(" Connected successfully!")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"\n Account Info:")
        print(f"  Balance: ${account_info.balance:.2f}")
        print(f"  Equity: ${account_info.equity:.2f}")
        print(f"  Margin: ${account_info.margin:.2f}")
    
    print("\n" + "="*70)
    print("🤖 BOT ĐANG CHẠY - Monitoring for breakeven opportunities...")
    print("="*70)
    print("\n Chú ý:")
    print("  1. Khi có tín hiệu  Mở 2 lệnh (Order 1: RR 1:1, Order 2: Main RR)")
    print("  2. Khi Order 1 hit TP  Tự động move SL Order 2 về breakeven")
    print("  3. Xem log để theo dõi quá trình")
    print("\n🛑 Nhấn Ctrl+C để dừng bot\n")
    
    try:
        cycle_count = 0
        while True:
            cycle_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Run one cycle
            bot.run_cycle()
            
            # Display status every 10 cycles
            if cycle_count % 10 == 0:
                positions = mt5.positions_get(symbol=bot_config.symbol)
                open_positions = len([p for p in positions if p.magic == bot_config.magic_number]) if positions else 0
                
                print(f"[{current_time}] Cycle {cycle_count} - Open positions: {open_positions}")
                
                if bot.current_trade:
                    print(f"   Current Trade:")
                    print(f"     Entry: {bot.current_trade.entry_price:.5f}")
                    print(f"     SL: {bot.current_trade.stop_loss:.5f}")
                    print(f"     TP1 Hit: {bot.current_trade.tp1_hit}")
                    print(f"     SL Moved to BE: {bot.current_trade.sl_moved_to_breakeven}")
            
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 Bot stopped by user")
        print("="*70)
        
        # Print stats
        stats = bot.get_stats()
        if stats['total_trades'] > 0:
            print(f"\n FINAL STATISTICS:")
            print(f"  Total Trades: {stats['total_trades']}")
            print(f"  Win Rate: {stats['win_rate']:.2f}%")
            print(f"  Profit Factor: {stats['profit_factor']:.2f}")
            print(f"  Total P/L: ${stats['total_profit']:.2f}")
        
        mt5.shutdown()

if __name__ == "__main__":
    main()
