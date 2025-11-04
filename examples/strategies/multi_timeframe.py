"""
Multi-Timeframe Strategy Example

This example demonstrates how to create a strategy that uses multiple timeframes
for confirmation. This is a common approach in professional trading.

Strategy Logic:
- Higher Timeframe (H1): Determine overall trend using EMA 200
- Lower Timeframe (M15): Find entry points using RSI
- Only take trades aligned with higher timeframe trend

Example:
    # Create config
    config = {
        'symbol': 'EURUSD',
        'lower_timeframe': 'M15',
        'higher_timeframe': 'H1',
        'rsi_period': 14,
        'ema_period': 200,
    }
    
    # Initialize and run
    bot = MultiTimeframeStrategy(config)
    bot.backtest(start_date='2024-01-01', end_date='2024-12-31')

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import MetaTrader5 as mt5
import talib
import pandas as pd
from typing import Dict, Optional
from datetime import datetime, timedelta


@StrategyRegistry.register("multi_timeframe")
class MultiTimeframeStrategy(BaseTradingBot):
    """
    Multi-Timeframe Strategy - Trade with trend confirmation
    
    This strategy combines:
    - H1 timeframe: Trend direction (EMA 200)
    - M15 timeframe: Entry signals (RSI oversold/overbought)
    
    Entry Rules:
    - BUY: H1 price > EMA200 AND M15 RSI < 30 (oversold in uptrend)
    - SELL: H1 price < EMA200 AND M15 RSI > 70 (overbought in downtrend)
    
    Risk Management:
    - Stop Loss: 2x ATR on entry timeframe
    - Take Profit: 3x ATR (Risk:Reward 1:1.5)
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Timeframe configuration
        self.lower_tf = config.get('lower_timeframe', mt5.TIMEFRAME_M15)
        self.higher_tf = config.get('higher_timeframe', mt5.TIMEFRAME_H1)
        
        # Indicator parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.ema_period = config.get('ema_period', 200)
        self.atr_period = config.get('atr_period', 14)
        
        # Risk management
        self.sl_atr_mult = config.get('sl_atr_multiplier', 2.0)
        self.tp_atr_mult = config.get('tp_atr_multiplier', 3.0)
        
        # Data storage
        self.higher_tf_data = None
        self.last_higher_tf_update = None
        
        self.logger.info(f"Initialized Multi-Timeframe Strategy")
        self.logger.info(f"Higher TF: {self._timeframe_to_string(self.higher_tf)}")
        self.logger.info(f"Lower TF: {self._timeframe_to_string(self.lower_tf)}")
        self.logger.info(f"EMA: {self.ema_period}, RSI: {self.rsi_period}")
    
    def _timeframe_to_string(self, timeframe) -> str:
        """Convert MT5 timeframe constant to string"""
        tf_map = {
            mt5.TIMEFRAME_M1: 'M1',
            mt5.TIMEFRAME_M5: 'M5',
            mt5.TIMEFRAME_M15: 'M15',
            mt5.TIMEFRAME_M30: 'M30',
            mt5.TIMEFRAME_H1: 'H1',
            mt5.TIMEFRAME_H4: 'H4',
            mt5.TIMEFRAME_D1: 'D1',
        }
        return tf_map.get(timeframe, str(timeframe))
    
    def fetch_higher_timeframe_data(self) -> pd.DataFrame:
        """
        Fetch data from higher timeframe for trend analysis
        
        Returns:
            DataFrame with OHLCV data and EMA indicator
        """
        # Fetch enough bars for EMA calculation
        bars_needed = self.ema_period + 50
        
        rates = mt5.copy_rates_from_pos(
            self.symbol,
            self.higher_tf,
            0,
            bars_needed
        )
        
        if rates is None or len(rates) == 0:
            self.logger.error("Failed to fetch higher timeframe data")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate trend indicator (EMA)
        df['ema'] = talib.EMA(df['close'], timeperiod=self.ema_period)
        
        # Determine trend: 1 = uptrend, -1 = downtrend, 0 = neutral
        df['trend'] = 0
        df.loc[df['close'] > df['ema'], 'trend'] = 1
        df.loc[df['close'] < df['ema'], 'trend'] = -1
        
        return df
    
    def get_current_trend(self) -> int:
        """
        Get current market trend from higher timeframe
        
        Returns:
            1 for uptrend, -1 for downtrend, 0 for neutral/unknown
        """
        # Update higher timeframe data every 15 minutes
        current_time = datetime.now()
        
        if (self.higher_tf_data is None or 
            self.last_higher_tf_update is None or
            (current_time - self.last_higher_tf_update).seconds > 900):
            
            self.higher_tf_data = self.fetch_higher_timeframe_data()
            self.last_higher_tf_update = current_time
            
            if self.higher_tf_data is None:
                return 0
        
        # Get latest trend value
        current_trend = self.higher_tf_data['trend'].iloc[-1]
        
        return int(current_trend)
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicators for lower timeframe (entry signals)
        
        Args:
            df: OHLCV data from lower timeframe
            
        Returns:
            DataFrame with RSI and ATR indicators
        """
        # RSI for entry signals
        df['rsi'] = talib.RSI(df['close'], timeperiod=self.rsi_period)
        
        # ATR for stop loss and take profit
        df['atr'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=self.atr_period
        )
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate trading signal using multi-timeframe analysis
        
        Strategy:
        1. Check higher timeframe trend
        2. If uptrend: Look for oversold RSI (buy signal)
        3. If downtrend: Look for overbought RSI (sell signal)
        4. No trend: No trade
        
        Args:
            df: DataFrame with lower timeframe data and indicators
            
        Returns:
            1 for buy, -1 for sell, 0 for no signal
        """
        if len(df) < 2:
            return 0
        
        # Get higher timeframe trend
        trend = self.get_current_trend()
        
        if trend == 0:
            self.logger.debug("No clear trend - no signal")
            return 0
        
        # Get latest RSI value
        current_rsi = df['rsi'].iloc[-1]
        
        # BUY Signal: Uptrend + Oversold RSI
        if trend == 1 and current_rsi < self.rsi_oversold:
            self.logger.info(f"BUY Signal: Uptrend + RSI oversold ({current_rsi:.2f})")
            return 1
        
        # SELL Signal: Downtrend + Overbought RSI
        if trend == -1 and current_rsi > self.rsi_overbought:
            self.logger.info(f"SELL Signal: Downtrend + RSI overbought ({current_rsi:.2f})")
            return -1
        
        return 0
    
    def calculate_position_size(self, df: pd.DataFrame, signal: int) -> float:
        """
        Calculate position size based on ATR and risk percentage
        
        Args:
            df: DataFrame with indicators
            signal: Trade direction (1 or -1)
            
        Returns:
            Position size in lots
        """
        if signal == 0:
            return 0.0
        
        # Get current ATR for risk calculation
        current_atr = df['atr'].iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Stop loss distance in price units
        sl_distance = current_atr * self.sl_atr_mult
        
        # Calculate risk amount in account currency
        account_balance = self.get_account_balance()
        risk_amount = account_balance * (self.risk_percent / 100)
        
        # Get symbol info for lot calculation
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            self.logger.error(f"Failed to get symbol info for {self.symbol}")
            return 0.01
        
        # Calculate position size
        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        
        # Position size = Risk Amount / (SL Distance / Tick Size * Tick Value)
        position_size = risk_amount / (sl_distance / tick_size * tick_value)
        
        # Round to symbol's volume step
        volume_step = symbol_info.volume_step
        position_size = round(position_size / volume_step) * volume_step
        
        # Ensure within limits
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max
        position_size = max(min_volume, min(position_size, max_volume))
        
        self.logger.info(f"Position size: {position_size} lots (Risk: ${risk_amount:.2f}, SL: {sl_distance:.5f})")
        
        return position_size
    
    def calculate_stop_loss(self, df: pd.DataFrame, signal: int, entry_price: float) -> float:
        """
        Calculate stop loss based on ATR
        
        Args:
            df: DataFrame with ATR
            signal: Trade direction (1 or -1)
            entry_price: Entry price
            
        Returns:
            Stop loss price
        """
        current_atr = df['atr'].iloc[-1]
        sl_distance = current_atr * self.sl_atr_mult
        
        if signal == 1:  # Long position
            sl_price = entry_price - sl_distance
        else:  # Short position
            sl_price = entry_price + sl_distance
        
        return sl_price
    
    def calculate_take_profit(self, df: pd.DataFrame, signal: int, entry_price: float) -> float:
        """
        Calculate take profit based on ATR
        
        Args:
            df: DataFrame with ATR
            signal: Trade direction (1 or -1)
            entry_price: Entry price
            
        Returns:
            Take profit price
        """
        current_atr = df['atr'].iloc[-1]
        tp_distance = current_atr * self.tp_atr_mult
        
        if signal == 1:  # Long position
            tp_price = entry_price + tp_distance
        else:  # Short position
            tp_price = entry_price - tp_distance
        
        return tp_price
    
    def get_strategy_info(self) -> Dict:
        """Return strategy information"""
        return {
            'name': 'Multi-Timeframe Strategy',
            'id': 'multi_timeframe',
            'version': '1.0.0',
            'description': 'Trend following with multi-timeframe confirmation',
            'timeframes': {
                'higher': self._timeframe_to_string(self.higher_tf),
                'lower': self._timeframe_to_string(self.lower_tf),
            },
            'indicators': {
                'trend': f'EMA {self.ema_period}',
                'entry': f'RSI {self.rsi_period}',
                'risk': f'ATR {self.atr_period}',
            }
        }


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'symbol': 'EURUSD',
        'timeframe': 'M15',  # Entry timeframe
        'lower_timeframe': mt5.TIMEFRAME_M15,
        'higher_timeframe': mt5.TIMEFRAME_H1,
        'risk_percent': 1.0,
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'ema_period': 200,
        'atr_period': 14,
        'sl_atr_multiplier': 2.0,
        'tp_atr_multiplier': 3.0,
        'magic_number': 100001,
    }
    
    # Initialize strategy
    bot = MultiTimeframeStrategy(config)
    
    # Print strategy info
    info = bot.get_strategy_info()
    print("\n" + "=" * 60)
    print(f"Strategy: {info['name']}")
    print("=" * 60)
    print(f"Version: {info['version']}")
    print(f"Description: {info['description']}")
    print(f"\nTimeframes:")
    print(f"  Higher (Trend): {info['timeframes']['higher']}")
    print(f"  Lower (Entry): {info['timeframes']['lower']}")
    print(f"\nIndicators:")
    for key, value in info['indicators'].items():
        print(f"  {key.title()}: {value}")
    print("=" * 60 + "\n")
    
    # Run backtest (if needed)
    # bot.backtest(start_date='2024-01-01', end_date='2024-12-31')
