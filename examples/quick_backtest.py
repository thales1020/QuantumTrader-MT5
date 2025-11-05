"""
Quick Start: Backtest với Architecture v2.0
===========================================

Minimal example để bắt đầu nhanh

Author: QuantumTrader Team
"""

from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5

from engines.base_backtest_engine import BaseStrategy, RealisticBacktestEngine
from engines.broker_simulator import BrokerConfig
from engines.performance_analyzer import PerformanceAnalyzer


# Simple Moving Average Crossover Strategy
class SMAStrategy(BaseStrategy):
    """Simple SMA crossover strategy for demo"""
    
    def __init__(self, fast_period=10, slow_period=30):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calculate SMAs
        data['sma_fast'] = data['close'].rolling(self.fast_period).mean()
        data['sma_slow'] = data['close'].rolling(self.slow_period).mean()
        
        # Generate signals
        data['signal'] = 0
        data.loc[data['sma_fast'] > data['sma_slow'], 'signal'] = 1  # BUY
        data.loc[data['sma_fast'] < data['sma_slow'], 'signal'] = -1  # SELL
        
        # Only signal on crossover
        data['prev_signal'] = data['signal'].shift(1)
        data.loc[data['signal'] == data['prev_signal'], 'signal'] = 0
        
        return data


# Quick backtest function
def quick_backtest(
    symbol='EURUSD',
    timeframe='H1', 
    start='2024-01-01',
    end='2024-12-31',
    balance=10000,
    lot_size=0.1
):
    """
    Quick backtest with default settings
    
    Usage:
        results = quick_backtest('EURUSD', 'H1', '2024-01-01', '2024-12-31')
    """
    
    # 1. Load data from MT5
    if not mt5.initialize():
        raise Exception("MT5 init failed")
    
    tf_map = {'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 
              'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
              'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4, 
              'D1': mt5.TIMEFRAME_D1}
    
    rates = mt5.copy_rates_range(
        symbol, 
        tf_map[timeframe],
        datetime.fromisoformat(start),
        datetime.fromisoformat(end)
    )
    
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)
    mt5.shutdown()
    
    print(f"✅ Loaded {len(data)} bars")
    
    # 2. Create strategy
    strategy = SMAStrategy(fast_period=10, slow_period=30)
    
    # 3. Create realistic broker config
    broker = BrokerConfig(
        spread_pips=1.5,
        commission_per_lot=7.0,
        swap_long_per_lot=-5.0,
        swap_short_per_lot=-5.0
    )
    
    # 4. Run backtest
    engine = RealisticBacktestEngine(
        strategy=strategy,
        data=data,
        symbol=symbol,
        initial_balance=balance,
        lot_size=lot_size,
        broker_config=broker
    )
    
    results = engine.run()
    
    # 5. Print results
    print("\n📊 RESULTS:")
    print(f"   Initial: ${balance:,.2f}")
    print(f"   Final:   ${results['final_balance']:,.2f}")
    print(f"   Profit:  ${results['final_balance'] - balance:,.2f}")
    print(f"   Return:  {((results['final_balance']/balance - 1) * 100):.2f}%")
    print(f"   Trades:  {len(results['trades'])}")
    
    # 6. Export to Excel
    analyzer = PerformanceAnalyzer()
    for trade in results['trades']:
        analyzer.add_trade(trade)
    
    filename = f"backtest_{symbol}_{timeframe}.xlsx"
    analyzer.export_to_excel(filename)
    print(f"\n💾 Exported to {filename}")
    
    return results


if __name__ == "__main__":
    # Quick test with broker-specific symbol
    quick_backtest(symbol='EURUSDm')  # ← Changed: Support broker naming
