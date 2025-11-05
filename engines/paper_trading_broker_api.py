"""
Paper Trading Broker API
=========================

API đầy đủ cho paper trading broker:
- Submit/Cancel/Modify orders
- Query positions và account
- Real-time market data integration
- Database storage
- Order matching engine

Author: QuantumTrader Team
Version: 2.0.0
Date: November 2025
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import logging
import threading
import time

from engines.order_matching_engine import (
    OrderMatchingEngine, Order, OrderType, OrderSide, 
    OrderStatus, TimeInForce, Fill
)
from engines.database_manager import DatabaseManager
from engines.supabase_database import SupabaseDatabase, SupabaseConfig
from engines.broker_simulator import Position


class PaperTradingBrokerAPI:
    """
    Paper Trading Broker API
    
    Chức năng đầy đủ:
    1. Nhận lệnh qua API
    2. Khớp lệnh dựa trên market data
    3. Lưu tất cả vào database
    4. Trả kết quả và trạng thái tài khoản
    """
    
    def __init__(self, 
                 initial_balance: float = 10000,
                 db_path: str = "data/paper_trading.db",
                 use_supabase: bool = False,
                 supabase_config: Optional[SupabaseConfig] = None,
                 auto_update: bool = True,
                 update_interval: int = 1):
        """
        Args:
            initial_balance: Starting balance
            db_path: SQLite database file path (if not using Supabase)
            use_supabase: Whether to use Supabase instead of SQLite
            supabase_config: Supabase configuration (required if use_supabase=True)
            auto_update: Auto update with live market data
            update_interval: Update interval in seconds
        """
        # Components
        self.matching_engine = OrderMatchingEngine()
        
        # Database - choose backend
        if use_supabase:
            if not supabase_config:
                raise ValueError("supabase_config required when use_supabase=True")
            self.logger = logging.getLogger('PaperTradingBrokerAPI')
            self.logger.info("☁️  Using Supabase cloud database")
            self.database = SupabaseDatabase(supabase_config)
            self.db_backend = 'supabase'
        else:
            self.logger = logging.getLogger('PaperTradingBrokerAPI')
            self.logger.info("📦 Using SQLite local database")
            self.database = DatabaseManager(db_path)
            self.db_backend = 'sqlite'
        
        # Account
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.margin_used = 0.0
        self.free_margin = initial_balance
        
        # Positions
        self.positions: Dict[str, Position] = {}
        self.order_counter = 0
        self.position_counter = 0
        
        # Auto update
        self.auto_update = auto_update
        self.update_interval = update_interval
        self._stop_update = False
        self._update_thread = None
        
        self.logger = logging.getLogger('PaperTradingBrokerAPI')
        self.logger.info("✅ Paper Trading Broker API initialized")
        
        if auto_update:
            self.start_auto_update()
    
    # ==================== PROPERTIES ====================
    
    @property
    def orders(self) -> Dict[str, Order]:
        """
        Get all pending orders
        
        Returns:
            Dictionary of pending orders {order_id: Order}
        """
        return self.matching_engine.pending_orders
    
    # ==================== ORDER MANAGEMENT ====================
    
    def submit_order(self, 
                    symbol: str,
                    order_type: str,
                    side: str,
                    quantity: float,
                    limit_price: Optional[float] = None,
                    stop_price: Optional[float] = None,
                    stop_loss: Optional[float] = None,
                    take_profit: Optional[float] = None,
                    time_in_force: str = "GTC") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit order to the paper trading broker
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD", "XAUUSD")
            order_type: Order type - "MARKET", "LIMIT", "STOP", "STOP_LIMIT"
            side: Order side - "BUY" or "SELL"
            quantity: Position size in lots (e.g., 0.1, 1.0)
            limit_price: Limit price (required for LIMIT/STOP_LIMIT orders)
            stop_price: Stop price (required for STOP/STOP_LIMIT orders)
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            time_in_force: Time in force - "GTC", "IOC", "FOK", "DAY" (default: "GTC")
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - success (bool): True if order submitted successfully
                - order_id (str): Order ID if successful, None if failed
                - error (str): Error message if failed, None if successful
        
        Example:
            >>> broker = PaperTradingBrokerAPI()
            >>> success, order_id, error = broker.submit_order(
            ...     symbol="EURUSD",
            ...     order_type="MARKET",
            ...     side="BUY",
            ...     quantity=0.1,
            ...     stop_loss=1.0950,
            ...     take_profit=1.1100
            ... )
            >>> if success:
            ...     print(f"Order submitted: {order_id}")
            ... else:
            ...     print(f"Error: {error}")
        """
        try:
            # Generate order ID
            self.order_counter += 1
            order_id = f"PAPER_{self.order_counter:08d}"
            
            # Create order
            order = Order(
                order_id=order_id,
                symbol=symbol,
                order_type=OrderType[order_type.upper()],
                side=OrderSide[side.upper()],
                quantity=quantity,
                limit_price=limit_price,
                stop_price=stop_price,
                time_in_force=TimeInForce[time_in_force.upper()]
            )
            
            # Submit to matching engine
            success, error = self.matching_engine.submit_order(order)
            
            if not success:
                self.logger.warning(f"Order rejected: {error}")
                return False, None, error
            
            # Save to database
            self.database.save_order(order)
            
            # If market order, try to match immediately
            if order.order_type == OrderType.MARKET:
                current_bar = self._get_current_market_data(symbol)
                if current_bar:
                    fills = self.matching_engine.process_market_data(current_bar)
                    self._process_fills(fills)
            
            self.logger.info(f"✅ Order submitted: {order_id}")
            return True, order_id, None
            
        except Exception as e:
            self.logger.error(f"Failed to submit order: {e}")
            return False, None, str(e)
    
    def cancel_order(self, order_id: str, reason: str = "User cancelled") -> bool:
        """
        Cancel order
        
        Args:
            order_id: Order ID to cancel
            reason: Cancellation reason
        
        Returns:
            success
        """
        try:
            success = self.matching_engine.cancel_order(order_id, reason)
            
            if success:
                # Update database
                order = self.matching_engine.get_order(order_id)
                if order:
                    self.database.update_order(order)
                
                self.logger.info(f"✅ Order cancelled: {order_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order: {e}")
            return False
    
    def modify_order(self, order_id: str, 
                    new_quantity: Optional[float] = None,
                    new_limit_price: Optional[float] = None,
                    new_stop_loss: Optional[float] = None,
                    new_take_profit: Optional[float] = None) -> bool:
        """
        Modify existing order
        
        Args:
            order_id: Order ID
            new_quantity: New quantity
            new_limit_price: New limit price
            new_stop_loss: New SL
            new_take_profit: New TP
        
        Returns:
            success
        """
        try:
            order = self.matching_engine.get_order(order_id)
            
            if not order:
                self.logger.warning(f"Order {order_id} not found")
                return False
            
            # Cannot modify filled orders
            if order.status == OrderStatus.FILLED:
                self.logger.warning(f"Cannot modify filled order {order_id}")
                return False
            
            # Update fields
            if new_quantity:
                order.quantity = new_quantity
                order.remaining_quantity = new_quantity - order.filled_quantity
            
            if new_limit_price:
                order.limit_price = new_limit_price
            
            # Update database
            self.database.update_order(order)
            
            self.logger.info(f"✅ Order modified: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to modify order: {e}")
            return False
    
    # ==================== POSITION MANAGEMENT ====================
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open positions
        
        Args:
            symbol: Filter by symbol (optional)
        
        Returns:
            List of position dicts
        """
        positions = []
        
        for pos in self.positions.values():
            if symbol and pos.symbol != symbol:
                continue
            
            positions.append({
                'position_id': pos.position_id,
                'symbol': pos.symbol,
                'direction': 'LONG' if pos.direction == 1 else 'SHORT',
                'lot_size': pos.lot_size,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'stop_loss': pos.stop_loss,
                'take_profit': pos.take_profit,
                'unrealized_pnl': pos.unrealized_pnl,
                'realized_pnl': pos.realized_pnl,
                'total_commission': pos.total_commission,
                'total_swap': pos.total_swap,
                'open_time': pos.open_time.isoformat() if pos.open_time else None,
                'days_held': pos.days_held
            })
        
        return positions
    
    def close_position(self, position_id: str, reason: str = "Manual close") -> bool:
        """
        Close position manually
        
        Args:
            position_id: Position ID
            reason: Close reason
        
        Returns:
            success
        """
        try:
            if position_id not in self.positions:
                self.logger.warning(f"Position {position_id} not found")
                return False
            
            pos = self.positions[position_id]
            
            # Get current price
            current_price = self._get_current_price(pos.symbol)
            
            # Close position
            self._close_position_internal(position_id, current_price, reason)
            
            self.logger.info(f"✅ Position closed: {position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close position: {e}")
            return False
    
    # ==================== ACCOUNT QUERIES ====================
    
    def get_account_info(self) -> Dict:
        """
        Get current account information
        
        Returns:
            Account info dict
        """
        return {
            'balance': self.balance,
            'equity': self.equity,
            'margin_used': self.margin_used,
            'free_margin': self.free_margin,
            'margin_level': (self.equity / self.margin_used * 100) if self.margin_used > 0 else 0,
            'num_positions': len(self.positions),
            'num_pending_orders': len(self.matching_engine.pending_orders),
            'total_realized_pnl': self.balance - self.initial_balance
        }
    
    def get_order_history(self, start_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get order history from database
        
        Args:
            start_date: Filter from date
        
        Returns:
            List of order dicts
        """
        orders = self.database.get_all_orders()
        
        result = []
        for order in orders:
            if start_date and order.created_time < start_date:
                continue
            
            result.append({
                'order_id': order.order_id,
                'symbol': order.symbol,
                'type': order.order_type.value,
                'side': order.side.value,
                'quantity': order.quantity,
                'filled_quantity': order.filled_quantity,
                'avg_fill_price': order.avg_fill_price,
                'status': order.status.value,
                'created_time': order.created_time.isoformat(),
                'filled_time': order.filled_time.isoformat() if order.filled_time else None
            })
        
        return result
    
    def get_trade_history(self) -> List[Dict]:
        """
        Get completed trades from database
        
        Returns:
            List of trade dicts
        """
        trades = self.database.get_all_trades()
        
        result = []
        for trade in trades:
            result.append({
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'entry_time': trade.entry_time.isoformat(),
                'exit_time': trade.exit_time.isoformat(),
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'lot_size': trade.lot_size,
                'gross_pnl': trade.gross_pnl,
                'net_pnl': trade.net_pnl,
                'commission': trade.commission,
                'swap': trade.swap,
                'exit_reason': trade.exit_reason
            })
        
        return result
    
    # ==================== AUTO UPDATE ====================
    
    def start_auto_update(self):
        """Start auto update with live market data"""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._stop_update = False
            self._update_thread = threading.Thread(target=self._auto_update_loop, daemon=True)
            self._update_thread.start()
            self.logger.info("🔄 Auto update started")
    
    def stop_auto_update(self):
        """Stop auto update"""
        self._stop_update = True
        if self._update_thread:
            self._update_thread.join(timeout=5)
        self.logger.info("⏸️ Auto update stopped")
    
    def _auto_update_loop(self):
        """Auto update loop - runs in background thread"""
        while not self._stop_update:
            try:
                # Get symbols from pending orders and positions
                symbols = set()
                
                for order in self.matching_engine.pending_orders.values():
                    symbols.add(order.symbol)
                
                for pos in self.positions.values():
                    symbols.add(pos.symbol)
                
                # Update each symbol
                for symbol in symbols:
                    bar = self._get_current_market_data(symbol)
                    if bar:
                        # Process orders
                        fills = self.matching_engine.process_market_data(bar)
                        self._process_fills(fills)
                        
                        # Update positions
                        self._update_positions(symbol, bar)
                
                # Save account snapshot
                self.database.save_account_snapshot(self.get_account_info())
                
                # Sleep
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Auto update error: {e}")
                time.sleep(self.update_interval)
    
    # ==================== INTERNAL METHODS ====================
    
    def _get_current_market_data(self, symbol: str) -> Optional[Dict]:
        """Get current market data from MT5"""
        try:
            # Get latest tick
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                return None
            
            # Get last bar
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
            if rates is None or len(rates) == 0:
                return None
            
            bar = {
                'time': datetime.now(),
                'open': rates[0]['open'],
                'high': rates[0]['high'],
                'low': rates[0]['low'],
                'close': tick.last,
                'tick_volume': rates[0]['tick_volume'],
                'bid': tick.bid,
                'ask': tick.ask
            }
            
            return bar
            
        except Exception as e:
            self.logger.error(f"Failed to get market data for {symbol}: {e}")
            return None
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price"""
        tick = mt5.symbol_info_tick(symbol)
        return tick.last if tick else 0.0
    
    def _process_fills(self, fills: List[Fill]):
        """Process fills and create positions"""
        for fill in fills:
            # Save fill to database
            self.database.save_fill(fill)
            
            # Get order
            order = self.matching_engine.get_order(fill.order_id)
            if not order:
                continue
            
            # Update order in database
            self.database.update_order(order)
            
            # Create or update position
            if order.status == OrderStatus.FILLED:
                self._create_position_from_fill(order, fill)
    
    def _create_position_from_fill(self, order: Order, fill: Fill):
        """Create position from filled order"""
        self.position_counter += 1
        position_id = f"POS_{self.position_counter:08d}"
        
        # Get SL/TP from order if available
        stop_loss = getattr(order, 'stop_loss', None)
        take_profit = getattr(order, 'take_profit', None)
        
        # Create position
        position = Position(
            position_id=position_id,
            symbol=order.symbol,
            direction=order.side.value,
            lot_size=order.filled_quantity,
            entry_price=order.avg_fill_price,
            current_price=order.avg_fill_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            total_commission=sum(f.commission for f in order.fills),
            open_time=datetime.now()
        )
        
        self.positions[position_id] = position
        
        # Save to database
        self.database.save_position(position)
        
        self.logger.info(f"📊 Position opened: {position_id}")
    
    def _update_positions(self, symbol: str, bar: Dict):
        """Update positions for symbol"""
        for pos in list(self.positions.values()):
            if pos.symbol != symbol:
                continue
            
            # Update current price
            pos.current_price = bar['close']
            
            # Calculate unrealized P&L
            if pos.direction == 'BUY':
                pos.unrealized_pnl = (pos.current_price - pos.entry_price) * pos.lot_size * 100000  # Standard lot
            else:  # SELL
                pos.unrealized_pnl = (pos.entry_price - pos.current_price) * pos.lot_size * 100000
            
            # Check Stop Loss
            if pos.stop_loss:
                sl_hit = False
                slippage = 0.0
                
                if pos.direction == 'BUY' and bar['low'] <= pos.stop_loss:
                    # SL hit on buy position
                    sl_hit = True
                    # Simulate slippage (1-2 pips worse)
                    import random
                    slippage = random.uniform(0.0001, 0.0002)
                    exit_price = pos.stop_loss - slippage
                    
                elif pos.direction == 'SELL' and bar['high'] >= pos.stop_loss:
                    # SL hit on sell position
                    sl_hit = True
                    slippage = random.uniform(0.0001, 0.0002)
                    exit_price = pos.stop_loss + slippage
                
                if sl_hit:
                    self.logger.info(f"🛑 Stop Loss hit: {pos.position_id} at {exit_price}")
                    self._close_position_internal(pos.position_id, exit_price, "Stop Loss")
                    continue
            
            # Check Take Profit
            if pos.take_profit:
                tp_hit = False
                slippage = 0.0
                
                if pos.direction == 'BUY' and bar['high'] >= pos.take_profit:
                    # TP hit on buy position
                    tp_hit = True
                    # Favorable slippage (0-1 pip better)
                    import random
                    slippage = random.uniform(0, 0.0001)
                    exit_price = pos.take_profit + slippage
                    
                elif pos.direction == 'SELL' and bar['low'] <= pos.take_profit:
                    # TP hit on sell position
                    tp_hit = True
                    slippage = random.uniform(0, 0.0001)
                    exit_price = pos.take_profit - slippage
                
                if tp_hit:
                    self.logger.info(f"🎯 Take Profit hit: {pos.position_id} at {exit_price}")
                    self._close_position_internal(pos.position_id, exit_price, "Take Profit")
                    continue
    
    def _close_position_internal(self, position_id: str, exit_price: float, reason: str):
        """Internal position close"""
        pos = self.positions[position_id]
        
        # Calculate P&L
        # Standard lot size = 100,000 units
        lot_multiplier = 100000
        
        # Calculate gross P&L
        if pos.direction == 'BUY':
            gross_pnl = (exit_price - pos.entry_price) * pos.lot_size * lot_multiplier
        else:  # SELL
            gross_pnl = (pos.entry_price - exit_price) * pos.lot_size * lot_multiplier
        
        # Get symbol info for pip calculation
        symbol_info = mt5.symbol_info(pos.symbol)
        if symbol_info:
            point = symbol_info.point
        else:
            # Fallback for common symbols
            if 'JPY' in pos.symbol:
                point = 0.01  # JPY pairs
            else:
                point = 0.0001  # Most pairs
        
        # Calculate spread cost
        tick = mt5.symbol_info_tick(pos.symbol)
        if tick:
            spread = (tick.ask - tick.bid) * pos.lot_size * lot_multiplier
        else:
            # Estimate 2 pips spread
            spread = 2 * point * pos.lot_size * lot_multiplier
        
        # Calculate total costs
        total_commission = pos.total_commission
        total_swap = pos.total_swap
        total_costs = total_commission + total_swap + spread
        
        # Net P&L
        net_pnl = gross_pnl - total_costs
        
        # Update position
        pos.exit_price = exit_price
        pos.exit_time = datetime.now()
        pos.realized_pnl = gross_pnl
        pos.net_pnl = net_pnl
        pos.exit_reason = reason
        
        # Update account balance
        self.balance += net_pnl
        self.equity = self.balance
        
        # Update database
        self.database.close_position(position_id, exit_price, reason)
        
        # Save as completed trade
        from engines.database_manager import Trade
        trade = Trade(
            trade_id=position_id.replace('POS_', 'TRADE_'),
            symbol=pos.symbol,
            direction=pos.direction,
            entry_time=pos.open_time,
            exit_time=pos.exit_time,
            entry_price=pos.entry_price,
            exit_price=pos.exit_price,
            lot_size=pos.lot_size,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            commission=total_commission,
            swap=total_swap,
            exit_reason=reason
        )
        self.database.save_trade(trade)
        
        # Log result
        pnl_str = f"+${net_pnl:.2f}" if net_pnl > 0 else f"-${abs(net_pnl):.2f}"
        self.logger.info(f"📊 Position closed: {position_id} | {reason} | P&L: {pnl_str}")
        
        # Remove from active positions
        del self.positions[position_id]


# Example usage
if __name__ == "__main__":
    """
    Test Paper Trading Broker API
    """
    logging.basicConfig(level=logging.INFO)
    
    # Initialize MT5
    if not mt5.initialize():
        print("MT5 initialization failed")
        exit()
    
    # Create broker
    broker = PaperTradingBrokerAPI(
        initial_balance=10000,
        db_path="data/test_paper_trading.db",
        auto_update=False  # Manual control for testing
    )
    
    # Submit market order
    success, order_id, error = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1
    )
    
    print(f"Order submitted: {success}, ID: {order_id}")
    
    # Get account info
    account = broker.get_account_info()
    print(f"Account: {account}")
    
    # Get positions
    positions = broker.get_positions()
    print(f"Positions: {positions}")
    
    mt5.shutdown()
