#!/usr/bin/env python3
"""
Simple Backtest Runner for ML-SuperTrend-MT5
This script runs a backtest on historical data
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys

# Import bot components
from core.supertrend_bot import SuperTrendBot, Config

def load_config(config_file="config/config.json"):
    """Load configuration"""
    with open(config_file, 'r') as f:
        return json.load(f)

def initialize_mt5(account_config):
    """Initialize MT5 connection"""
    if not mt5.initialize():
        print("[ERROR] MT5 initialization failed")
        return False
    
    if not mt5.login(account_config['login'], 
                     password=account_config['password'], 
                     server=account_config['server']):
        print(f"[ERROR] Login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print(f"[OK] Connected to {account_config['server']}")
    return True

def run_simple_backtest(symbol, timeframe, start_date, end_date, config):
    """Run a simple backtest"""
    print("\n" + "="*60)
    print("BACKTEST SIMULATION")
    print("="*60)
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("="*60 + "\n")
    
    # Load historical data
    print("[LOADING] Fetching historical data...")
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    
    if rates is None or len(rates) == 0:
        print(f"[ERROR] No data available for {symbol}")
        print(f"        Error: {mt5.last_error()}")
        return None
    
    print(f"[OK] Loaded {len(rates)} bars")
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Backtest variables
    initial_balance = 10000.0
    balance = initial_balance
    equity = initial_balance
    positions = []
    closed_trades = []
    
    print(f"[INFO] Initial Balance: ${initial_balance:.2f}")
    print(f"[INFO] Risk per trade: {config.risk_percent}%")
    print("\n[SIMULATING] Running backtest...\n")
    
    # Simple SuperTrend backtest
    for i in range(200, len(df)):
        current_bar = df.iloc[i]
        
        # Simple moving average crossover strategy (placeholder for SuperTrend)
        # You can replace this with actual SuperTrend logic
        if i > 20:
            # Simple trend detection
            ma_short = df['close'].iloc[i-10:i].mean()
            ma_long = df['close'].iloc[i-20:i].mean()
            
            # Entry signals
            buy_signal = ma_short > ma_long and len(positions) == 0
            sell_signal = ma_short < ma_long and len(positions) == 0
            
            # Calculate ATR for SL/TP
            high_low = df['high'].iloc[i-14:i] - df['low'].iloc[i-14:i]
            atr = high_low.mean()
            
            # Open position
            if buy_signal:
                entry_price = current_bar['close']
                sl = entry_price - (atr * config.sl_multiplier)
                tp = entry_price + (atr * config.tp_multiplier)
                
                # Calculate position size
                risk_amount = balance * (config.risk_percent / 100)
                # Simplified position sizing
                volume = 0.01  # Fixed for demo
                
                positions.append({
                    'type': 'BUY',
                    'entry_price': entry_price,
                    'sl': sl,
                    'tp': tp,
                    'volume': volume,
                    'entry_time': current_bar['time']
                })
                
                print(f"[BUY] {current_bar['time'].strftime('%Y-%m-%d %H:%M')} | "
                      f"Price: {entry_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
            
            elif sell_signal:
                entry_price = current_bar['close']
                sl = entry_price + (atr * config.sl_multiplier)
                tp = entry_price - (atr * config.tp_multiplier)
                
                risk_amount = balance * (config.risk_percent / 100)
                volume = 0.01
                
                positions.append({
                    'type': 'SELL',
                    'entry_price': entry_price,
                    'sl': sl,
                    'tp': tp,
                    'volume': volume,
                    'entry_time': current_bar['time']
                })
                
                print(f"[SELL] {current_bar['time'].strftime('%Y-%m-%d %H:%M')} | "
                      f"Price: {entry_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        
        # Check exit conditions for open positions
        for pos in positions[:]:
            current_price = current_bar['close']
            
            # Check SL/TP hit
            hit_sl = False
            hit_tp = False
            
            if pos['type'] == 'BUY':
                hit_sl = current_price <= pos['sl']
                hit_tp = current_price >= pos['tp']
            else:  # SELL
                hit_sl = current_price >= pos['sl']
                hit_tp = current_price <= pos['tp']
            
            if hit_sl or hit_tp:
                exit_price = pos['sl'] if hit_sl else pos['tp']
                
                # Calculate P&L (simplified)
                if pos['type'] == 'BUY':
                    pnl = (exit_price - pos['entry_price']) * pos['volume'] * 100
                else:
                    pnl = (pos['entry_price'] - exit_price) * pos['volume'] * 100
                
                balance += pnl
                
                result = "SL HIT" if hit_sl else "TP HIT"
                print(f"[CLOSE] {current_bar['time'].strftime('%Y-%m-%d %H:%M')} | "
                      f"{result} | P&L: ${pnl:.2f} | Balance: ${balance:.2f}")
                
                closed_trades.append({
                    'entry_time': pos['entry_time'],
                    'exit_time': current_bar['time'],
                    'type': pos['type'],
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'result': 'WIN' if pnl > 0 else 'LOSS'
                })
                
                positions.remove(pos)
    
    # Calculate statistics
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    
    if len(closed_trades) > 0:
        wins = [t for t in closed_trades if t['pnl'] > 0]
        losses = [t for t in closed_trades if t['pnl'] < 0]
        
        total_trades = len(closed_trades)
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = sum(t['pnl'] for t in wins)
        total_loss = abs(sum(t['pnl'] for t in losses))
        net_profit = balance - initial_balance
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        print(f"Initial Balance:  ${initial_balance:.2f}")
        print(f"Final Balance:    ${balance:.2f}")
        print(f"Net Profit:       ${net_profit:.2f} ({(net_profit/initial_balance*100):.2f}%)")
        print(f"\nTotal Trades:     {total_trades}")
        print(f"Wins:             {win_count} ({win_rate:.1f}%)")
        print(f"Losses:           {loss_count} ({100-win_rate:.1f}%)")
        print(f"\nProfit Factor:    {profit_factor:.2f}")
        print(f"Avg Win:          ${total_profit/win_count:.2f}" if win_count > 0 else "Avg Win: $0.00")
        print(f"Avg Loss:         ${total_loss/loss_count:.2f}" if loss_count > 0 else "Avg Loss: $0.00")
        
        # Show trade details
        print("\n" + "="*60)
        print("TRADE HISTORY")
        print("="*60)
        for i, trade in enumerate(closed_trades[-10:], 1):  # Last 10 trades
            print(f"{i}. {trade['entry_time'].strftime('%Y-%m-%d')} | "
                  f"{trade['type']:4} | "
                  f"Entry: {trade['entry_price']:.2f} | "
                  f"Exit: {trade['exit_price']:.2f} | "
                  f"P&L: ${trade['pnl']:+.2f} | "
                  f"{trade['result']}")
    else:
        print("No trades executed during backtest period")
    
    print("="*60)
    
    return {
        'initial_balance': initial_balance,
        'final_balance': balance,
        'net_profit': balance - initial_balance,
        'trades': closed_trades
    }

def main():
    # Load configuration
    config_data = load_config()
    
    # Get account config
    account_config = config_data['accounts']['demo']
    
    # Initialize MT5
    if not initialize_mt5(account_config):
        sys.exit(1)
    
    # Backtest parameters
    symbol = "XAUUSDm"  # Change to your symbol
    timeframe = mt5.TIMEFRAME_H1  # 1 Hour
    
    # Date range - last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Create config
    symbol_config = config_data['symbols'].get(symbol, config_data['symbols']['EURUSD'])
    
    config = Config(
        symbol=symbol,
        timeframe=timeframe,
        atr_period=config_data['global_settings']['atr_period'],
        min_factor=symbol_config['min_factor'],
        max_factor=symbol_config['max_factor'],
        risk_percent=symbol_config['risk_percent'],
        sl_multiplier=symbol_config['sl_multiplier'],
        tp_multiplier=symbol_config['tp_multiplier']
    )
    
    # Run backtest
    results = run_simple_backtest(symbol, timeframe, start_date, end_date, config)
    
    # Cleanup
    mt5.shutdown()
    print("\n[OK] Backtest complete")

if __name__ == "__main__":
    main()
