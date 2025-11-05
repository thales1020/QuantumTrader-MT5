"""
Supabase Database Integration
==============================

Production-ready cloud database using Supabase (PostgreSQL)

Features:
- Real-time data sync
- Cloud storage
- REST API auto-generated
- Row Level Security
- Multi-device access
- Automatic backups

Author: QuantumTrader Team
Version: 2.0.0
Date: November 2025
"""

from supabase import create_client, Client
from datetime import datetime
from typing import List, Dict, Optional, Callable
import logging
import os


def _to_isoformat(value) -> Optional[str]:
    """
    Helper function to convert datetime to ISO format string
    Handles both datetime objects and strings
    
    Args:
        value: datetime object, string, or None
        
    Returns:
        ISO format string or None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value  # Already a string
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)  # Fallback


class SupabaseConfig:
    """Supabase configuration"""
    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and KEY required. Set SUPABASE_URL and SUPABASE_KEY "
                "environment variables or pass to constructor."
            )


class SupabaseDatabase:
    """
    Supabase Database Manager
    
    Handles all database operations with Supabase cloud PostgreSQL
    
    Features:
    - CRUD operations for all tables
    - Real-time subscriptions
    - Automatic sync across devices
    - Cloud backup
    """
    
    def __init__(self, config: SupabaseConfig):
        """
        Initialize Supabase client
        
        Args:
            config: SupabaseConfig with URL and KEY
        """
        self.config = config
        self.client: Client = create_client(config.url, config.key)
        self.logger = logging.getLogger('SupabaseDatabase')
        self.logger.info(f"✅ Connected to Supabase: {config.url[:30]}...")
        
        # Real-time subscriptions
        self.subscriptions = []
    
    # ==================== ORDERS ====================
    
    def save_order(self, order_data: Dict) -> Dict:
        """
        Save order to Supabase
        
        Args:
            order_data: Order dictionary
        
        Returns:
            Inserted order with ID
        """
        try:
            response = self.client.table('orders').insert({
                'order_id': order_data['order_id'],
                'symbol': order_data['symbol'],
                'order_type': order_data['order_type'],
                'side': order_data['side'],
                'quantity': order_data['quantity'],
                'limit_price': order_data.get('limit_price'),
                'stop_price': order_data.get('stop_price'),
                'avg_fill_price': order_data.get('avg_fill_price', 0.0),
                'status': order_data['status'],
                'filled_quantity': order_data.get('filled_quantity', 0.0),
                'remaining_quantity': order_data.get('remaining_quantity', order_data['quantity']),
                'created_time': _to_isoformat(order_data.get('created_time', datetime.now())),
                'filled_time': _to_isoformat(order_data.get('filled_time')),
                'cancelled_time': _to_isoformat(order_data.get('cancelled_time')),
                'expires_at': _to_isoformat(order_data.get('expires_at')),
                'rejection_reason': order_data.get('rejection_reason'),
                'cancelled_reason': order_data.get('cancelled_reason'),
                'strategy_name': order_data.get('strategy_name')
            }).execute()
            
            self.logger.debug(f"💾 Saved order to Supabase: {order_data['order_id']}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to save order to Supabase: {e}")
            raise
    
    def update_order(self, order_id: str, updates: Dict) -> bool:
        """
        Update order in Supabase
        
        Args:
            order_id: Order ID
            updates: Fields to update
        
        Returns:
            Success
        """
        try:
            # Convert datetime objects to ISO format
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = _to_isoformat(value)
            
            response = self.client.table('orders').update(updates).eq('order_id', order_id).execute()
            
            self.logger.debug(f"📝 Updated order in Supabase: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update order in Supabase: {e}")
            return False
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order by ID"""
        try:
            response = self.client.table('orders').select('*').eq('order_id', order_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"Failed to get order: {e}")
            return None
    
    def get_all_orders(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get all orders, optionally filtered by status
        
        Args:
            status: Filter by status (PENDING, FILLED, CANCELLED, etc.)
            limit: Maximum number of orders to return
        
        Returns:
            List of order dicts
        """
        try:
            query = self.client.table('orders').select('*')
            
            if status:
                query = query.eq('status', status)
            
            response = query.order('created_time', desc=True).limit(limit).execute()
            return response.data
            
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []
    
    # ==================== FILLS ====================
    
    def save_fill(self, fill_data: Dict) -> Dict:
        """Save fill to Supabase"""
        try:
            response = self.client.table('fills').insert({
                'fill_id': fill_data['fill_id'],
                'order_id': fill_data['order_id'],
                'fill_time': _to_isoformat(fill_data.get('fill_time', datetime.now())),
                'fill_price': fill_data['fill_price'],
                'fill_volume': fill_data['fill_volume'],
                'commission': fill_data.get('commission', 0.0),
                'is_partial': fill_data.get('is_partial', False),
                'remaining_volume': fill_data.get('remaining_volume', 0.0),
                'market_price': fill_data.get('market_price'),
                'bid': fill_data.get('bid'),
                'ask': fill_data.get('ask'),
                'volume': fill_data.get('volume', 0)
            }).execute()
            
            self.logger.debug(f"💾 Saved fill to Supabase: {fill_data['fill_id']}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to save fill: {e}")
            raise
    
    def get_fills_by_order(self, order_id: str) -> List[Dict]:
        """Get all fills for an order"""
        try:
            response = self.client.table('fills').select('*').eq('order_id', order_id).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get fills: {e}")
            return []
    
    # ==================== POSITIONS ====================
    
    def save_position(self, position_data: Dict) -> Dict:
        """Save position to Supabase"""
        try:
            response = self.client.table('positions').insert({
                'position_id': position_data['position_id'],
                'symbol': position_data['symbol'],
                'side': position_data['side'],
                'quantity': position_data['quantity'],
                'entry_price': position_data['entry_price'],
                'current_price': position_data.get('current_price', position_data['entry_price']),
                'exit_price': position_data.get('exit_price'),
                'stop_loss': position_data.get('stop_loss'),
                'take_profit': position_data.get('take_profit'),
                'is_open': position_data.get('is_open', True),
                'unrealized_pnl': position_data.get('unrealized_pnl', 0.0),
                'realized_pnl': position_data.get('realized_pnl', 0.0),
                'total_commission': position_data.get('total_commission', 0.0),
                'total_swap': position_data.get('total_swap', 0.0),
                'spread_cost': position_data.get('spread_cost', 0.0),
                'open_time': _to_isoformat(position_data.get('open_time', datetime.now())),
                'close_time': _to_isoformat(position_data.get('close_time')),
                'days_held': position_data.get('days_held', 0),
                'exit_reason': position_data.get('exit_reason'),
                'strategy_name': position_data.get('strategy_name')
            }).execute()
            
            self.logger.debug(f"💾 Saved position to Supabase: {position_data['position_id']}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to save position: {e}")
            raise
    
    def update_position(self, position_id: str, updates: Dict) -> bool:
        """Update position"""
        try:
            # Convert datetime objects
            for key, value in updates.items():
                if isinstance(value, datetime):
                    updates[key] = _to_isoformat(value)
            
            response = self.client.table('positions').update(updates).eq('position_id', position_id).execute()
            
            self.logger.debug(f"📝 Updated position: {position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update position: {e}")
            return False
    
    def close_position(self, position_id: str, exit_price: float, exit_reason: str) -> bool:
        """Close position"""
        return self.update_position(position_id, {
            'is_open': False,
            'exit_price': exit_price,
            'close_time': datetime.now(),
            'exit_reason': exit_reason
        })
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            response = self.client.table('positions').select('*').eq('is_open', True).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get open positions: {e}")
            return []
    
    def get_position_by_id(self, position_id: str) -> Optional[Dict]:
        """Get position by ID"""
        try:
            response = self.client.table('positions').select('*').eq('position_id', position_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"Failed to get position: {e}")
            return None
    
    # ==================== TRADES ====================
    
    def save_trade(self, trade_data: Dict) -> Dict:
        """Save completed trade to Supabase"""
        try:
            response = self.client.table('trades').insert({
                'trade_id': trade_data['trade_id'],
                'symbol': trade_data['symbol'],
                'direction': trade_data['direction'],
                'entry_time': _to_isoformat(trade_data.get('entry_time', datetime.now())),
                'exit_time': _to_isoformat(trade_data.get('exit_time', datetime.now())),
                'entry_price': trade_data['entry_price'],
                'exit_price': trade_data['exit_price'],
                'lot_size': trade_data['lot_size'],
                'gross_pnl': trade_data['gross_pnl'],
                'commission': trade_data.get('commission', 0.0),
                'swap': trade_data.get('swap', 0.0),
                'spread_cost': trade_data.get('spread_cost', 0.0),
                'slippage': trade_data.get('slippage', 0.0),
                'net_pnl': trade_data['net_pnl'],
                'pips': trade_data.get('pips'),
                'duration_hours': trade_data.get('duration_hours'),
                'exit_reason': trade_data.get('exit_reason'),
                'balance_after': trade_data.get('balance_after'),
                'equity_after': trade_data.get('equity_after'),
                'drawdown_pct': trade_data.get('drawdown_pct', 0.0),
                'strategy_name': trade_data.get('strategy_name')
            }).execute()
            
            self.logger.debug(f"💾 Saved trade to Supabase: Trade #{trade_data['trade_id']}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to save trade: {e}")
            raise
    
    def get_all_trades(self, limit: int = 100) -> List[Dict]:
        """Get all completed trades"""
        try:
            response = self.client.table('trades').select('*').order('exit_time', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get trades: {e}")
            return []
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """Get trades for specific symbol"""
        try:
            response = self.client.table('trades').select('*').eq('symbol', symbol).order('exit_time', desc=True).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get trades for {symbol}: {e}")
            return []
    
    # ==================== ACCOUNT HISTORY ====================
    
    def save_account_snapshot(self, account_data: Dict) -> Dict:
        """Save account snapshot"""
        try:
            response = self.client.table('account_history').insert({
                'timestamp': _to_isoformat(account_data.get('timestamp', datetime.now())),
                'balance': account_data['balance'],
                'equity': account_data['equity'],
                'margin_used': account_data.get('margin_used', 0.0),
                'free_margin': account_data.get('free_margin', 0.0),
                'margin_level': account_data.get('margin_level', 0.0),
                'num_positions': account_data.get('num_positions', 0),
                'num_pending_orders': account_data.get('num_pending_orders', 0),
                'daily_pnl': account_data.get('daily_pnl', 0.0),
                'daily_return_pct': account_data.get('daily_return_pct', 0.0),
                'total_realized_pnl': account_data.get('total_realized_pnl', 0.0),
                'total_trades': account_data.get('total_trades', 0),
                'total_commission_paid': account_data.get('total_commission_paid', 0.0),
                'drawdown_usd': account_data.get('drawdown_usd', 0.0),
                'drawdown_pct': account_data.get('drawdown_pct', 0.0)
            }).execute()
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to save account snapshot: {e}")
            raise
    
    def get_account_history(self, days: Optional[int] = None, start_date: Optional[datetime] = None, limit: int = 1000) -> List[Dict]:
        """
        Get account history
        
        Args:
            days: Number of days to look back (convenience parameter)
            start_date: Specific start date (overrides days parameter)
            limit: Maximum records to return
        """
        try:
            query = self.client.table('account_history').select('*')
            
            # Handle days parameter
            if days and not start_date:
                from datetime import timedelta
                start_date = datetime.now() - timedelta(days=days)
            
            if start_date:
                query = query.gte('timestamp', _to_isoformat(start_date))
            
            response = query.order('timestamp', desc=False).limit(limit).execute()
            return response.data
            
        except Exception as e:
            self.logger.error(f"Failed to get account history: {e}")
            return []
    
    # ==================== REAL-TIME SUBSCRIPTIONS ====================
    
    def subscribe_to_trades(self, callback: Callable[[Dict], None]):
        """
        Subscribe to real-time trade updates
        
        Args:
            callback: Function to call when new trade is inserted
        """
        def handle_trade_insert(payload):
            self.logger.info(f"🔔 Real-time trade update: {payload['new']}")
            callback(payload['new'])
        
        subscription = self.client.table('trades').on('INSERT', handle_trade_insert).subscribe()
        self.subscriptions.append(subscription)
        self.logger.info("✅ Subscribed to real-time trades")
    
    def subscribe_to_positions(self, callback: Callable[[Dict], None]):
        """
        Subscribe to real-time position updates
        
        Args:
            callback: Function to call when position is updated
        """
        def handle_position_update(payload):
            self.logger.info(f"🔔 Real-time position update: {payload['new']}")
            callback(payload['new'])
        
        subscription = self.client.table('positions').on('UPDATE', handle_position_update).subscribe()
        self.subscriptions.append(subscription)
        self.logger.info("✅ Subscribed to real-time positions")
    
    def unsubscribe_all(self):
        """Unsubscribe from all real-time channels"""
        for sub in self.subscriptions:
            sub.unsubscribe()
        self.subscriptions.clear()
        self.logger.info("⏸️ Unsubscribed from all real-time channels")
    
    # ==================== ANALYTICS ====================
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            # Count records in each table
            orders_count = len(self.client.table('orders').select('id', count='exact').execute().data)
            trades_count = len(self.client.table('trades').select('id', count='exact').execute().data)
            positions_count = len(self.client.table('positions').select('id', count='exact').execute().data)
            
            # Get filled orders
            filled_orders = len(
                self.client.table('orders').select('id').eq('status', 'FILLED').execute().data
            )
            
            # Get open positions
            open_positions = len(
                self.client.table('positions').select('id').eq('is_open', True).execute().data
            )
            
            return {
                'total_orders': orders_count,
                'filled_orders': filled_orders,
                'total_trades': trades_count,
                'total_positions': positions_count,
                'open_positions': open_positions
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary from trades"""
        try:
            trades = self.get_all_trades(limit=10000)
            
            if not trades:
                return {}
            
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['net_pnl'] > 0])
            total_pnl = sum(t['net_pnl'] for t in trades)
            total_commission = sum(t['commission'] for t in trades)
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                'total_pnl': total_pnl,
                'total_commission': total_commission,
                'avg_pnl_per_trade': total_pnl / total_trades if total_trades > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    """
    Test Supabase Database
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize
    config = SupabaseConfig(
        url="https://your-project.supabase.co",
        key="your-anon-key"
    )
    
    db = SupabaseDatabase(config)
    
    # Test save order
    order_data = {
        'order_id': 'TEST_001',
        'symbol': 'EURUSD',
        'order_type': 'MARKET',
        'side': 'BUY',
        'quantity': 1.0,
        'status': 'PENDING',
        'created_time': datetime.now()
    }
    
    result = db.save_order(order_data)
    print(f"Saved order: {result}")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
