"""
ICT (Inner Circle Trader) Bot - Refactored Version
Inherits from BaseTradingBot for improved architecture

This version uses:
- BaseTradingBot abstract class
- Template method pattern
- Hook system for extensibility
- Proper separation of concerns
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import warnings

from core.base_bot import BaseTradingBot, BaseConfig

warnings.filterwarnings('ignore')


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class OrderBlock:
    """Represents an ICT Order Block"""
    price_high: float
    price_low: float
    direction: str  # 'bullish' or 'bearish'
    time: datetime
    strength: float  # 0-100
    

@dataclass
class FairValueGap:
    """Represents an ICT Fair Value Gap (FVG)"""
    top: float
    bottom: float
    direction: str  # 'bullish' or 'bearish'
    time: datetime
    filled: bool = False


@dataclass
class ICTConfig(BaseConfig):
    """
    Configuration for ICT Bot - extends base BaseConfig
    """
    # ICT-specific parameters
    lookback_candles: int = 20  # For Order Blocks
    fvg_min_size: float = 0.0005  # Minimum FVG size
    liquidity_sweep_pips: float = 5.0  # Pips for liquidity sweep detection
    
    # Feature toggles
    use_market_structure: bool = True  # Use BOS/CHoCH
    use_order_blocks: bool = True
    use_fvg: bool = True
    use_liquidity_sweeps: bool = True
    
    # Risk management
    move_sl_to_breakeven: bool = True  # Move SL to BE when Order 1 hits TP


# ============================================================================
# ICT BOT CLASS
# ============================================================================

class ICTBot(BaseTradingBot):
    """
    ICT (Inner Circle Trader) Strategy Bot
    
    Implements Smart Money Concepts:
    - Order Blocks (OB)
    - Fair Value Gaps (FVG)
    - Break of Structure (BOS)
    - Change of Character (CHoCH)
    - Liquidity Sweeps
    - Market Structure (HH, HL, LH, LL)
    
    Inherits from BaseTradingBot for:
    - Connection management
    - Position sizing
    - Risk management
    - Trading execution
    - Hooks & events
    """
    
    def __init__(self, config: ICTConfig):
        """Initialize ICT Bot with specific configuration"""
        super().__init__(config)
        
        # ICT-specific state
        self.order_blocks: List[OrderBlock] = []
        self.fair_value_gaps: List[FairValueGap] = []
        self.market_structure: Dict = {
            'highs': [],
            'lows': [],
            'trend': 'neutral',
            'last_high': None,
            'last_low': None
        }
        
        self.logger.info("ICT Bot initialized with Smart Money Concepts")
    
    # ========================================================================
    # ABSTRACT METHODS IMPLEMENTATION (Required by BaseTradingBot)
    # ========================================================================
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ICT-specific indicators
        
        Required by BaseTradingBot abstract method
        """
        if df is None or len(df) < 20:
            return df
        
        # Market Structure Analysis
        if self.config.use_market_structure:
            self.identify_market_structure(df)
        
        # Order Blocks
        if self.config.use_order_blocks:
            self.order_blocks = self.identify_order_blocks(df)
            self.logger.info(f"Identified {len(self.order_blocks)} order blocks")
        
        # Fair Value Gaps
        if self.config.use_fvg:
            self.fair_value_gaps = self.identify_fair_value_gaps(df)
            active_fvgs = [fvg for fvg in self.fair_value_gaps if not fvg.filled]
            self.logger.info(f"Identified {len(active_fvgs)} active FVGs")
        
        # Add ATR for volatility
        df = self._add_atr(df)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on ICT concepts
        
        Required by BaseTradingBot abstract method
        
        Returns:
            Dict with signal data or None
            Format: {
                'type': 'BUY' or 'SELL',
                'price': float,
                'confidence': float (0-100),
                'reason': str,
                'metadata': dict with ICT-specific data
            }
        """
        if df is None or len(df) < 50:
            return None
        
        current_price = df['close'].iloc[-1]
        signal_type = None
        confidence = 0.0
        metadata = {}
        
        # Check liquidity sweeps
        liquidity_sweep = None
        if self.config.use_liquidity_sweeps:
            liquidity_sweep = self.detect_liquidity_sweep(df)
        
        # =====================================================================
        # BULLISH SIGNAL LOGIC
        # =====================================================================
        if self._check_bullish_setup(df, current_price, liquidity_sweep):
            signal_type = 'BUY'
            confidence = self._calculate_signal_confidence(df, 'bullish')
            
            # Find best Order Block for entry
            best_ob = self._find_best_order_block('bullish', current_price)
            
            # Find best FVG
            best_fvg = self._find_best_fvg('bullish', current_price)
            
            metadata = {
                'order_block': best_ob,
                'fvg': best_fvg,
                'liquidity_sweep': liquidity_sweep,
                'market_structure': self.market_structure.copy(),
                'setup_type': 'ICT_BULLISH'
            }
            
            reason = f"ICT Bullish: MS={self.market_structure.get('trend')}, " \
                    f"OB={'Yes' if best_ob else 'No'}, FVG={'Yes' if best_fvg else 'No'}"
            
            self.logger.info(f"🟢 BULLISH Signal | Confidence: {confidence:.1f}% | "
                           f"OB: {best_ob is not None} | FVG: {best_fvg is not None}")
        
        # =====================================================================
        # BEARISH SIGNAL LOGIC
        # =====================================================================
        elif self._check_bearish_setup(df, current_price, liquidity_sweep):
            signal_type = 'SELL'
            confidence = self._calculate_signal_confidence(df, 'bearish')
            
            # Find best Order Block for entry
            best_ob = self._find_best_order_block('bearish', current_price)
            
            # Find best FVG
            best_fvg = self._find_best_fvg('bearish', current_price)
            
            metadata = {
                'order_block': best_ob,
                'fvg': best_fvg,
                'liquidity_sweep': liquidity_sweep,
                'market_structure': self.market_structure.copy(),
                'setup_type': 'ICT_BEARISH'
            }
            
            reason = f"ICT Bearish: MS={self.market_structure.get('trend')}, " \
                    f"OB={'Yes' if best_ob else 'No'}, FVG={'Yes' if best_fvg else 'No'}"
            
            self.logger.info(f"🔴 BEARISH Signal | Confidence: {confidence:.1f}% | "
                           f"OB: {best_ob is not None} | FVG: {best_fvg is not None}")
        
        # Return signal dict if we have a valid signal
        if signal_type:
            # Calculate stop loss and take profit
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else self._calculate_atr_value(df)
            
            if signal_type == 'BUY':
                # SL below order block or recent swing low
                best_ob = metadata.get('order_block')
                if best_ob:
                    stop_loss = best_ob.price_low - (atr * 0.5)
                else:
                    recent_low = df['low'].tail(20).min()
                    stop_loss = recent_low - (atr * 0.5)
                
                risk = current_price - stop_loss
                take_profit = current_price + (risk * self.config.rr_ratio)
            else:
                # SL above order block or recent swing high
                best_ob = metadata.get('order_block')
                if best_ob:
                    stop_loss = best_ob.price_high + (atr * 0.5)
                else:
                    recent_high = df['high'].tail(20).max()
                    stop_loss = recent_high + (atr * 0.5)
                
                risk = stop_loss - current_price
                take_profit = current_price - (risk * self.config.rr_ratio)
            
            return {
                'type': signal_type,
                'price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'reason': reason,
                'atr': atr,
                'metadata': metadata
            }
        
        return None
    
    # ========================================================================
    # ICT ANALYSIS METHODS
    # ========================================================================
    
    def identify_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Identify Higher Highs (HH), Higher Lows (HL), Lower Highs (LH), Lower Lows (LL)
        BOS (Break of Structure) and CHoCH (Change of Character)
        """
        if len(df) < 20:
            return self.market_structure
        
        # Only analyze recent data for performance
        recent_df = df.tail(100) if len(df) > 100 else df
        
        # Find swing highs and lows
        swing_high = recent_df['high'][(recent_df['high'] > recent_df['high'].shift(1)) & 
                                       (recent_df['high'] > recent_df['high'].shift(-1)) &
                                       (recent_df['high'] > recent_df['high'].shift(2)) &
                                       (recent_df['high'] > recent_df['high'].shift(-2))]
        
        swing_low = recent_df['low'][(recent_df['low'] < recent_df['low'].shift(1)) & 
                                      (recent_df['low'] < recent_df['low'].shift(-1)) &
                                      (recent_df['low'] < recent_df['low'].shift(2)) &
                                      (recent_df['low'] < recent_df['low'].shift(-2))]
        
        # Get recent swing points
        recent_highs = swing_high.dropna().tail(5).tolist()
        recent_lows = swing_low.dropna().tail(5).tolist()
        
        # Determine trend
        trend = 'neutral'
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            # Bullish: Higher Highs and Higher Lows
            if recent_highs[-1] > recent_highs[-2] and recent_lows[-1] > recent_lows[-2]:
                trend = 'bullish'
            # Bearish: Lower Highs and Lower Lows
            elif recent_highs[-1] < recent_highs[-2] and recent_lows[-1] < recent_lows[-2]:
                trend = 'bearish'
        
        self.market_structure = {
            'highs': recent_highs,
            'lows': recent_lows,
            'trend': trend,
            'last_high': recent_highs[-1] if recent_highs else None,
            'last_low': recent_lows[-1] if recent_lows else None
        }
        
        return self.market_structure
    
    def identify_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """
        Identify Order Blocks (OB)
        Bullish OB: Last down candle before strong up move
        Bearish OB: Last up candle before strong down move
        """
        if len(df) < self.config.lookback_candles:
            return []
        
        order_blocks = []
        
        # Only scan recent data for performance
        scan_range = min(50, len(df) - 3)
        start_idx = len(df) - scan_range - 3
        
        for i in range(start_idx, len(df) - 3):
            # Bullish Order Block
            if (df['close'].iloc[i] < df['open'].iloc[i] and  # Down candle
                df['close'].iloc[i+1] > df['open'].iloc[i+1] and  # Up candle
                df['close'].iloc[i+2] > df['open'].iloc[i+2] and  # Up candle
                df['close'].iloc[i+2] > df['high'].iloc[i]):  # Strong move up
                
                ob = OrderBlock(
                    price_high=df['high'].iloc[i],
                    price_low=df['low'].iloc[i],
                    direction='bullish',
                    time=df.index[i],
                    strength=((df['close'].iloc[i+2] - df['low'].iloc[i]) / 
                             df['low'].iloc[i]) * 100
                )
                order_blocks.append(ob)
            
            # Bearish Order Block
            elif (df['close'].iloc[i] > df['open'].iloc[i] and  # Up candle
                  df['close'].iloc[i+1] < df['open'].iloc[i+1] and  # Down candle
                  df['close'].iloc[i+2] < df['open'].iloc[i+2] and  # Down candle
                  df['close'].iloc[i+2] < df['low'].iloc[i]):  # Strong move down
                
                ob = OrderBlock(
                    price_high=df['high'].iloc[i],
                    price_low=df['low'].iloc[i],
                    direction='bearish',
                    time=df.index[i],
                    strength=((df['high'].iloc[i] - df['close'].iloc[i+2]) / 
                             df['high'].iloc[i]) * 100
                )
                order_blocks.append(ob)
        
        # Keep only recent order blocks (last 10)
        return order_blocks[-10:] if len(order_blocks) > 10 else order_blocks
    
    def identify_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """
        Identify Fair Value Gaps (FVG/Imbalances)
        Bullish FVG: Gap between candle[i-2].low and candle[i].high when candle[i-1] doesn't fill it
        Bearish FVG: Gap between candle[i-2].high and candle[i].low when candle[i-1] doesn't fill it
        """
        if len(df) < 3:
            return []
        
        fvgs = []
        current_price = df['close'].iloc[-1]
        
        # Only scan recent data
        scan_range = min(50, len(df) - 2)
        start_idx = len(df) - scan_range - 2
        
        for i in range(start_idx, len(df)):
            if i < 2:
                continue
            
            # Bullish FVG
            gap_bottom = df['high'].iloc[i-2]
            gap_top = df['low'].iloc[i]
            
            if (gap_top > gap_bottom and
                df['high'].iloc[i-1] < gap_bottom and
                (gap_top - gap_bottom) >= self.config.fvg_min_size):
                
                # Check if FVG is filled by subsequent candles
                filled = False
                for j in range(i+1, len(df)):
                    if df['low'].iloc[j] <= gap_bottom:
                        filled = True
                        break
                
                fvg = FairValueGap(
                    top=gap_top,
                    bottom=gap_bottom,
                    direction='bullish',
                    time=df.index[i],
                    filled=filled
                )
                fvgs.append(fvg)
            
            # Bearish FVG
            gap_top = df['low'].iloc[i-2]
            gap_bottom = df['high'].iloc[i]
            
            if (gap_bottom < gap_top and
                df['low'].iloc[i-1] > gap_top and
                (gap_top - gap_bottom) >= self.config.fvg_min_size):
                
                # Check if FVG is filled
                filled = False
                for j in range(i+1, len(df)):
                    if df['high'].iloc[j] >= gap_top:
                        filled = True
                        break
                
                fvg = FairValueGap(
                    top=gap_top,
                    bottom=gap_bottom,
                    direction='bearish',
                    time=df.index[i],
                    filled=filled
                )
                fvgs.append(fvg)
        
        # Keep only unfilled FVGs and recent ones
        active_fvgs = [fvg for fvg in fvgs if not fvg.filled]
        return active_fvgs[-10:] if len(active_fvgs) > 10 else active_fvgs
    
    def detect_liquidity_sweep(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect liquidity sweeps (stop hunts)
        Returns 'bullish' or 'bearish' if sweep detected
        """
        if len(df) < 20:
            return None
        
        recent_df = df.tail(20)
        current_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Calculate pip size for the symbol
        # Try to get from MT5, fallback to default calculation
        try:
            symbol_info = mt5.symbol_info(self.config.symbol)
            if symbol_info:
                point = symbol_info.point
            else:
                # Fallback: assume standard forex
                point = 0.00001 if 'JPY' not in self.config.symbol else 0.001
        except:
            # If MT5 not connected, use fallback
            point = 0.00001 if 'JPY' not in self.config.symbol else 0.001
        
        pip_value = point * 10 if 'JPY' in self.config.symbol else point
        sweep_size = self.config.liquidity_sweep_pips * pip_value
        
        # Bullish Sweep: Wick below recent lows then closes higher
        recent_low = recent_df['low'].min()
        if (current_candle['low'] < recent_low - sweep_size and
            current_candle['close'] > prev_candle['close'] and
            current_candle['close'] > current_candle['open']):
            return 'bullish'
        
        # Bearish Sweep: Wick above recent highs then closes lower
        recent_high = recent_df['high'].max()
        if (current_candle['high'] > recent_high + sweep_size and
            current_candle['close'] < prev_candle['close'] and
            current_candle['close'] < current_candle['open']):
            return 'bearish'
        
        return None
    
    # ========================================================================
    # SIGNAL HELPER METHODS
    # ========================================================================
    
    def _check_bullish_setup(self, df: pd.DataFrame, current_price: float, 
                             liquidity_sweep: Optional[str]) -> bool:
        """Check if bullish setup conditions are met"""
        conditions_met = 0
        required_conditions = 0
        
        # Condition 1: Market Structure (optional)
        if self.config.use_market_structure:
            required_conditions += 1
            if self.market_structure['trend'] == 'bullish':
                conditions_met += 1
        
        # Condition 2: Near bullish Order Block
        if self.config.use_order_blocks and self.order_blocks:
            required_conditions += 1
            best_ob = self._find_best_order_block('bullish', current_price)
            if best_ob:
                conditions_met += 1
        
        # Condition 3: Near bullish FVG
        if self.config.use_fvg and self.fair_value_gaps:
            required_conditions += 1
            best_fvg = self._find_best_fvg('bullish', current_price)
            if best_fvg:
                conditions_met += 1
        
        # Condition 4: Liquidity Sweep
        if self.config.use_liquidity_sweeps:
            required_conditions += 1
            if liquidity_sweep == 'bullish':
                conditions_met += 1
        
        # Need at least 60% of conditions
        if required_conditions == 0:
            return False
        
        return (conditions_met / required_conditions) >= 0.6
    
    def _check_bearish_setup(self, df: pd.DataFrame, current_price: float, 
                             liquidity_sweep: Optional[str]) -> bool:
        """Check if bearish setup conditions are met"""
        conditions_met = 0
        required_conditions = 0
        
        # Condition 1: Market Structure
        if self.config.use_market_structure:
            required_conditions += 1
            if self.market_structure['trend'] == 'bearish':
                conditions_met += 1
        
        # Condition 2: Near bearish Order Block
        if self.config.use_order_blocks and self.order_blocks:
            required_conditions += 1
            best_ob = self._find_best_order_block('bearish', current_price)
            if best_ob:
                conditions_met += 1
        
        # Condition 3: Near bearish FVG
        if self.config.use_fvg and self.fair_value_gaps:
            required_conditions += 1
            best_fvg = self._find_best_fvg('bearish', current_price)
            if best_fvg:
                conditions_met += 1
        
        # Condition 4: Liquidity Sweep
        if self.config.use_liquidity_sweeps:
            required_conditions += 1
            if liquidity_sweep == 'bearish':
                conditions_met += 1
        
        # Need at least 60% of conditions
        if required_conditions == 0:
            return False
        
        return (conditions_met / required_conditions) >= 0.6
    
    def _find_best_order_block(self, direction: str, current_price: float) -> Optional[OrderBlock]:
        """Find the best order block near current price"""
        if not self.order_blocks:
            return None
        
        # Filter by direction
        relevant_obs = [ob for ob in self.order_blocks if ob.direction == direction]
        if not relevant_obs:
            return None
        
        # Find closest to current price
        if direction == 'bullish':
            # For bullish, we want OB below current price
            below_price = [ob for ob in relevant_obs if ob.price_high < current_price]
            if below_price:
                return max(below_price, key=lambda x: x.price_high)
        else:
            # For bearish, we want OB above current price
            above_price = [ob for ob in relevant_obs if ob.price_low > current_price]
            if above_price:
                return min(above_price, key=lambda x: x.price_low)
        
        return None
    
    def _find_best_fvg(self, direction: str, current_price: float) -> Optional[FairValueGap]:
        """Find the best FVG near current price"""
        if not self.fair_value_gaps:
            return None
        
        # Filter by direction and unfilled
        relevant_fvgs = [fvg for fvg in self.fair_value_gaps 
                        if fvg.direction == direction and not fvg.filled]
        if not relevant_fvgs:
            return None
        
        # Check if price is in or near FVG
        for fvg in relevant_fvgs:
            if direction == 'bullish':
                if fvg.bottom <= current_price <= fvg.top:
                    return fvg
            else:
                if fvg.bottom <= current_price <= fvg.top:
                    return fvg
        
        return None
    
    def _calculate_signal_confidence(self, df: pd.DataFrame, direction: str) -> float:
        """Calculate confidence score for the signal (0-100)"""
        confidence = 0.0
        
        # Market structure alignment (+30)
        if self.market_structure['trend'] == direction:
            confidence += 30
        
        # Order Block presence (+25)
        ob = self._find_best_order_block(direction, df['close'].iloc[-1])
        if ob:
            confidence += 25
        
        # FVG presence (+25)
        fvg = self._find_best_fvg(direction, df['close'].iloc[-1])
        if fvg:
            confidence += 25
        
        # Recent momentum (+20)
        recent_close = df['close'].tail(5)
        if direction == 'bullish' and recent_close.is_monotonic_increasing:
            confidence += 20
        elif direction == 'bearish' and recent_close.is_monotonic_decreasing:
            confidence += 20
        
        return min(confidence, 100.0)
    
    def _add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add ATR indicator to dataframe"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(period).mean()
        
        return df
    
    def _calculate_atr_value(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate current ATR value"""
        if 'atr' in df.columns:
            return df['atr'].iloc[-1]
        
        df = self._add_atr(df, period)
        return df['atr'].iloc[-1]
    
    
    # ========================================================================
    # HOOKS IMPLEMENTATION (Optional - for custom behavior)
    # ========================================================================
    
    def hook_pre_signal_generation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hook called before signal generation"""
        # Clean up old order blocks and FVGs
        current_time = df.index[-1]
        
        # Remove order blocks older than 100 candles
        if self.order_blocks:
            self.order_blocks = [ob for ob in self.order_blocks 
                                if (current_time - ob.time).total_seconds() < 
                                (100 * self._get_timeframe_seconds())]
        
        return df
    
    def hook_post_signal_generation(self, signal: Optional[Dict]) -> Optional[Dict]:
        """Hook called after signal generation"""
        if signal:
            # Log ICT-specific information
            metadata = signal.get('metadata', {})
            ms_trend = metadata.get('market_structure', {}).get('trend', 'unknown')
            self.logger.info(f"ICT Analysis: Market Structure = {ms_trend}")
        
        return signal
    
    def hook_pre_trade_execution(self, signal: Dict) -> Dict:
        """Hook called before trade execution"""
        # Could add additional filters here
        return signal
    
    def hook_post_trade_execution(self, success: bool, signal: Dict):
        """Hook called after trade execution"""
        if success:
            setup_type = signal.get('metadata', {}).get('setup_type', 'ICT')
            self.logger.info(f"✅ ICT trade opened: {signal.get('type')} - {setup_type}")
        else:
            self.logger.warning(f"❌ ICT trade failed: {signal.get('type')}")
    
    def _get_timeframe_seconds(self) -> int:
        """Get timeframe in seconds"""
        timeframe_map = {
            mt5.TIMEFRAME_M1: 60,
            mt5.TIMEFRAME_M5: 300,
            mt5.TIMEFRAME_M15: 900,
            mt5.TIMEFRAME_M30: 1800,
            mt5.TIMEFRAME_H1: 3600,
            mt5.TIMEFRAME_H4: 14400,
            mt5.TIMEFRAME_D1: 86400,
        }
        return timeframe_map.get(self.config.timeframe, 900)
    
    # ========================================================================
    # STRATEGY REGISTRATION
    # ========================================================================
    
    def get_strategy_info(self) -> Dict:
        """Get strategy information for registry"""
        return {
            'name': 'ICT Bot',
            'version': '2.0.0',
            'description': 'Inner Circle Trader strategy with Smart Money Concepts',
            'author': 'Trần Trọng Hiếu',
            'strategies': ['Order Blocks', 'Fair Value Gaps', 'Market Structure', 'Liquidity Sweeps'],
            'timeframes': ['M15', 'M30', 'H1', 'H4'],
            'risk_level': 'Medium',
            'tags': ['ICT', 'SMC', 'price-action', 'institutional']
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Create configuration
    config = ICTConfig(
        symbol="EURUSDm",
        timeframe=mt5.TIMEFRAME_M15,
        risk_percent=1.0,
        rr_ratio=2.0,
        max_positions=1,
        magic_number=123457,
        
        # ICT-specific
        use_market_structure=True,
        use_order_blocks=True,
        use_fvg=True,
        use_liquidity_sweeps=True,
        move_sl_to_breakeven=True,
        
        # Dual orders
        use_dual_orders=True,
        rr_order1=1.0,  # Quick profit at RR 1:1
    )
    
    # Create and run bot
    bot = ICTBot(config)
    
    # Connect to MT5
    if bot.connect(login=12345, password="password", server="Server-Name"):
        # Run bot
        bot.run(interval_seconds=60)
    else:
        print("Failed to connect to MT5")
