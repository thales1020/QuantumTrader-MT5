"""
EURUSD Breakout - EURUSD Breakout trading strategy

Template: Breakout Strategy
Generated: 2025-11-04 19:59:33
Author: QuantumTrader
Version: 1.0.0

Strategy Logic:
- Buy when price breaks above Bollinger upper band with volume
- Sell when price breaks below Bollinger lower band with volume
- Exit with trailing stop based on ATR or time limit

Parameters:
- BB Period: 15
- BB Std Dev: 2.0
- Volume Multiplier: 1.5
- Trailing ATR: 2.0
- Max Bars: 50
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import talib
import pandas as pd
from typing import Dict, Optional
import MetaTrader5 as mt5


@StrategyRegistry.register("eurusd_breakout")
class EurusdBreakout(BaseTradingBot):
    """
    EURUSD Breakout trading strategy
    
    Indicators:
    - Bollinger Bands: 15 period, 2.0 std dev
    - Volume SMA: 15 period
    - ATR: 14 period
    
    Entry Rules:
    - BUY: Close > Upper BB AND Volume > 1.5x Average
    - SELL: Close < Lower BB AND Volume > 1.5x Average
    
    Exit Rules:
    - Trailing stop: 2.0x ATR
    - Time limit: 50 bars
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        self.bb_period = config.get('bb_period', 15)
        self.bb_std = config.get('bb_std', 2.0)
        self.volume_mult = config.get('volume_multiplier', 1.5)
        self.trailing_atr = config.get('trailing_atr', 2.0)
        self.max_bars = config.get('max_bars', 50)
        self.atr_period = config.get('atr_period', 14)
        
        # Track entry bar for time-based exit
        self.entry_bar_time = None
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
        self.logger.info(f"BB: {self.bb_period} period, {self.bb_std} std")
        self.logger.info(f"Volume filter: {self.volume_mult}x average")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if len(df) < self.bb_period:
            return df
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            df['close'],
            timeperiod=self.bb_period,
            nbdevup=self.bb_std,
            nbdevdn=self.bb_std,
            matype=0
        )
        
        # Volume average
        df['vol_sma'] = talib.SMA(df['tick_volume' if 'tick_volume' in df.columns else 'volume'],
                                    timeperiod=self.bb_period)
        
        # ATR for trailing stop
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.atr_period)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        df = self.calculate_indicators(df)
        
        if len(df) < 2:
            return None
        
        # Current values
        close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        volume = df['tick_volume' if 'tick_volume' in df.columns else 'volume'].iloc[-1]
        vol_avg = df['vol_sma'].iloc[-1]
        atr = df['atr'].iloc[-1]
        
        if pd.isna([bb_upper, bb_lower, vol_avg, atr]).any():
            return None
        
        # Volume confirmation
        volume_confirmed = volume > vol_avg * self.volume_mult
        
        # Bullish breakout: Close above upper band
        if close > bb_upper and prev_close <= bb_upper and volume_confirmed:
            signal = {
                'type': 'BUY',
                'price': close,
                'time': df['time'].iloc[-1] if 'time' in df.columns else pd.Timestamp.now(),
                'bb_upper': bb_upper,
                'volume': volume,
                'vol_avg': vol_avg,
                'atr': atr,
                'stop_loss': close - (atr * self.trailing_atr),
                'reason': f'Bullish breakout above BB (vol: {volume/vol_avg:.1f}x)'
            }
            
            self.entry_bar_time = signal['time']
            self.logger.info(f"📈 BUY Signal: {signal['reason']}")
            return signal
        
        # Bearish breakout: Close below lower band
        elif close < bb_lower and prev_close >= bb_lower and volume_confirmed:
            signal = {
                'type': 'SELL',
                'price': close,
                'time': df['time'].iloc[-1] if 'time' in df.columns else pd.Timestamp.now(),
                'bb_lower': bb_lower,
                'volume': volume,
                'vol_avg': vol_avg,
                'atr': atr,
                'stop_loss': close + (atr * self.trailing_atr),
                'reason': f'Bearish breakout below BB (vol: {volume/vol_avg:.1f}x)'
            }
            
            self.entry_bar_time = signal['time']
            self.logger.info(f"📉 SELL Signal: {signal['reason']}")
            return signal
        
        return None
    
    def should_close_position(self, df: pd.DataFrame, position_type: str) -> bool:
        """Close on time limit or when price returns to BB middle"""
        if self.entry_bar_time is None:
            return False
        
        df = self.calculate_indicators(df)
        
        if len(df) < 1:
            return False
        
        current_time = df['time'].iloc[-1] if 'time' in df.columns else pd.Timestamp.now()
        
        # Time-based exit
        bars_held = len(df[df['time'] >= self.entry_bar_time]) if 'time' in df.columns else 0
        if bars_held >= self.max_bars:
            self.logger.info(f"Closing: Time limit reached ({bars_held} bars)")
            self.entry_bar_time = None
            return True
        
        # Price returns to middle band (breakout failed)
        close = df['close'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        
        if pd.isna(bb_middle):
            return False
        
        if position_type == 'BUY' and close < bb_middle:
            self.logger.info("Closing BUY: Price returned to BB middle")
            self.entry_bar_time = None
            return True
        elif position_type == 'SELL' and close > bb_middle:
            self.logger.info("Closing SELL: Price returned to BB middle")
            self.entry_bar_time = None
            return True
        
        return False
    
    def get_strategy_info(self) -> Dict:
        return {
            'name': 'EURUSD Breakout',
            'class': 'EurusdBreakout',
            'id': 'eurusd_breakout',
            'description': 'EURUSD Breakout trading strategy',
            'type': 'Breakout',
            'difficulty': 'Intermediate',
            'parameters': {
                'bb_period': self.bb_period,
                'bb_std': self.bb_std,
                'volume_multiplier': self.volume_mult,
                'trailing_atr': self.trailing_atr,
                'max_bars': self.max_bars
            },
            'template': 'breakout',
            'version': '1.0.0',
            'author': 'QuantumTrader'
        }
