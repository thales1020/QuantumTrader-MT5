"""
RSI Filter Plugin

Filters trading signals based on RSI (Relative Strength Index).
Only accepts BUY signals when RSI is oversold and SELL signals when overbought.
"""

import logging
from typing import Optional, Dict
import pandas as pd

try:
    import talib
except ImportError:
    talib = None

from core.plugin_system import BasePlugin

logger = logging.getLogger(__name__)


class RSIFilterPlugin(BasePlugin):
    """
    Filter signals using RSI indicator.
    
    Configuration:
        period: RSI calculation period (default: 14)
        oversold: Oversold threshold (default: 30)
        overbought: Overbought threshold (default: 70)
        boost_confidence: Whether to boost signal confidence (default: True)
    
    Example:
        >>> config = {'period': 14, 'oversold': 30, 'overbought': 70}
        >>> plugin = RSIFilterPlugin(config)
        >>> bot.plugin_manager.register(plugin)
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize RSI Filter Plugin.
        
        Args:
            config: Configuration dict
        """
        super().__init__(name="RSIFilter")
        
        if talib is None:
            raise ImportError("TA-Lib is required for RSIFilterPlugin. Install with: pip install TA-Lib")
        
        config = config or {}
        self.period = config.get('period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
        self.boost_confidence = config.get('boost_confidence', True)
        
        logger.info(f"RSI Filter configured: period={self.period}, oversold={self.oversold}, overbought={self.overbought}")
    
    @property
    def name(self) -> str:
        return "RSIFilter"
    
    def on_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add RSI indicator to dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with 'rsi' column added
        """
        if 'rsi' not in df.columns:
            df['rsi'] = talib.RSI(df['close'], timeperiod=self.period)
            logger.debug(f"Added RSI column (period={self.period})")
        
        return df
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """
        Filter signal based on RSI conditions.
        
        BUY signals: Only accept when RSI < oversold
        SELL signals: Only accept when RSI > overbought
        
        Args:
            signal: Trading signal dict
            df: DataFrame with market data
            
        Returns:
            Modified signal or None to reject
        """
        if signal is None:
            return None
        
        # Get current RSI value
        rsi = df['rsi'].iloc[-1]
        
        if pd.isna(rsi):
            logger.warning("RSI is NaN, rejecting signal")
            return None
        
        signal_type = signal.get('type')
        
        if signal_type == 'BUY':
            # Only accept BUY when oversold
            if rsi < self.oversold:
                if self.boost_confidence and 'confidence' in signal:
                    # Boost confidence for strong oversold
                    if rsi < self.oversold - 10:
                        signal['confidence'] += 15
                        logger.info(f"Strong oversold BUY signal (RSI={rsi:.1f}), confidence boosted")
                    else:
                        signal['confidence'] += 10
                
                logger.info(f"Accepted BUY signal (RSI={rsi:.1f} < {self.oversold})")
                return signal
            else:
                logger.info(f"Rejected BUY signal (RSI={rsi:.1f} >= {self.oversold})")
                return None
        
        elif signal_type == 'SELL':
            # Only accept SELL when overbought
            if rsi > self.overbought:
                if self.boost_confidence and 'confidence' in signal:
                    # Boost confidence for strong overbought
                    if rsi > self.overbought + 10:
                        signal['confidence'] += 15
                        logger.info(f"Strong overbought SELL signal (RSI={rsi:.1f}), confidence boosted")
                    else:
                        signal['confidence'] += 10
                
                logger.info(f"Accepted SELL signal (RSI={rsi:.1f} > {self.overbought})")
                return signal
            else:
                logger.info(f"Rejected SELL signal (RSI={rsi:.1f} <= {self.overbought})")
                return None
        
        # Unknown signal type, pass through
        return signal
