"""Test ICTBot with Real MT5"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import MetaTrader5 as mt5
import pandas as pd
from core.ict_bot import ICTBot, ICTConfig

def test_connection():
    if not mt5.initialize():
        print("MT5 not initialized")
        return False
    account = mt5.account_info()
    if account:
        print(f"Connected: {account.login} | Balance: ${account.balance:.2f}")
        return True
    return False

def test_ict(symbol="EURUSDm"):
    print(f"\nTesting {symbol}...")
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 500)
    if rates is None:
        print("No data")
        return
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    config = ICTConfig(symbol=symbol, timeframe=mt5.TIMEFRAME_M15, risk_percent=1.0)
    bot = ICTBot(config)
    
    df = bot.calculate_indicators(df)
    signal = bot.generate_signal(df)
    
    print(f"  OBs: {len(bot.order_blocks)} | FVGs: {len(bot.fair_value_gaps)}")
    print(f"  Signal: {signal.get('type') if signal else 'None'}")

if __name__ == "__main__":
    if test_connection():
        test_ict("EURUSDm")
        test_ict("AUDUSDm")
        mt5.shutdown()
