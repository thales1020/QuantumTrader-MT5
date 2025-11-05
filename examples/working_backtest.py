"""
Simple Working Backtest Example - Fixed Interface
==================================================

Minimal working example với BaseStrategy interface đúng

Author: QuantumTrader Team
"""

from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
from typing import Dict, Optional
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from engines.base_backtest_engine import BaseStrategy, BaseBacktestEngine
from engines.broker_simulator import BrokerConfig


class SimpleSMAStrategy(BaseStrategy):
    """Simple SMA Crossover - Implements BaseStrategy correctly"""
    
    def __init__(self, fast=10, slow=30):
        super().__init__()
        self.fast = fast
        self.slow = slow
        self.data_prepared = None
    
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMAs - Required by BaseStrategy"""
        data['sma_fast'] = data['close'].rolling(self.fast).mean()
        data['sma_slow'] = data['close'].rolling(self.slow).mean()
        self.data_prepared = data
        return data
    
    def analyze(self, data: pd.DataFrame, current_bar: Dict) -> Optional[Dict]:
        """Generate signal - Required by BaseStrategy"""
        
        # Use prepared data
        if self.data_prepared is None:
            self.data_prepared = self.prepare_data(data)
        
        df = self.data_prepared
        
        # Get current timestamp
        current_time = pd.to_datetime(current_bar['time'], unit='s')
        if current_time not in df.index:
            return None
        
        idx = df.index.get_loc(current_time)
        
        # Need enough history
        if idx < self.slow:
            return None
        
        # Current and previous SMAs
        sma_fast_now = df['sma_fast'].iloc[idx]
        sma_slow_now = df['sma_slow'].iloc[idx]
        sma_fast_prev = df['sma_fast'].iloc[idx-1]
        sma_slow_prev = df['sma_slow'].iloc[idx-1]
        
        # Debug first few bars
        if idx < 100 and idx % 10 == 0:
            print(f"Bar {idx}: Fast={sma_fast_now:.5f} Slow={sma_slow_now:.5f}")
        
        # Check for crossover
        # BUY: Fast crosses above Slow
        if sma_fast_prev <= sma_slow_prev and sma_fast_now > sma_slow_now:
            atr = df['high'].iloc[idx-14:idx].max() - df['low'].iloc[idx-14:idx].min()
            print(f"🟢 BUY SIGNAL at {current_time}")
            return {
                'action': 'BUY',
                'lot_size': 0.1,
                'stop_loss': current_bar['close'] - (atr * 1.5),
                'take_profit': current_bar['close'] + (atr * 2.0),
                'reason': 'SMA Golden Cross'
            }
        
        # SELL: Fast crosses below Slow
        elif sma_fast_prev >= sma_slow_prev and sma_fast_now < sma_slow_now:
            atr = df['high'].iloc[idx-14:idx].max() - df['low'].iloc[idx-14:idx].min()
            print(f"🔴 SELL SIGNAL at {current_time}")
            return {
                'action': 'SELL',
                'lot_size': 0.1,
                'stop_loss': current_bar['close'] + (atr * 1.5),
                'take_profit': current_bar['close'] - (atr * 2.0),
                'reason': 'SMA Death Cross'
            }
        
        return None


def run_simple_backtest():
    """Run backtest with working strategy"""
    
    print("="*70)
    print("SIMPLE SMA BACKTEST - Architecture v2.0")
    print("="*70)
    
    # Config
    SYMBOL = 'AUDUSDm'         # ← Changed to AUDUSD
    START = datetime(2020, 1, 1)   # ← From 2020
    END = datetime(2025, 11, 5)    # Today
    
    print(f"\n📊 Symbol: {SYMBOL}")
    print(f"   Period: {START.date()} to {END.date()}")
    
    # Initialize MT5
    if not mt5.initialize():
        raise Exception("MT5 init failed")
    
    # Create strategy
    print("\n🎯 Creating SMA strategy...")
    strategy = SimpleSMAStrategy(fast=10, slow=30)
    print("   Fast SMA: 10")
    print("   Slow SMA: 30")
    
    # Broker config
    print("\n💰 Broker config...")
    broker = BrokerConfig(
        spread_pips=1.5,
        commission_per_lot=7.0,
        swap_long=-5.0,
        swap_short=-5.0,
        slippage_pips_max=2.0,
        rejection_probability=0.01
    )
    print("   Spread: 1.5 pips")
    print("   Commission: $7/lot")
    print("   Swap: -$5/lot/day")
    
    # Run backtest
    print("\n⚙️  Running backtest...\n")
    engine = BaseBacktestEngine(
        strategy=strategy,
        broker_config=broker,
        initial_balance=10000
    )
    
    metrics = engine.run_backtest(
        symbol=SYMBOL,
        start_date=START,
        end_date=END,
        timeframe=mt5.TIMEFRAME_H1,
        export_excel=True
    )
    
    print("\n" + "="*70)
    print("✅ BACKTEST COMPLETE!")
    print("="*70)
    print("\n💡 Check reports/ folder for Excel file")
    
    mt5.shutdown()
    return metrics


if __name__ == "__main__":
    run_simple_backtest()
