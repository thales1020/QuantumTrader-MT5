"""
Volume Filter Plugin

Filters trading signals based on volume analysis.
Rejects signals with volume below average and boosts confidence for high volume.
"""

import logging
from typing import Optional, Dict
import pandas as pd

from core.plugin_system import BasePlugin

logger = logging.getLogger(__name__)


class VolumeFilterPlugin(BasePlugin):
    """
    Filter signals using volume analysis.
    
    Configuration:
        multiplier: Minimum volume multiplier vs average (default: 1.5)
        period: Period for volume moving average (default: 20)
        boost_confidence: Boost confidence for high volume (default: True)
    
    Example:
        >>> config = {'multiplier': 1.5, 'period': 20}
        >>> plugin = VolumeFilterPlugin(config)
        >>> bot.plugin_manager.register(plugin)
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize Volume Filter Plugin.
        
        Args:
            config: Configuration dict
        """
        super().__init__(name="VolumeFilter")
        
        config = config or {}
        self.multiplier = config.get('multiplier', 1.5)
        self.period = config.get('period', 20)
        self.boost_confidence = config.get('boost_confidence', True)
        
        logger.info(f"Volume Filter configured: multiplier={self.multiplier}x, period={self.period}")
    
    @property
    def name(self) -> str:
        return "VolumeFilter"
    
    def on_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add average volume column to dataframe.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with 'avg_volume' column added
        """
        # Determine volume column name
        if 'tick_volume' in df.columns:
            volume_col = 'tick_volume'
        elif 'volume' in df.columns:
            volume_col = 'volume'
        else:
            return df
        
        # Add average volume column
        if 'avg_volume' not in df.columns:
            df['avg_volume'] = df[volume_col].rolling(window=self.period).mean()
            logger.debug(f"Added avg_volume column (period={self.period})")
        
        return df
    
    def on_signal(self, signal: Optional[Dict], df: pd.DataFrame) -> Optional[Dict]:
        """
        Filter signal based on volume.
        
        Rejects signals where volume < average volume * multiplier.
        Boosts confidence when volume is significantly higher.
        
        Args:
            signal: Trading signal dict
            df: DataFrame with market data
            
        Returns:
            Modified signal or None to reject
        """
        if signal is None:
            return None
        
        # Calculate average volume
        if 'tick_volume' in df.columns:
            volume_col = 'tick_volume'
        elif 'volume' in df.columns:
            volume_col = 'volume'
        else:
            logger.warning("No volume column found, passing signal through")
            return signal
        
        avg_volume = df[volume_col].rolling(window=self.period).mean().iloc[-1]
        current_volume = df[volume_col].iloc[-1]
        
        if pd.isna(avg_volume) or pd.isna(current_volume):
            logger.warning("Volume data is NaN, passing signal through")
            return signal
        
        volume_ratio = current_volume / avg_volume
        
        # Reject low volume signals
        if volume_ratio < self.multiplier:
            logger.info(f"Rejected signal due to low volume (ratio={volume_ratio:.2f}x < {self.multiplier}x)")
            return None
        
        # Boost confidence for high volume
        if self.boost_confidence and 'confidence' in signal:
            if volume_ratio >= self.multiplier * 2:
                # Very high volume
                signal['confidence'] += 20
                logger.info(f"Very high volume (ratio={volume_ratio:.2f}x), confidence boosted +20")
            elif volume_ratio >= self.multiplier * 1.5:
                # High volume
                signal['confidence'] += 10
                logger.info(f"High volume (ratio={volume_ratio:.2f}x), confidence boosted +10")
        
        logger.info(f"Accepted signal with volume ratio {volume_ratio:.2f}x")
        return signal
