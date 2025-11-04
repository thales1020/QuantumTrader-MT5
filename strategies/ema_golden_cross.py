"""
EMA Golden Cross - EMA Golden Cross trading strategy

Template: MA Crossover
Generated: 2025-11-04 19:30:29
Author: QuantumTrader
Version: 1.0.0

Strategy Logic:
- Buy Signal: Fast MA crosses above Slow MA
- Sell Signal: Fast MA crosses below Slow MA
- Exit: Opposite crossover or stop loss

Parameters:
- Fast MA Period: 50
- Slow MA Period: 200
- MA Type: EMA
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import talib
import pandas as pd
from typing import Dict, Optional
import MetaTrader5 as mt5


@StrategyRegistry.register("ema_golden_cross")
class EmaGoldenCross(BaseTradingBot):
    """
    EMA Golden Cross trading strategy
    
    Indicators:
    - Fast MA (EMA): 50 periods
    - Slow MA (EMA): 200 periods
    
    Entry Rules:
    - BUY: Fast MA crosses above Slow MA
    - SELL: Fast MA crosses below Slow MA
    
    Exit Rules:
    - Opposite crossover occurs
    - Stop loss hit
    - Take profit hit
    """
    
    def __init__(self, config: Dict):
        """
        Initialize MA Crossover Strategy
        
        Args:
            config: Strategy configuration dictionary
        """
        super().__init__(config)
        
        # Strategy parameters
        self.fast_period = config.get('fast_period', 50)
        self.slow_period = config.get('slow_period', 200)
        self.ma_type = config.get('ma_type', 'EMA')
        
        # Validate parameters
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
        self.logger.info(f"Fast MA: {self.ma_type}{self.fast_period}")
        self.logger.info(f"Slow MA: {self.ma_type}{self.slow_period}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        if len(df) < self.slow_period:
            self.logger.warning(f"Insufficient data: {len(df)} < {self.slow_period}")
            return df
        
        # Calculate moving averages based on type
        if self.ma_type == 'SMA':
            df['ma_fast'] = talib.SMA(df['close'], timeperiod=self.fast_period)
            df['ma_slow'] = talib.SMA(df['close'], timeperiod=self.slow_period)
        elif self.ma_type == 'EMA':
            df['ma_fast'] = talib.EMA(df['close'], timeperiod=self.fast_period)
            df['ma_slow'] = talib.EMA(df['close'], timeperiod=self.slow_period)
        elif self.ma_type == 'WMA':
            df['ma_fast'] = talib.WMA(df['close'], timeperiod=self.fast_period)
            df['ma_slow'] = talib.WMA(df['close'], timeperiod=self.slow_period)
        else:
            # Default to SMA if unknown type
            self.logger.warning(f"Unknown MA type: {self.ma_type}, using SMA")
            df['ma_fast'] = talib.SMA(df['close'], timeperiod=self.fast_period)
            df['ma_slow'] = talib.SMA(df['close'], timeperiod=self.slow_period)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on MA crossover
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            Signal dictionary or None
        """
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        # Need at least 2 bars to detect crossover
        if len(df) < 2:
            return None
        
        # Get current and previous values
        current_fast = df['ma_fast'].iloc[-1]
        current_slow = df['ma_slow'].iloc[-1]
        prev_fast = df['ma_fast'].iloc[-2]
        prev_slow = df['ma_slow'].iloc[-2]
        
        # Check for NaN
        if pd.isna([current_fast, current_slow, prev_fast, prev_slow]).any():
            return None
        
        # Detect crossover
        bullish_cross = prev_fast <= prev_slow and current_fast > current_slow
        bearish_cross = prev_fast >= prev_slow and current_fast < current_slow
        
        # Generate signal
        if bullish_cross:
            signal = {
                'type': 'BUY',
                'price': df['close'].iloc[-1],
                'time': df['time'].iloc[-1] if 'time' in df.columns else pd.Timestamp.now(),
                'ma_fast': current_fast,
                'ma_slow': current_slow,
                'reason': f'{self.ma_type}{self.fast_period} crossed above {self.ma_type}{self.slow_period}'
            }
            self.logger.info(f"📈 BUY Signal: {signal['reason']}")
            return signal
            
        elif bearish_cross:
            signal = {
                'type': 'SELL',
                'price': df['close'].iloc[-1],
                'time': df['time'].iloc[-1] if 'time' in df.columns else pd.Timestamp.now(),
                'ma_fast': current_fast,
                'ma_slow': current_slow,
                'reason': f'{self.ma_type}{self.fast_period} crossed below {self.ma_type}{self.slow_period}'
            }
            self.logger.info(f"📉 SELL Signal: {signal['reason']}")
            return signal
        
        return None
    
    def should_close_position(self, df: pd.DataFrame, position_type: str) -> bool:
        """
        Check if current position should be closed
        
        Args:
            df: DataFrame with OHLCV and indicator data
            position_type: 'BUY' or 'SELL'
            
        Returns:
            True if position should be closed
        """
        # Calculate indicators
        df = self.calculate_indicators(df)
        
        if len(df) < 2:
            return False
        
        # Get current and previous values
        current_fast = df['ma_fast'].iloc[-1]
        current_slow = df['ma_slow'].iloc[-1]
        prev_fast = df['ma_fast'].iloc[-2]
        prev_slow = df['ma_slow'].iloc[-2]
        
        # Check for NaN
        if pd.isna([current_fast, current_slow, prev_fast, prev_slow]).any():
            return False
        
        # Detect opposite crossover
        if position_type == 'BUY':
            # Close long if bearish crossover
            return prev_fast >= prev_slow and current_fast < current_slow
        else:
            # Close short if bullish crossover
            return prev_fast <= prev_slow and current_fast > current_slow
    
    def get_strategy_info(self) -> Dict:
        """
        Get strategy information
        
        Returns:
            Dictionary with strategy details
        """
        return {
            'name': 'EMA Golden Cross',
            'class': 'EmaGoldenCross',
            'id': 'ema_golden_cross',
            'description': 'EMA Golden Cross trading strategy',
            'type': 'Trend Following',
            'difficulty': 'Beginner',
            'parameters': {
                'fast_period': self.fast_period,
                'slow_period': self.slow_period,
                'ma_type': self.ma_type
            },
            'template': 'ma_crossover',
            'version': '1.0.0',
            'author': 'QuantumTrader'
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    """
    Example usage of EmaGoldenCross
    """
    import json
    
    # Example configuration
    config = {
        'symbol': 'EURUSD',
        'timeframe': 'M15',
        'fast_period': 50,
        'slow_period': 200,
        'ma_type': 'EMA',
        'risk_percent': 1.0,
        'magic_number': 123456
    }
    
    print("=" * 60)
    print("EMA Golden Cross - Example")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    print("=" * 60)
    
    # Initialize strategy
    bot = EmaGoldenCross(config)
    
    # Display strategy info
    info = bot.get_strategy_info()
    print("\nStrategy Info:")
    print(json.dumps(info, indent=2))
