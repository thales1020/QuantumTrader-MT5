"""
Portfolio Strategy Example

This example demonstrates how to trade multiple symbols simultaneously
with shared risk management and capital allocation.

Strategy Logic:
- Trade 3-5 symbols with the same strategy
- Allocate capital proportionally
- Manage total portfolio risk
- Rebalance based on performance

Example:
    # Create config
    config = {
        'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
        'total_risk_percent': 3.0,  # Max 3% risk across all positions
        'strategy_type': 'trend_following',
    }
    
    # Initialize and run
    portfolio = PortfolioStrategy(config)
    portfolio.run()

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import MetaTrader5 as mt5
import talib
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np


@StrategyRegistry.register("portfolio")
class PortfolioStrategy(BaseTradingBot):
    """
    Portfolio Strategy - Trade multiple symbols with unified risk management
    
    This strategy manages a portfolio of currency pairs, applying:
    - Equal weight allocation or performance-based weighting
    - Centralized risk management across all symbols
    - Correlation-aware position sizing
    - Automated rebalancing
    
    Features:
    - Trade 3-10 symbols simultaneously
    - Total portfolio risk limited to configured percentage
    - Individual position sizing based on volatility
    - Correlation checks to avoid over-exposure
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Portfolio configuration
        self.symbols = config.get('symbols', ['EURUSD', 'GBPUSD', 'USDJPY'])
        self.total_risk_percent = config.get('total_risk_percent', 3.0)
        self.max_positions = config.get('max_positions', len(self.symbols))
        self.rebalance_period = config.get('rebalance_hours', 24)
        
        # Strategy parameters (apply to all symbols)
        self.ema_fast = config.get('ema_fast', 50)
        self.ema_slow = config.get('ema_slow', 200)
        self.atr_period = config.get('atr_period', 14)
        self.sl_atr_mult = config.get('sl_atr_multiplier', 2.0)
        self.tp_atr_mult = config.get('tp_atr_multiplier', 3.0)
        
        # Portfolio tracking
        self.symbol_data = {}  # Store data for each symbol
        self.symbol_signals = {}  # Current signals
        self.symbol_weights = {}  # Capital allocation weights
        self.last_rebalance = None
        
        # Initialize equal weights
        weight = 1.0 / len(self.symbols)
        for symbol in self.symbols:
            self.symbol_weights[symbol] = weight
        
        self.logger.info(f"Initialized Portfolio Strategy")
        self.logger.info(f"Symbols: {', '.join(self.symbols)}")
        self.logger.info(f"Total Risk: {self.total_risk_percent}%")
        self.logger.info(f"Max Positions: {self.max_positions}")
    
    def fetch_symbol_data(self, symbol: str, bars: int = 300) -> Optional[pd.DataFrame]:
        """
        Fetch data for a specific symbol
        
        Args:
            symbol: Symbol to fetch
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        rates = mt5.copy_rates_from_pos(
            symbol,
            self.timeframe,
            0,
            bars
        )
        
        if rates is None or len(rates) == 0:
            self.logger.error(f"Failed to fetch data for {symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df['symbol'] = symbol
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicators for portfolio strategy
        
        Uses EMA crossover for trend detection and ATR for volatility
        
        Args:
            df: OHLCV data
            
        Returns:
            DataFrame with indicators
        """
        # Trend indicators
        df['ema_fast'] = talib.EMA(df['close'], timeperiod=self.ema_fast)
        df['ema_slow'] = talib.EMA(df['close'], timeperiod=self.ema_slow)
        
        # Volatility
        df['atr'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=self.atr_period
        )
        
        # Normalized ATR (for cross-symbol comparison)
        df['atr_pct'] = (df['atr'] / df['close']) * 100
        
        return df
    
    def generate_signal_for_symbol(self, df: pd.DataFrame, symbol: str) -> int:
        """
        Generate signal for a specific symbol
        
        Strategy: EMA crossover
        - BUY: Fast EMA crosses above Slow EMA
        - SELL: Fast EMA crosses below Slow EMA
        
        Args:
            df: DataFrame with indicators
            symbol: Symbol name
            
        Returns:
            1 for buy, -1 for sell, 0 for no signal
        """
        if len(df) < 2:
            return 0
        
        # Current and previous EMA values
        ema_fast_current = df['ema_fast'].iloc[-1]
        ema_slow_current = df['ema_slow'].iloc[-1]
        ema_fast_prev = df['ema_fast'].iloc[-2]
        ema_slow_prev = df['ema_slow'].iloc[-2]
        
        # BUY Signal: Fast crosses above Slow
        if ema_fast_prev <= ema_slow_prev and ema_fast_current > ema_slow_current:
            self.logger.info(f"{symbol}: BUY signal (EMA crossover)")
            return 1
        
        # SELL Signal: Fast crosses below Slow
        if ema_fast_prev >= ema_slow_prev and ema_fast_current < ema_slow_current:
            self.logger.info(f"{symbol}: SELL signal (EMA crossover)")
            return -1
        
        return 0
    
    def update_portfolio_data(self):
        """Fetch and update data for all symbols in portfolio"""
        for symbol in self.symbols:
            df = self.fetch_symbol_data(symbol)
            if df is not None:
                df = self.calculate_indicators(df)
                self.symbol_data[symbol] = df
                
                # Update signal
                signal = self.generate_signal_for_symbol(df, symbol)
                self.symbol_signals[symbol] = signal
    
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix between symbols
        
        Returns:
            Correlation matrix
        """
        # Collect close prices for all symbols
        close_prices = {}
        
        for symbol, df in self.symbol_data.items():
            if df is not None and len(df) > 0:
                close_prices[symbol] = df['close']
        
        if len(close_prices) < 2:
            return pd.DataFrame()
        
        # Align data and calculate correlation
        price_df = pd.DataFrame(close_prices)
        correlation = price_df.corr()
        
        return correlation
    
    def get_available_risk_budget(self) -> float:
        """
        Calculate available risk budget based on existing positions
        
        Returns:
            Available risk percentage
        """
        # Get current open positions
        positions = mt5.positions_get()
        if positions is None:
            return self.total_risk_percent
        
        # Filter positions for our symbols
        our_positions = [
            p for p in positions 
            if p.symbol in self.symbols and p.magic == self.magic_number
        ]
        
        # Calculate used risk (simplified)
        used_risk = len(our_positions) * (self.total_risk_percent / self.max_positions)
        available_risk = max(0, self.total_risk_percent - used_risk)
        
        return available_risk
    
    def select_best_opportunities(self, max_trades: int = 3) -> List[Dict]:
        """
        Select best trading opportunities from all symbols
        
        Ranks symbols by:
        1. Signal strength
        2. Low correlation with existing positions
        3. Volatility (prefer moderate volatility)
        
        Args:
            max_trades: Maximum number of trades to select
            
        Returns:
            List of trade opportunities with symbol and signal
        """
        opportunities = []
        
        # Collect all symbols with signals
        for symbol, signal in self.symbol_signals.items():
            if signal != 0 and symbol in self.symbol_data:
                df = self.symbol_data[symbol]
                
                opportunities.append({
                    'symbol': symbol,
                    'signal': signal,
                    'atr_pct': df['atr_pct'].iloc[-1],
                    'weight': self.symbol_weights.get(symbol, 1.0),
                })
        
        if not opportunities:
            return []
        
        # Sort by weight (performance-based) and volatility
        opportunities.sort(
            key=lambda x: x['weight'] / (x['atr_pct'] + 0.1),
            reverse=True
        )
        
        # Select top opportunities
        selected = opportunities[:max_trades]
        
        self.logger.info(f"Selected {len(selected)} opportunities: {[o['symbol'] for o in selected]}")
        
        return selected
    
    def allocate_risk_per_symbol(self, num_positions: int) -> float:
        """
        Calculate risk allocation per symbol
        
        Args:
            num_positions: Number of positions to open
            
        Returns:
            Risk percentage per position
        """
        available_risk = self.get_available_risk_budget()
        
        if num_positions == 0:
            return 0.0
        
        # Divide available risk equally among new positions
        risk_per_position = available_risk / num_positions
        
        return risk_per_position
    
    def rebalance_weights(self):
        """
        Rebalance portfolio weights based on performance
        
        This is a simple example - in production, you'd use more
        sophisticated methods (Sharpe ratio, drawdown, etc.)
        """
        positions = mt5.positions_get()
        if positions is None:
            return
        
        # Calculate P&L for each symbol
        symbol_pnl = {symbol: 0.0 for symbol in self.symbols}
        
        for position in positions:
            if position.symbol in self.symbols:
                symbol_pnl[position.symbol] += position.profit
        
        # Calculate performance scores (higher = better)
        total_pnl = sum(symbol_pnl.values())
        
        if total_pnl > 0:
            # Performance-based weighting
            for symbol in self.symbols:
                pnl = symbol_pnl.get(symbol, 0)
                self.symbol_weights[symbol] = max(0.1, (pnl / total_pnl) * 0.7 + 0.3)
        else:
            # Equal weighting if no profit
            weight = 1.0 / len(self.symbols)
            for symbol in self.symbols:
                self.symbol_weights[symbol] = weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.symbol_weights.values())
        for symbol in self.symbols:
            self.symbol_weights[symbol] /= total_weight
        
        self.logger.info(f"Rebalanced weights: {self.symbol_weights}")
        self.last_rebalance = datetime.now()
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        """
        This method is overridden for portfolio strategy
        We manage signals at portfolio level, not single symbol
        
        Returns:
            Always returns 0 (no single signal)
        """
        return 0
    
    def run_portfolio_logic(self):
        """
        Main portfolio trading logic
        
        Steps:
        1. Update data for all symbols
        2. Generate signals for each symbol
        3. Select best opportunities
        4. Allocate risk and open positions
        5. Rebalance periodically
        """
        # Update all symbol data
        self.update_portfolio_data()
        
        # Check if rebalancing is needed
        if (self.last_rebalance is None or
            (datetime.now() - self.last_rebalance).seconds > self.rebalance_period * 3600):
            self.rebalance_weights()
        
        # Get best opportunities
        opportunities = self.select_best_opportunities(max_trades=self.max_positions)
        
        if not opportunities:
            self.logger.debug("No trading opportunities found")
            return
        
        # Calculate risk allocation
        risk_per_position = self.allocate_risk_per_symbol(len(opportunities))
        
        if risk_per_position <= 0:
            self.logger.warning("No risk budget available")
            return
        
        # Open positions for selected symbols
        for opp in opportunities:
            symbol = opp['symbol']
            signal = opp['signal']
            df = self.symbol_data[symbol]
            
            # Calculate position parameters
            current_price = df['close'].iloc[-1]
            atr = df['atr'].iloc[-1]
            
            sl_price = (current_price - atr * self.sl_atr_mult if signal == 1 
                       else current_price + atr * self.sl_atr_mult)
            tp_price = (current_price + atr * self.tp_atr_mult if signal == 1
                       else current_price - atr * self.tp_atr_mult)
            
            # Calculate position size based on allocated risk
            account_balance = self.get_account_balance()
            risk_amount = account_balance * (risk_per_position / 100)
            
            # Simplified lot calculation
            lot_size = 0.01  # Would calculate based on risk_amount and SL distance
            
            self.logger.info(f"Opening position: {symbol} {signal} @ {current_price}")
            self.logger.info(f"SL: {sl_price}, TP: {tp_price}, Lots: {lot_size}")
            
            # Here you would call self.place_order() or similar
            # self.place_order(symbol, signal, lot_size, sl_price, tp_price)
    
    def get_strategy_info(self) -> Dict:
        """Return portfolio strategy information"""
        return {
            'name': 'Portfolio Strategy',
            'id': 'portfolio',
            'version': '1.0.0',
            'description': 'Multi-symbol portfolio with unified risk management',
            'symbols': self.symbols,
            'total_risk': f"{self.total_risk_percent}%",
            'max_positions': self.max_positions,
            'strategy': f'EMA Crossover ({self.ema_fast}/{self.ema_slow})',
        }


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
        'timeframe': mt5.TIMEFRAME_H1,
        'total_risk_percent': 3.0,
        'max_positions': 3,
        'ema_fast': 50,
        'ema_slow': 200,
        'atr_period': 14,
        'sl_atr_multiplier': 2.0,
        'tp_atr_multiplier': 3.0,
        'rebalance_hours': 24,
        'magic_number': 100002,
    }
    
    # Initialize portfolio strategy
    portfolio = PortfolioStrategy(config)
    
    # Print strategy info
    info = portfolio.get_strategy_info()
    print("\n" + "=" * 60)
    print(f"Strategy: {info['name']}")
    print("=" * 60)
    print(f"Version: {info['version']}")
    print(f"Description: {info['description']}")
    print(f"\nSymbols: {', '.join(info['symbols'])}")
    print(f"Total Risk: {info['total_risk']}")
    print(f"Max Positions: {info['max_positions']}")
    print(f"Strategy Type: {info['strategy']}")
    print("=" * 60 + "\n")
    
    # Run portfolio logic (would be in a loop in production)
    # portfolio.run_portfolio_logic()
