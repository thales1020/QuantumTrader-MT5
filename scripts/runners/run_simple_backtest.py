#!/usr/bin/env python3
"""
Simple Backtest Runner using BacktestEngine
Uses the completed backtest_engine.py
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import sys
import logging

from engines.backtest_engine import BacktestEngine

# Simple Strategy Class
class SimpleStrategy:
    """Simple MA Crossover Strategy for testing"""
    
    def __init__(self, short_period=10, long_period=20, atr_period=14):
        self.short_period = short_period
        self.long_period = long_period
        self.atr_period = atr_period
    
    def generate_signal(self, df):
        """Generate buy/sell signals"""
        if len(df) < self.long_period + 1:
            return None
        
        # Calculate moving averages
        ma_short = df['close'].iloc[-self.short_period:].mean()
        ma_long = df['close'].iloc[-self.long_period:].mean()
        
        # Previous MAs
        ma_short_prev = df['close'].iloc[-(self.short_period+1):-1].mean()
        ma_long_prev = df['close'].iloc[-(self.long_period+1):-1].mean()
        
        # Calculate ATR for SL/TP
        high_low = df['high'].iloc[-self.atr_period:] - df['low'].iloc[-self.atr_period:]
        atr = high_low.mean()
        
        current_price = df['close'].iloc[-1]
        
        # Buy signal
        if ma_short > ma_long and ma_short_prev <= ma_long_prev:
            return {
                'type': 'BUY',
                'sl': current_price - (atr * 2),
                'tp': current_price + (atr * 3),
                'volume': 0.01
            }
        
        # Sell signal
        elif ma_short < ma_long and ma_short_prev >= ma_long_prev:
            return {
                'type': 'SELL',
                'sl': current_price + (atr * 2),
                'tp': current_price - (atr * 3),
                'volume': 0.01
            }
        
        return None

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    demo_config = config['accounts']['demo']
    
    # Initialize MT5
    if not mt5.initialize():
        print("[ERROR] MT5 initialization failed")
        sys.exit(1)
    
    if not mt5.login(demo_config['login'], 
                     password=demo_config['password'], 
                     server=demo_config['server']):
        print(f"[ERROR] Login failed: {mt5.last_error()}")
        mt5.shutdown()
        sys.exit(1)
    
    print(f"[OK] Connected to {demo_config['server']}")
    
    # Backtest parameters
    symbol = "XAUUSDm"
    timeframe = mt5.TIMEFRAME_H1
    initial_balance = 10000
    
    # Date range - last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print("\n" + "="*60)
    print(f"BACKTEST: {symbol}")
    print("="*60)
    print(f"Timeframe: H1")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Initial Balance: ${initial_balance:,.2f}")
    print("Strategy: MA Crossover (10/20)")
    print("="*60)
    
    # Create strategy and backtest engine
    strategy = SimpleStrategy(short_period=10, long_period=20)
    engine = BacktestEngine(strategy, initial_balance=initial_balance)
    
    # Run backtest
    report = engine.run_backtest(symbol, start_date, end_date, timeframe)
    
    # Print results
    if report:
        engine.print_report(report)
        
        # Show last 10 trades
        if len(report['trades']) > 0:
            print("\n" + "="*60)
            print("LAST 10 TRADES")
            print("="*60)
            for i, trade in enumerate(report['trades'][-10:], 1):
                print(f"{i:2}. {trade['entry_time'].strftime('%Y-%m-%d %H:%M')} | "
                      f"{trade['type']:4} | "
                      f"Entry: {trade['entry_price']:.2f} | "
                      f"Exit: {trade['exit_price']:.2f} | "
                      f"P&L: ${trade['pnl']:+7.2f} | "
                      f"{trade['reason']}")
            print("="*60)
    
    # Cleanup
    mt5.shutdown()
    print("\n[OK] Backtest complete")

if __name__ == "__main__":
    main()
