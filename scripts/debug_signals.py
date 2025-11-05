"""Debug data to see why no trades"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

mt5.initialize()

# Load data
rates = mt5.copy_rates_range('EURUSDm', mt5.TIMEFRAME_H1, datetime(2025, 1, 1), datetime(2025, 11, 4))
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Calculate SMAs
df['sma_fast'] = df['close'].rolling(10).mean()
df['sma_slow'] = df['close'].rolling(30).mean()

# Find crossovers
df['cross_up'] = (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1)) & (df['sma_fast'] > df['sma_slow'])
df['cross_down'] = (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1)) & (df['sma_fast'] < df['sma_slow'])

crossovers = df[df['cross_up'] | df['cross_down']]

print(f"Total bars: {len(df)}")
print(f"Golden crosses (BUY): {df['cross_up'].sum()}")
print(f"Death crosses (SELL): {df['cross_down'].sum()}")
print(f"\nFirst 5 crossovers:")
print(crossovers[['time', 'close', 'sma_fast', 'sma_slow', 'cross_up', 'cross_down']].head())

mt5.shutdown()
