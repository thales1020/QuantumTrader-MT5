"""
Custom Indicator Integration Example

This example shows how to create and integrate custom indicators
that are not available in TA-Lib.

Custom Indicators Demonstrated:
1. Ichimoku Cloud (popular Japanese indicator)
2. Pivot Points (Support/Resistance levels)
3. VWAP (Volume Weighted Average Price)

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import MetaTrader5 as mt5
import talib
import pandas as pd
import numpy as np
from typing import Dict, Tuple


@StrategyRegistry.register("custom_indicators")
class CustomIndicatorStrategy(BaseTradingBot):
    """
    Strategy using custom technical indicators
    
    This demonstrates how to:
    - Implement indicators not in TA-Lib
    - Combine multiple custom indicators
    - Create complex entry/exit logic
    
    Indicators Used:
    - Ichimoku Cloud (trend and momentum)
    - Pivot Points (support/resistance)
    - VWAP (institutional price levels)
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Ichimoku parameters
        self.tenkan_period = config.get('tenkan_period', 9)
        self.kijun_period = config.get('kijun_period', 26)
        self.senkou_b_period = config.get('senkou_b_period', 52)
        
        # Risk parameters
        self.atr_period = config.get('atr_period', 14)
        self.sl_atr_mult = config.get('sl_atr_multiplier', 2.0)
        self.tp_atr_mult = config.get('tp_atr_multiplier', 3.0)
        
        self.logger.info("Initialized Custom Indicator Strategy")
        self.logger.info(f"Ichimoku: {self.tenkan_period}/{self.kijun_period}/{self.senkou_b_period}")
    
    def calculate_ichimoku(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Ichimoku Cloud indicator
        
        Components:
        - Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        - Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        - Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2, shifted 26 periods
        - Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, shifted 26
        - Chikou Span (Lagging Span): Close shifted back 26 periods
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with Ichimoku components
        """
        # Tenkan-sen (Conversion Line)
        high_tenkan = df['high'].rolling(window=self.tenkan_period).max()
        low_tenkan = df['low'].rolling(window=self.tenkan_period).min()
        df['tenkan_sen'] = (high_tenkan + low_tenkan) / 2
        
        # Kijun-sen (Base Line)
        high_kijun = df['high'].rolling(window=self.kijun_period).max()
        low_kijun = df['low'].rolling(window=self.kijun_period).min()
        df['kijun_sen'] = (high_kijun + low_kijun) / 2
        
        # Senkou Span A (Leading Span A)
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(self.kijun_period)
        
        # Senkou Span B (Leading Span B)
        high_senkou = df['high'].rolling(window=self.senkou_b_period).max()
        low_senkou = df['low'].rolling(window=self.senkou_b_period).min()
        df['senkou_span_b'] = ((high_senkou + low_senkou) / 2).shift(self.kijun_period)
        
        # Chikou Span (Lagging Span)
        df['chikou_span'] = df['close'].shift(-self.kijun_period)
        
        return df
    
    def calculate_pivot_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily Pivot Points
        
        Formulas:
        - Pivot Point (PP) = (High + Low + Close) / 3
        - Resistance 1 (R1) = 2*PP - Low
        - Support 1 (S1) = 2*PP - High
        - Resistance 2 (R2) = PP + (High - Low)
        - Support 2 (S2) = PP - (High - Low)
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with pivot levels
        """
        # Use previous day's OHLC for pivot calculation
        df['pivot'] = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        
        # Resistance levels
        df['r1'] = 2 * df['pivot'] - df['low'].shift(1)
        df['r2'] = df['pivot'] + (df['high'].shift(1) - df['low'].shift(1))
        
        # Support levels
        df['s1'] = 2 * df['pivot'] - df['high'].shift(1)
        df['s2'] = df['pivot'] - (df['high'].shift(1) - df['low'].shift(1))
        
        return df
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VWAP (Volume Weighted Average Price)
        
        VWAP = Cumulative(Typical Price * Volume) / Cumulative(Volume)
        Typical Price = (High + Low + Close) / 3
        
        Resets daily (for intraday timeframes)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with VWAP
        """
        # Calculate typical price
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        # For daily VWAP, we would reset cumsum at start of each day
        # This is a simplified version - cumulative since start
        df['vwap_numerator'] = (df['typical_price'] * df['tick_volume']).cumsum()
        df['vwap_denominator'] = df['tick_volume'].cumsum()
        df['vwap'] = df['vwap_numerator'] / df['vwap_denominator']
        
        # Clean up temporary columns
        df.drop(['vwap_numerator', 'vwap_denominator'], axis=1, inplace=True)
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators including custom ones
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            DataFrame with all indicators
        """
        # Custom indicators
        df = self.calculate_ichimoku(df)
        df = self.calculate_pivot_points(df)
        df = self.calculate_vwap(df)
        
        # Standard indicators
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.atr_period)
        
        return df
    
    def analyze_ichimoku_signal(self, df: pd.DataFrame) -> int:
        """
        Analyze Ichimoku Cloud for trading signal
        
        Bullish Conditions:
        - Price above cloud (Senkou Span A & B)
        - Tenkan-sen above Kijun-sen
        - Chikou Span above price (26 bars ago)
        
        Bearish Conditions:
        - Price below cloud
        - Tenkan-sen below Kijun-sen
        - Chikou Span below price (26 bars ago)
        
        Args:
            df: DataFrame with Ichimoku indicators
            
        Returns:
            1 for bullish, -1 for bearish, 0 for neutral
        """
        if len(df) < self.senkou_b_period + self.kijun_period:
            return 0
        
        # Get latest values
        idx = -1
        price = df['close'].iloc[idx]
        tenkan = df['tenkan_sen'].iloc[idx]
        kijun = df['kijun_sen'].iloc[idx]
        senkou_a = df['senkou_span_a'].iloc[idx]
        senkou_b = df['senkou_span_b'].iloc[idx]
        
        # Chikou span is shifted back, so we look at current close vs close 26 bars ago
        if len(df) >= self.kijun_period:
            price_26_ago = df['close'].iloc[-self.kijun_period]
        else:
            price_26_ago = price
        
        # Cloud top and bottom
        cloud_top = max(senkou_a, senkou_b) if not pd.isna(senkou_a) and not pd.isna(senkou_b) else price
        cloud_bottom = min(senkou_a, senkou_b) if not pd.isna(senkou_a) and not pd.isna(senkou_b) else price
        
        # Bullish signal
        bullish_conditions = [
            price > cloud_top,  # Price above cloud
            tenkan > kijun if not pd.isna(tenkan) and not pd.isna(kijun) else False,  # TK cross bullish
            price > price_26_ago,  # Chikou span above price
        ]
        
        # Bearish signal
        bearish_conditions = [
            price < cloud_bottom,  # Price below cloud
            tenkan < kijun if not pd.isna(tenkan) and not pd.isna(kijun) else False,  # TK cross bearish
            price < price_26_ago,  # Chikou span below price
        ]
        
        # Strong signal requires all conditions
        if all(bullish_conditions):
            return 1
        elif all(bearish_conditions):
            return -1
        
        return 0
    
    def analyze_pivot_support(self, df: pd.DataFrame, signal: int) -> bool:
        """
        Check if signal is supported by pivot levels
        
        Args:
            df: DataFrame with pivot points
            signal: Current signal (1 or -1)
            
        Returns:
            True if pivot levels confirm signal
        """
        if len(df) < 2:
            return False
        
        price = df['close'].iloc[-1]
        pivot = df['pivot'].iloc[-1]
        r1 = df['r1'].iloc[-1]
        s1 = df['s1'].iloc[-1]
        
        # Check for NaN values
        if pd.isna(pivot) or pd.isna(r1) or pd.isna(s1):
            return False
        
        # Buy signal confirmation: price near support
        if signal == 1:
            near_support = abs(price - s1) < abs(price - pivot)
            return near_support
        
        # Sell signal confirmation: price near resistance
        if signal == -1:
            near_resistance = abs(price - r1) < abs(price - pivot)
            return near_resistance
        
        return False
    
    def analyze_vwap_position(self, df: pd.DataFrame) -> int:
        """
        Analyze price position relative to VWAP
        
        Args:
            df: DataFrame with VWAP
            
        Returns:
            1 if price above VWAP, -1 if below, 0 if at VWAP
        """
        if len(df) < 2:
            return 0
        
        price = df['close'].iloc[-1]
        vwap = df['vwap'].iloc[-1]
        
        if pd.isna(vwap):
            return 0
        
        # Price significantly above VWAP (bullish)
        if price > vwap * 1.001:  # 0.1% threshold
            return 1
        
        # Price significantly below VWAP (bearish)
        if price < vwap * 0.999:
            return -1
        
        return 0
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        Generate trading signal combining all custom indicators
        
        Signal Requirements:
        1. Ichimoku shows clear trend
        2. Pivot points confirm direction
        3. Price aligned with VWAP
        
        Args:
            df: DataFrame with all indicators
            
        Returns:
            1 for buy, -1 for sell, 0 for no signal
        """
        # Get individual signals
        ichimoku_signal = self.analyze_ichimoku_signal(df)
        vwap_position = self.analyze_vwap_position(df)
        
        # No trade if Ichimoku is neutral
        if ichimoku_signal == 0:
            return 0
        
        # Check pivot confirmation
        pivot_confirmed = self.analyze_pivot_support(df, ichimoku_signal)
        
        # All indicators must align
        if ichimoku_signal == 1 and vwap_position >= 0 and pivot_confirmed:
            self.logger.info("BUY Signal: Ichimoku bullish + VWAP support + Pivot confirmation")
            return 1
        
        if ichimoku_signal == -1 and vwap_position <= 0 and pivot_confirmed:
            self.logger.info("SELL Signal: Ichimoku bearish + VWAP resistance + Pivot confirmation")
            return -1
        
        return 0
    
    def calculate_stop_loss(self, df: pd.DataFrame, signal: int, entry_price: float) -> float:
        """Calculate stop loss based on ATR"""
        current_atr = df['atr'].iloc[-1]
        sl_distance = current_atr * self.sl_atr_mult
        
        if signal == 1:
            sl_price = entry_price - sl_distance
        else:
            sl_price = entry_price + sl_distance
        
        return sl_price
    
    def calculate_take_profit(self, df: pd.DataFrame, signal: int, entry_price: float) -> float:
        """Calculate take profit based on ATR"""
        current_atr = df['atr'].iloc[-1]
        tp_distance = current_atr * self.tp_atr_mult
        
        if signal == 1:
            tp_price = entry_price + tp_distance
        else:
            tp_price = entry_price - tp_distance
        
        return tp_price
    
    def get_strategy_info(self) -> Dict:
        """Return strategy information"""
        return {
            'name': 'Custom Indicator Strategy',
            'id': 'custom_indicators',
            'version': '1.0.0',
            'description': 'Strategy using Ichimoku, Pivot Points, and VWAP',
            'indicators': {
                'ichimoku': f'Tenkan:{self.tenkan_period}, Kijun:{self.kijun_period}, Senkou B:{self.senkou_b_period}',
                'pivot_points': 'Daily levels',
                'vwap': 'Volume Weighted Average Price',
                'atr': f'{self.atr_period} period',
            }
        }


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'symbol': 'EURUSD',
        'timeframe': mt5.TIMEFRAME_H1,
        'risk_percent': 1.0,
        'tenkan_period': 9,
        'kijun_period': 26,
        'senkou_b_period': 52,
        'atr_period': 14,
        'sl_atr_multiplier': 2.0,
        'tp_atr_multiplier': 3.0,
        'magic_number': 100003,
    }
    
    # Initialize strategy
    bot = CustomIndicatorStrategy(config)
    
    # Print strategy info
    info = bot.get_strategy_info()
    print("\n" + "=" * 60)
    print(f"Strategy: {info['name']}")
    print("=" * 60)
    print(f"Version: {info['version']}")
    print(f"Description: {info['description']}")
    print(f"\nCustom Indicators:")
    for name, params in info['indicators'].items():
        print(f"  {name.replace('_', ' ').title()}: {params}")
    print("=" * 60 + "\n")
    
    # Example: Fetch data and calculate indicators
    print("Example: Calculating custom indicators...")
    print("-" * 60)
    
    # Would fetch real data in production
    # df = bot.fetch_data()
    # df = bot.calculate_indicators(df)
    # signal = bot.generate_signal(df)
    
    print("✅ Custom indicators implemented:")
    print("   1. Ichimoku Cloud (trend identification)")
    print("   2. Pivot Points (support/resistance)")
    print("   3. VWAP (institutional levels)")
    print("\n✅ All indicators can be combined for confluence trading")
    print("=" * 60 + "\n")
