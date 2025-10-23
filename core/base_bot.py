"""
Base Trading Bot - Abstract Base Class for All Trading Strategies

This module provides the foundation for all trading bots in the system.
It implements common functionality and defines the contract that all bots must follow.

Author: xPOURY4
Date: October 23, 2025
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
import logging


@dataclass
class BaseTrade:
    """Base class for trade data"""
    entry_price: float
    stop_loss: float
    take_profit: float
    direction: int  # 1 for BUY, -1 for SELL
    volume: float
    ticket: int = 0
    entry_time: datetime = None
    ticket1: int = 0  # Quick profit order (RR 1:1)
    ticket2: int = 0  # Main RR order
    tp1_hit: bool = False  # Track if Order 1 hit TP
    sl_moved_to_breakeven: bool = False  # Track if SL moved to BE


@dataclass
class BaseConfig:
    """Base configuration with common settings"""
    symbol: str = "EURUSD"
    timeframe: int = mt5.TIMEFRAME_M15
    risk_percent: float = 1.0
    rr_ratio: float = 2.0
    max_positions: int = 1
    magic_number: int = 123456
    move_sl_to_breakeven: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        valid_keys = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_keys)


class BaseTradingBot(ABC):
    """
    Abstract base class for all trading bots.
    
    This class provides:
    - Common functionality (MT5 connection, data fetching, logging)
    - Template methods for trading cycle
    - Hook system for customization
    - Enforced contract through abstract methods
    
    To create a new bot:
    1. Inherit from BaseTradingBot
    2. Implement required abstract methods
    3. Optionally override template methods for custom behavior
    4. Register with StrategyRegistry
    
    Example:
        class MyBot(BaseTradingBot):
            def generate_signal(self, df):
                # Your signal logic
                return signal
            
            def calculate_indicators(self, df):
                # Your indicators
                return df
    """
    
    def __init__(self, config: BaseConfig):
        """
        Initialize bot.
        
        Args:
            config: Configuration object (BaseConfig or subclass)
        """
        self.config = config
        self.current_trade = None
        self.trade_history: List[BaseTrade] = []
        self.is_connected = False
        self.logger = self._setup_logger()
        self.last_data = None  # Store last fetched data
        
        # Hook lists for customization
        self._pre_signal_hooks: List[Callable] = []
        self._post_signal_hooks: List[Callable] = []
        self._pre_trade_hooks: List[Callable] = []
        self._post_trade_hooks: List[Callable] = []
        self._pre_cycle_hooks: List[Callable] = []
        self._post_cycle_hooks: List[Callable] = []
        
        self.logger.info(f"Initialized {self.__class__.__name__}")
    
    # ============================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ============================================================================
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal from market data.
        
        This is the core logic of your strategy. Analyze the dataframe
        and return a signal dictionary if conditions are met.
        
        Args:
            df: DataFrame with OHLCV data and indicators
        
        Returns:
            Dict with signal data if signal found, None otherwise
            
        Example:
            {
                'type': 'BUY',  # or 'SELL'
                'price': 1.1050,
                'atr': 0.0015,
                'confidence': 0.85,  # Optional
                'reason': 'Order Block + FVG alignment'  # Optional
            }
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy-specific indicators.
        
        Add your indicator columns to the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
            
        Example:
            df['rsi'] = talib.RSI(df['close'])
            df['sma'] = talib.SMA(df['close'], 20)
            return df
        """
        pass
    
    # ============================================================================
    # TEMPLATE METHODS - Define the algorithm structure
    # ============================================================================
    
    def run_cycle(self):
        """
        Main trading cycle - Template Method Pattern.
        
        This method defines the structure of one trading cycle:
        1. Validate conditions
        2. Execute pre-cycle hooks
        3. Fetch market data
        4. Generate signal
        5. Execute trade if conditions met
        6. Execute post-cycle hooks
        
        Override this method only if you need completely different flow.
        For most cases, override the abstract methods instead.
        """
        # Pre-cycle hooks
        self._execute_hooks(self._pre_cycle_hooks, {'bot': self})
        
        # Validate trading conditions
        if not self._validate_conditions():
            return
        
        # Get market data
        data = self.get_data()
        if data is None or len(data) == 0:
            self.logger.warning("No data available")
            return
        
        self.last_data = data
        
        # Calculate indicators
        try:
            data = self.calculate_indicators(data)
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return
        
        # Pre-signal hooks
        hook_data = {'data': data, 'bot': self}
        self._execute_hooks(self._pre_signal_hooks, hook_data)
        
        # Generate signal
        signal = self.generate_signal(data)
        
        if signal:
            # Post-signal hooks
            hook_data = {'signal': signal, 'data': data, 'bot': self}
            cancelled = self._execute_hooks(self._post_signal_hooks, hook_data)
            
            if cancelled:
                self.logger.info("Signal cancelled by hook")
                return
            
            # Check if should trade
            if self._should_trade(signal):
                # Pre-trade hooks
                hook_data = {'signal': signal, 'bot': self}
                cancelled = self._execute_hooks(self._pre_trade_hooks, hook_data)
                
                if not cancelled:
                    # Execute trade
                    self.open_position(signal)
                    
                    # Post-trade hooks
                    hook_data = {'signal': signal, 'trade': self.current_trade, 'bot': self}
                    self._execute_hooks(self._post_trade_hooks, hook_data)
        
        # Check and manage existing positions
        if self.current_trade is not None:
            self.check_and_move_sl_to_breakeven()
        
        # Post-cycle hooks
        self._execute_hooks(self._post_cycle_hooks, {'bot': self})
    
    # ============================================================================
    # CONCRETE METHODS - Common implementation (can be overridden)
    # ============================================================================
    
    def connect(self, login: int, password: str, server: str) -> bool:
        """
        Connect to MetaTrader 5.
        
        Args:
            login: MT5 account number
            password: MT5 account password
            server: MT5 server name
        
        Returns:
            True if connected successfully
        """
        if not mt5.initialize():
            self.logger.error("MT5 initialization failed")
            return False
        
        if not mt5.login(login, password=password, server=server):
            self.logger.error(f"Login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        self.is_connected = True
        account_info = mt5.account_info()
        self.logger.info(f"✅ Connected to MT5: {account_info.server}")
        self.logger.info(f"   Account: {account_info.login}, Balance: ${account_info.balance:.2f}")
        return True
    
    def get_data(self, bars: int = 500) -> Optional[pd.DataFrame]:
        """
        Get market data from MT5.
        
        Args:
            bars: Number of bars to fetch
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        rates = mt5.copy_rates_from_pos(
            self.config.symbol, 
            self.config.timeframe, 
            0, 
            bars
        )
        
        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            self.logger.error(f"Failed to get rates for {self.config.symbol}: {error}")
            
            # Try to enable symbol
            if not mt5.symbol_select(self.config.symbol, True):
                self.logger.error(f"Cannot enable symbol {self.config.symbol}")
                return None
            
            # Retry
            self.logger.info(f"Symbol {self.config.symbol} enabled, retrying...")
            rates = mt5.copy_rates_from_pos(
                self.config.symbol, 
                self.config.timeframe, 
                0, 
                bars
            )
            
            if rates is None or len(rates) == 0:
                self.logger.error("Still no data after enabling symbol")
                return None
        
        self.logger.debug(f"Loaded {len(rates)} bars for {self.config.symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df
    
    def open_position(self, signal: Dict) -> bool:
        """
        Open trading position based on signal.
        
        Opens dual orders:
        - Order 1: RR 1:1 (quick profit)
        - Order 2: Main RR ratio
        
        Args:
            signal: Signal dictionary from generate_signal()
        
        Returns:
            True if position opened successfully
        """
        if self.current_trade is not None:
            self.logger.warning("Already in a trade")
            return False
        
        signal_type = signal.get('type')
        entry_price = signal.get('price')
        atr = signal.get('atr', 0.0015)  # Default ATR
        
        # Calculate SL and TP
        if signal_type == 'BUY':
            direction = 1
            sl = entry_price - (2 * atr)
            tp1 = entry_price + (entry_price - sl)  # RR 1:1
            tp2 = entry_price + (self.config.rr_ratio * (entry_price - sl))  # Main RR
        else:  # SELL
            direction = -1
            sl = entry_price + (2 * atr)
            tp1 = entry_price - (sl - entry_price)  # RR 1:1
            tp2 = entry_price - (self.config.rr_ratio * (sl - entry_price))  # Main RR
        
        # Calculate position size
        volume = self.calculate_position_size(entry_price, sl)
        volume_per_order = volume / 2  # Split between 2 orders
        
        # Round volume
        volume_per_order = self._round_volume(volume_per_order)
        
        if volume_per_order <= 0:
            self.logger.error("Invalid volume calculated")
            return False
        
        # Send Order 1 (RR 1:1)
        ticket1 = self._send_order(signal_type, volume_per_order, entry_price, sl, tp1)
        if ticket1 is None:
            self.logger.error("Failed to open Order 1")
            return False
        
        # Send Order 2 (Main RR)
        ticket2 = self._send_order(signal_type, volume_per_order, entry_price, sl, tp2)
        if ticket2 is None:
            self.logger.error("Failed to open Order 2")
            # Close Order 1
            self._close_position(ticket1)
            return False
        
        # Create trade object
        trade_class = type(self.current_trade) if self.current_trade else BaseTrade
        self.current_trade = trade_class(
            entry_price=entry_price,
            stop_loss=sl,
            take_profit=tp2,  # Use main TP
            direction=direction,
            volume=volume,
            ticket=ticket2,  # Main ticket
            entry_time=datetime.now(),
            ticket1=ticket1,
            ticket2=ticket2,
            tp1_hit=False,
            sl_moved_to_breakeven=False
        )
        
        self.logger.info(f"✅ Opened {signal_type} position:")
        self.logger.info(f"   Order 1: Ticket #{ticket1}, TP={tp1:.5f} (RR 1:1)")
        self.logger.info(f"   Order 2: Ticket #{ticket2}, TP={tp2:.5f} (RR {self.config.rr_ratio}:1)")
        self.logger.info(f"   Entry={entry_price:.5f}, SL={sl:.5f}")
        
        return True
    
    def calculate_position_size(self, entry: float, sl: float) -> float:
        """
        Calculate position size based on risk.
        
        Args:
            entry: Entry price
            sl: Stop loss price
        
        Returns:
            Volume (lot size)
        """
        account_info = mt5.account_info()
        if account_info is None:
            self.logger.error("Failed to get account info")
            return 0.01
        
        balance = account_info.balance
        risk_amount = balance * (self.config.risk_percent / 100)
        
        # Get symbol info
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.error(f"Failed to get symbol info for {self.config.symbol}")
            return 0.01
        
        # Calculate pip value
        point = symbol_info.point
        pip_value = symbol_info.trade_tick_value
        
        # Calculate distance to SL in pips
        sl_distance_pips = abs(entry - sl) / point
        
        # Calculate volume
        volume = risk_amount / (sl_distance_pips * pip_value / 10)
        
        # Apply min/max limits
        volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))
        
        return volume
    
    def check_and_move_sl_to_breakeven(self):
        """Check if Order 1 hit TP and move Order 2's SL to breakeven"""
        if self.current_trade is None:
            return
        
        if not self.config.move_sl_to_breakeven:
            return
        
        if self.current_trade.sl_moved_to_breakeven:
            return
        
        # Check if Order 1 still exists
        position1 = mt5.positions_get(ticket=self.current_trade.ticket1)
        
        if position1 is None or len(position1) == 0:
            # Order 1 closed (TP hit)
            self.current_trade.tp1_hit = True
            self.logger.info(f"✅ Order 1 hit TP! Moving Order 2's SL to breakeven...")
            
            # Move Order 2's SL to breakeven
            new_sl = self.current_trade.entry_price
            success = self.modify_sl(self.current_trade.ticket2, new_sl)
            
            if success:
                self.current_trade.sl_moved_to_breakeven = True
                self.current_trade.stop_loss = new_sl
                self.logger.info(f"   ✅ SL moved to breakeven: {new_sl:.5f}")
            else:
                self.logger.error(f"   ❌ Failed to move SL to breakeven")
        
        # Check if Order 2 also closed
        position2 = mt5.positions_get(ticket=self.current_trade.ticket2)
        if position2 is None or len(position2) == 0:
            self.logger.info("Both orders closed, trade complete")
            self.trade_history.append(self.current_trade)
            self.current_trade = None
    
    def modify_sl(self, ticket: int, new_sl: float) -> bool:
        """Modify stop loss of an open position"""
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            return False
        
        position = position[0]
        
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": self.config.symbol,
            "sl": new_sl,
            "tp": position.tp,
            "magic": self.config.magic_number,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Failed to modify SL: {result.comment}")
            return False
        
        return True
    
    # ============================================================================
    # VALIDATION & FILTERING METHODS
    # ============================================================================
    
    def _validate_conditions(self) -> bool:
        """
        Validate trading conditions before cycle.
        
        Override to add custom validation logic.
        
        Returns:
            True if conditions are valid
        """
        if not self.is_connected:
            self.logger.warning("Not connected to MT5")
            return False
        
        if self.current_trade is not None:
            # Already in trade, just manage it
            return True
        
        # Check if max positions reached
        positions = mt5.positions_get(symbol=self.config.symbol)
        if positions and len(positions) >= self.config.max_positions:
            return False
        
        return True
    
    def _should_trade(self, signal: Dict) -> bool:
        """
        Determine if should execute trade.
        
        Override to add filters (time, volatility, news, etc.)
        
        Args:
            signal: Generated signal
        
        Returns:
            True if all filters pass
        """
        # Default: trade all signals
        # Override for custom filters
        return True
    
    # ============================================================================
    # HOOK MANAGEMENT
    # ============================================================================
    
    def add_pre_signal_hook(self, func: Callable):
        """Add function to run before signal generation"""
        self._pre_signal_hooks.append(func)
    
    def add_post_signal_hook(self, func: Callable):
        """Add function to run after signal generation"""
        self._post_signal_hooks.append(func)
    
    def add_pre_trade_hook(self, func: Callable):
        """Add function to run before opening trade"""
        self._pre_trade_hooks.append(func)
    
    def add_post_trade_hook(self, func: Callable):
        """Add function to run after opening trade"""
        self._post_trade_hooks.append(func)
    
    def add_pre_cycle_hook(self, func: Callable):
        """Add function to run before cycle starts"""
        self._pre_cycle_hooks.append(func)
    
    def add_post_cycle_hook(self, func: Callable):
        """Add function to run after cycle ends"""
        self._post_cycle_hooks.append(func)
    
    def _execute_hooks(self, hooks: List[Callable], data: Dict) -> bool:
        """
        Execute all hooks in list.
        
        Args:
            hooks: List of hook functions
            data: Data to pass to hooks
        
        Returns:
            True if any hook cancelled the operation
        """
        for hook in hooks:
            try:
                result = hook(data)
                # If hook returns False, cancel operation
                if result is False:
                    return True
            except Exception as e:
                self.logger.error(f"Error in hook {hook.__name__}: {e}")
        
        return False
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the bot"""
        logger_name = self.__class__.__name__
        logger = logging.getLogger(logger_name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(f'{logger_name.lower()}.log')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _send_order(self, order_type: str, volume: float, price: float, 
                    sl: float, tp: float) -> Optional[int]:
        """Send order to MT5"""
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.error(f"Symbol {self.config.symbol} not found")
            return None
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if order_type == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.config.magic_number,
            "comment": f"{self.__class__.__name__} order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order failed: {result.comment}")
            return None
        
        return result.order
    
    def _close_position(self, ticket: int) -> bool:
        """Close position by ticket"""
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            return False
        
        position = position[0]
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
            "deviation": 20,
            "magic": self.config.magic_number,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Failed to close position: {result.comment}")
            return False
        
        return True
    
    def _round_volume(self, volume: float) -> float:
        """Round volume to symbol's volume step"""
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            return round(volume, 2)
        
        volume_step = symbol_info.volume_step
        volume = round(volume / volume_step) * volume_step
        
        # Ensure within limits
        volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))
        
        return volume
    
    def shutdown(self):
        """Cleanup and shutdown"""
        self.logger.info(f"Shutting down {self.__class__.__name__}")
        mt5.shutdown()
        self.is_connected = False
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"symbol={self.config.symbol}, "
                f"timeframe={self.config.timeframe}, "
                f"risk={self.config.risk_percent}%)")
