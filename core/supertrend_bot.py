"""
SuperTrend Bot - Refactored Version
Inherits from BaseTradingBot for improved architecture

Features:
- Multi-factor SuperTrend calculation
- K-means clustering for factor optimization
- Volume-adjusted performance tracking
- Normalized volatility adjustment
- Trailing stop logic
- Hook system for extensibility
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import talib
from sklearn.cluster import KMeans
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
class SuperTrendConfig(BaseConfig):
    """
    Configuration for SuperTrend Bot - extends BaseConfig
    """
    # SuperTrend parameters
    atr_period: int = 10
    min_factor: float = 1.0
    max_factor: float = 5.0
    factor_step: float = 0.5
    
    # ML optimization
    perf_alpha: float = 10.0  # EMA smoothing for performance
    cluster_choice: str = "Best"  # "Best", "Average", or "Worst"
    
    # Volume filter
    volume_ma_period: int = 20
    volume_multiplier: float = 1.2
    
    # Trailing stop
    use_trailing: bool = True
    trail_activation: float = 1.5  # ATR multiplier for activation


# ============================================================================
# SUPERTREND BOT CLASS
# ============================================================================

class SuperTrendBot(BaseTradingBot):
    """
    SuperTrend Strategy Bot with ML Optimization
    
    Uses K-means clustering to select optimal SuperTrend factor
    from a range of possible factors, optimizing for best performance.
    """
    
    def __init__(self, config: SuperTrendConfig):
        super().__init__(config)
        
        # SuperTrend-specific state
        self.supertrends: Dict[float, pd.DataFrame] = {}
        self.optimal_factor: Optional[float] = None
        self.cluster_performance: Optional[float] = None
        
        self.logger.info("SuperTrend Bot initialized with ML optimization")
        self.logger.info(f"Factor range: {config.min_factor}-{config.max_factor} (step {config.factor_step})")
        self.logger.info(f"Cluster choice: {config.cluster_choice}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all SuperTrend indicators with ML optimization
        
        Steps:
        1. Calculate basic indicators (ATR, volume MA, volatility)
        2. Calculate multiple SuperTrend indicators (min_factor to max_factor)
        3. Perform K-means clustering to select optimal factor
        4. Add optimal SuperTrend to dataframe
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        if len(df) < 50:
            self.logger.warning("Not enough data for indicators")
            return df
        
        # 1. Basic indicators
        df['hl2'] = (df['high'] + df['low']) / 2
        df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, 
                              timeperiod=self.config.atr_period)
        df['volume_ma'] = df['tick_volume'].rolling(window=self.config.volume_ma_period).mean()
        df['volatility'] = df['close'].rolling(window=self.config.atr_period).std()
        df['norm_volatility'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
        # Fill NaN values
        df['norm_volatility'].fillna(1.0, inplace=True)
        df['atr'].fillna(method='bfill', inplace=True)
        df['volume_ma'].fillna(df['tick_volume'].mean(), inplace=True)
        
        # 2. Calculate multi-factor SuperTrends
        self.supertrends = self.calculate_supertrends(df)
        
        # 3. ML Clustering for factor optimization
        self.optimal_factor, self.cluster_performance = self.perform_clustering(self.supertrends)
        
        self.logger.debug(f"Optimal factor: {self.optimal_factor:.2f}, Performance: {self.cluster_performance:.4f}")
        
        # 4. Add optimal SuperTrend to dataframe
        if self.optimal_factor and self.optimal_factor in self.supertrends:
            optimal_st = self.supertrends[self.optimal_factor]
            df['st_trend'] = optimal_st['trend']
            df['st_output'] = optimal_st['output']
            df['st_perf'] = optimal_st['vol_adj_perf']
        
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on optimal SuperTrend
        
        Signal generation logic:
        1. Check volume condition (must have sufficient volume)
        2. Get optimal SuperTrend from clustering
        3. Detect trend change (01 for BUY, 10 for SELL)
        4. Calculate SL/TP based on SuperTrend level and ATR
        
        Args:
            df: DataFrame with calculated indicators
            
        Returns:
            Signal dict or None
        """
        if len(df) < 50:
            return None
        
        # 1. Check volume condition
        if not self.check_volume_condition(df):
            self.logger.debug("Volume condition not met")
            return None
        
        # 2. Get optimal SuperTrend
        if not self.optimal_factor or self.optimal_factor not in self.supertrends:
            self.logger.warning("Optimal factor not available")
            return None
        
        optimal_st = self.supertrends[self.optimal_factor]
        
        # 3. Check for trend change
        if len(optimal_st) < 2:
            return None
        
        current_trend = optimal_st['trend'].iloc[-1]
        previous_trend = optimal_st['trend'].iloc[-2]
        current_price = df['close'].iloc[-1]
        st_level = optimal_st['output'].iloc[-1]
        atr = df['atr'].iloc[-1]
        
        signal = None
        
        # Bullish signal: Trend changes from 0 (down) to 1 (up)
        if previous_trend == 0 and current_trend == 1:
            # Calculate TP using RR ratio: TP = price + (SL_distance * rr_ratio)
            sl_distance = abs(current_price - st_level)
            tp_distance = sl_distance * self.config.rr_ratio
            
            signal = {
                'type': 'BUY',
                'price': current_price,
                'stop_loss': st_level,
                'take_profit': current_price + tp_distance,
                'confidence': min(100.0, abs(self.cluster_performance) * 10) if self.cluster_performance else 50.0,
                'reason': f'SuperTrend bullish crossover (factor={self.optimal_factor:.1f})',
                'atr': atr,
                'metadata': {
                    'optimal_factor': self.optimal_factor,
                    'cluster_performance': self.cluster_performance,
                    'cluster_choice': self.config.cluster_choice,
                    'st_level': st_level,
                    'volume_ok': True,
                    'strategy': 'ML_SUPERTREND'
                }
            }
            self.logger.info(f"🔵 BUY signal generated at {current_price:.5f}")
        
        # Bearish signal: Trend changes from 1 (up) to 0 (down)
        elif previous_trend == 1 and current_trend == 0:
            # Calculate TP using RR ratio: TP = price - (SL_distance * rr_ratio)
            sl_distance = abs(current_price - st_level)
            tp_distance = sl_distance * self.config.rr_ratio
            
            signal = {
                'type': 'SELL',
                'price': current_price,
                'stop_loss': st_level,
                'take_profit': current_price - tp_distance,
                'confidence': min(100.0, abs(self.cluster_performance) * 10) if self.cluster_performance else 50.0,
                'reason': f'SuperTrend bearish crossover (factor={self.optimal_factor:.1f})',
                'atr': atr,
                'metadata': {
                    'optimal_factor': self.optimal_factor,
                    'cluster_performance': self.cluster_performance,
                    'cluster_choice': self.config.cluster_choice,
                    'st_level': st_level,
                    'volume_ok': True,
                    'strategy': 'ML_SUPERTREND'
                }
            }
            self.logger.info(f" SELL signal generated at {current_price:.5f}")
        
        return signal
    
    # ========================================================================
    # SUPERTREND-SPECIFIC METHODS
    # ========================================================================
    
    def calculate_supertrends(self, df: pd.DataFrame) -> Dict[float, pd.DataFrame]:
        """
        Calculate multiple SuperTrend indicators with different factors
        
        For each factor from min_factor to max_factor:
        1. Calculate basic SuperTrend (upper/lower bands)
        2. Determine trend direction
        3. Calculate performance metrics (raw and volume-adjusted)
        4. Apply EMA smoothing to performance
        
        Args:
            df: DataFrame with OHLCV and basic indicators
            
        Returns:
            Dict mapping factor to SuperTrend DataFrame
        """
        factors = np.arange(
            self.config.min_factor, 
            self.config.max_factor + self.config.factor_step, 
            self.config.factor_step
        )
        
        supertrends = {}
        
        for factor in factors:
            st = pd.DataFrame(index=df.index)
            st['upper'] = df['hl2'] + (df['atr'] * factor)
            st['lower'] = df['hl2'] - (df['atr'] * factor)
            st['trend'] = 0
            st['output'] = 0.0
            st['perf'] = 0.0
            st['vol_adj_perf'] = 0.0
            
            # Calculate trend and output
            for i in range(1, len(df)):
                # Determine trend
                if df['close'].iloc[i] > st['upper'].iloc[i-1]:
                    st.iloc[i, st.columns.get_loc('trend')] = 1
                elif df['close'].iloc[i] < st['lower'].iloc[i-1]:
                    st.iloc[i, st.columns.get_loc('trend')] = 0
                else:
                    st.iloc[i, st.columns.get_loc('trend')] = st['trend'].iloc[i-1]
                
                # Calculate bands (maintaining direction)
                if st['trend'].iloc[i] == 1:
                    new_lower = max(st['lower'].iloc[i], st['lower'].iloc[i-1]) if st['trend'].iloc[i-1] == 1 else st['lower'].iloc[i]
                    st.iloc[i, st.columns.get_loc('lower')] = new_lower
                    st.iloc[i, st.columns.get_loc('output')] = new_lower
                else:
                    new_upper = min(st['upper'].iloc[i], st['upper'].iloc[i-1]) if st['trend'].iloc[i-1] == 0 else st['upper'].iloc[i]
                    st.iloc[i, st.columns.get_loc('upper')] = new_upper
                    st.iloc[i, st.columns.get_loc('output')] = new_upper
                
                # Calculate performance
                price_change = df['close'].iloc[i] - df['close'].iloc[i-1]
                direction = np.sign(df['close'].iloc[i-1] - st['output'].iloc[i-1])
                raw_perf = price_change * direction
                
                # Apply EMA smoothing
                alpha = 2 / (self.config.perf_alpha + 1)
                st.iloc[i, st.columns.get_loc('perf')] = alpha * raw_perf + (1 - alpha) * st['perf'].iloc[i-1]
                
                # Volume-adjusted performance
                vol_adj = raw_perf / (1 + df['norm_volatility'].iloc[i])
                st.iloc[i, st.columns.get_loc('vol_adj_perf')] = alpha * vol_adj + (1 - alpha) * st['vol_adj_perf'].iloc[i-1]
            
            supertrends[factor] = st
        
        self.logger.debug(f"Calculated {len(supertrends)} SuperTrend indicators")
        return supertrends
    
    def perform_clustering(self, supertrends: Dict[float, pd.DataFrame]) -> Tuple[float, float]:
        """
        Use K-means clustering to select optimal SuperTrend factor
        
        Process:
        1. Extract volume-adjusted performance for each factor
        2. Apply K-means clustering (3 clusters: Worst, Average, Best)
        3. Select cluster based on config.cluster_choice
        4. Return mean factor from selected cluster
        
        Args:
            supertrends: Dict of calculated SuperTrend DataFrames
            
        Returns:
            Tuple of (optimal_factor, cluster_performance)
        """
        performances = []
        factors = []
        
        # Extract performances (last 100 bars average)
        for factor, st in supertrends.items():
            if len(st) < 100:
                continue
            perf = st['vol_adj_perf'].iloc[-100:].mean()
            
            # Skip NaN or inf values
            if not np.isnan(perf) and not np.isinf(perf):
                performances.append(perf)
                factors.append(factor)
        
        # Validate we have data
        if len(performances) == 0:
            self.logger.error("No valid performance data for clustering")
            first_factor = list(supertrends.keys())[0]
            return first_factor, 0.0
        
        performances = np.array(performances).reshape(-1, 1)
        
        # Remove any remaining NaN
        valid_mask = ~np.isnan(performances).any(axis=1)
        performances = performances[valid_mask]
        factors = [f for i, f in enumerate(factors) if valid_mask[i]]
        
        if len(performances) == 0:
            self.logger.error("No valid performance data after NaN removal")
            first_factor = list(supertrends.keys())[0]
            return first_factor, 0.0
        
        # Check if we have enough variation for clustering
        if len(set(performances.flatten())) < 3:
            self.logger.warning("Not enough variation for clustering, using best performer")
            best_idx = np.argmax(performances)
            return factors[best_idx], performances[best_idx][0]
        
        # K-means clustering (3 clusters)
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(performances)
        
        # Sort clusters by performance
        cluster_centers = kmeans.cluster_centers_.flatten()
        sorted_indices = np.argsort(cluster_centers)
        
        # Map cluster choice to index
        cluster_map = {"Worst": 0, "Average": 1, "Best": 2}
        target_cluster = cluster_map.get(self.config.cluster_choice, 2)  # Default to Best
        target_label = sorted_indices[target_cluster]
        
        # Get factors in target cluster
        cluster_factors = [factors[i] for i, label in enumerate(kmeans.labels_) if label == target_label]
        
        if not cluster_factors:
            self.logger.warning("No factors in target cluster, using best overall")
            best_idx = np.argmax(performances)
            return factors[best_idx], performances[best_idx][0]
        
        # Return mean factor from cluster
        optimal_factor = np.mean(cluster_factors)
        cluster_perf = cluster_centers[target_label]
        
        self.logger.info(f"ML Optimization: Selected factor {optimal_factor:.2f} from '{self.config.cluster_choice}' cluster")
        self.logger.info(f"Cluster performance: {cluster_perf:.4f}")
        
        return optimal_factor, cluster_perf
    
    def check_volume_condition(self, df: pd.DataFrame) -> bool:
        """
        Check if current volume meets the threshold
        
        Args:
            df: DataFrame with volume data
            
        Returns:
            True if volume condition is met
        """
        if len(df) < 2:
            return False
        
        current_volume = df['tick_volume'].iloc[-1]
        volume_ma = df['volume_ma'].iloc[-1]
        
        return current_volume >= (volume_ma * self.config.volume_multiplier)
    
    def update_trailing_stop(self, position, current_price: float, atr: float) -> bool:
        """
        Update trailing stop based on SuperTrend levels
        
        Args:
            position: MT5 position object
            current_price: Current market price
            atr: Current ATR value
            
        Returns:
            True if stop was updated successfully
        """
        if not self.config.use_trailing:
            return False
        
        if not self.optimal_factor or self.optimal_factor not in self.supertrends:
            return False
        
        optimal_st = self.supertrends[self.optimal_factor]
        st_level = optimal_st['output'].iloc[-1]
        
        # Calculate new stop loss based on SuperTrend
        if position.type == mt5.ORDER_TYPE_BUY:
            # For long positions, trail stop upward
            new_sl = st_level
            
            # Only move stop if it's higher than current
            if new_sl > position.sl and new_sl < current_price:
                return self.modify_sl(position.ticket, new_sl)
        
        elif position.type == mt5.ORDER_TYPE_SELL:
            # For short positions, trail stop downward
            new_sl = st_level
            
            # Only move stop if it's lower than current
            if new_sl < position.sl and new_sl > current_price:
                return self.modify_sl(position.ticket, new_sl)
        
        return False
    
    # ========================================================================
    # HOOKS
    # ========================================================================
    
    def hook_post_signal_generation(self, signal: Optional[Dict]) -> Optional[Dict]:
        """Log ML optimization details after signal generation"""
        if signal:
            self.logger.info(f" ML Factor: {self.optimal_factor:.2f}")
            self.logger.info(f" Cluster Performance: {self.cluster_performance:.4f}")
            self.logger.info(f" Cluster Choice: {self.config.cluster_choice}")
        return signal
    
    def hook_post_cycle(self, cycle_data: Dict):
        """Log clustering status after each cycle"""
        if self.optimal_factor:
            self.logger.debug(f"Using ML-optimized factor: {self.optimal_factor:.2f} ({self.config.cluster_choice})")
        
        # Log number of supertrends calculated
        if self.supertrends:
            self.logger.debug(f"Tracking {len(self.supertrends)} SuperTrend variants")
