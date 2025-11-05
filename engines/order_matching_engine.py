"""
Advanced Order Matching Engine
================================

Xử lý khớp lệnh dựa trên:
- Loại lệnh: Market, Limit, Stop, Stop-Limit
- Dữ liệu thị trường: OHLC, Volume, Bid/Ask
- Khớp một phần (Partial Fill) dựa trên volume
- Thời gian hiệu lực: GTC, IOC, FOK, DAY

Author: QuantumTrader Team
Version: 2.0.0
Date: November 2025
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from enum import Enum
import logging


class OrderType(Enum):
    """Loại lệnh"""
    MARKET = "MARKET"           # Khớp ngay tại giá thị trường
    LIMIT = "LIMIT"             # Khớp ở giá limit hoặc tốt hơn
    STOP = "STOP"               # Kích hoạt thành market khi chạm stop
    STOP_LIMIT = "STOP_LIMIT"   # Kích hoạt thành limit khi chạm stop


class OrderSide(Enum):
    """Hướng lệnh"""
    BUY = 1
    SELL = -1


class OrderStatus(Enum):
    """Trạng thái lệnh"""
    PENDING = "PENDING"                 # Chờ khớp
    PARTIAL_FILLED = "PARTIAL_FILLED"   # Khớp một phần
    FILLED = "FILLED"                   # Khớp hoàn toàn
    CANCELLED = "CANCELLED"             # Đã hủy
    REJECTED = "REJECTED"               # Bị từ chối
    EXPIRED = "EXPIRED"                 # Hết hạn


class TimeInForce(Enum):
    """Thời gian hiệu lực"""
    GTC = "GTC"  # Good Till Cancelled - Hiệu lực đến khi hủy
    IOC = "IOC"  # Immediate Or Cancel - Khớp ngay hoặc hủy
    FOK = "FOK"  # Fill Or Kill - Khớp toàn bộ hoặc hủy
    DAY = "DAY"  # Day order - Hiệu lực trong ngày


@dataclass
class Fill:
    """Thông tin khớp lệnh"""
    fill_id: str
    order_id: str
    fill_time: datetime
    fill_price: float
    fill_volume: float
    commission: float
    is_partial: bool
    remaining_volume: float
    
    # Market data at fill
    market_price: float
    bid: float
    ask: float
    volume: int


@dataclass
class Order:
    """Lệnh giao dịch nâng cao"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float                          # Số lượng yêu cầu
    
    # Price parameters
    limit_price: Optional[float] = None      # Giá limit (cho LIMIT/STOP_LIMIT)
    stop_price: Optional[float] = None       # Giá stop (cho STOP/STOP_LIMIT)
    
    # Time parameters
    time_in_force: TimeInForce = TimeInForce.GTC
    created_time: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Status tracking
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    avg_fill_price: float = 0.0
    
    # Fills history
    fills: List[Fill] = field(default_factory=list)
    
    # Metadata
    rejection_reason: Optional[str] = None
    cancelled_reason: Optional[str] = None
    
    def __post_init__(self):
        self.remaining_quantity = self.quantity
    
    @property
    def is_buy(self) -> bool:
        return self.side == OrderSide.BUY
    
    @property
    def is_sell(self) -> bool:
        return self.side == OrderSide.SELL
    
    @property
    def fill_percentage(self) -> float:
        """Phần trăm đã khớp"""
        if self.quantity == 0:
            return 0
        return (self.filled_quantity / self.quantity) * 100


class OrderMatchingEngine:
    """
    Engine khớp lệnh thông minh
    
    Chức năng:
    1. Khớp market orders ngay lập tức
    2. Khớp limit orders khi giá thị trường chạm limit
    3. Kích hoạt stop orders khi giá chạm stop
    4. Xử lý partial fills dựa trên volume
    5. Respect time in force
    """
    
    def __init__(self):
        self.logger = logging.getLogger('OrderMatchingEngine')
        self.pending_orders: Dict[str, Order] = {}
        self.filled_orders: List[Order] = []
        self.cancelled_orders: List[Order] = []
        self.fill_counter = 0
        
    def submit_order(self, order: Order) -> Tuple[bool, Optional[str]]:
        """
        Nhận lệnh mới
        
        Returns:
            (success, error_message)
        """
        # Validate order
        is_valid, error = self._validate_order(order)
        if not is_valid:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = error
            return False, error
        
        # Add to pending orders
        self.pending_orders[order.order_id] = order
        self.logger.info(f"📝 Order {order.order_id} submitted: {order.side.name} {order.quantity} {order.symbol} @ {order.order_type.name}")
        
        return True, None
    
    def cancel_order(self, order_id: str, reason: str = "User cancelled") -> bool:
        """
        Hủy lệnh
        
        Returns:
            success
        """
        if order_id not in self.pending_orders:
            self.logger.warning(f"Order {order_id} not found")
            return False
        
        order = self.pending_orders[order_id]
        
        # Cannot cancel filled orders
        if order.status == OrderStatus.FILLED:
            self.logger.warning(f"Cannot cancel filled order {order_id}")
            return False
        
        # Mark as cancelled
        order.status = OrderStatus.CANCELLED
        order.cancelled_reason = reason
        
        # Move to cancelled list
        self.cancelled_orders.append(order)
        del self.pending_orders[order_id]
        
        self.logger.info(f"❌ Order {order_id} cancelled: {reason}")
        return True
    
    def process_market_data(self, bar: Dict) -> List[Fill]:
        """
        Xử lý bar dữ liệu mới, cố gắng khớp pending orders
        
        Args:
            bar: {
                'time': datetime,
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'tick_volume': int,
                'bid': float (optional),
                'ask': float (optional)
            }
        
        Returns:
            List of fills that occurred
        """
        fills = []
        current_time = bar.get('time', datetime.now())
        
        # Check for expired orders
        self._expire_orders(current_time)
        
        # Process each pending order
        orders_to_remove = []
        
        for order_id, order in list(self.pending_orders.items()):
            # Try to match order
            order_fills = self._try_match_order(order, bar)
            
            if order_fills:
                fills.extend(order_fills)
            
            # Check if order is complete or should be removed
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.EXPIRED]:
                orders_to_remove.append(order_id)
                
                if order.status == OrderStatus.FILLED:
                    self.filled_orders.append(order)
        
        # Remove completed orders
        for order_id in orders_to_remove:
            if order_id in self.pending_orders:
                del self.pending_orders[order_id]
        
        return fills
    
    def _try_match_order(self, order: Order, bar: Dict) -> List[Fill]:
        """
        Cố gắng khớp một lệnh với bar data hiện tại
        
        Returns:
            List of fills (có thể empty)
        """
        if order.order_type == OrderType.MARKET:
            return self._match_market_order(order, bar)
        
        elif order.order_type == OrderType.LIMIT:
            return self._match_limit_order(order, bar)
        
        elif order.order_type == OrderType.STOP:
            return self._match_stop_order(order, bar)
        
        elif order.order_type == OrderType.STOP_LIMIT:
            return self._match_stop_limit_order(order, bar)
        
        return []
    
    def _match_market_order(self, order: Order, bar: Dict) -> List[Fill]:
        """
        Khớp market order ngay lập tức tại giá thị trường
        
        Market order luôn khớp (trừ khi volume quá thấp)
        """
        # Get execution price
        if order.is_buy:
            # BUY: Phải trả ask price
            fill_price = bar.get('ask', bar['close'] + 0.0001)  # Default spread
        else:
            # SELL: Nhận bid price
            fill_price = bar.get('bid', bar['close'] - 0.0001)
        
        # Check if enough volume
        available_volume = bar.get('tick_volume', 1000)
        
        # Determine fill quantity
        if order.time_in_force == TimeInForce.FOK:
            # Fill Or Kill: Phải khớp toàn bộ hoặc không khớp
            if order.remaining_quantity > available_volume:
                self.logger.warning(f"FOK order {order.order_id} cannot be filled (insufficient volume)")
                order.status = OrderStatus.CANCELLED
                order.cancelled_reason = "FOK: Insufficient volume"
                return []
            fill_quantity = order.remaining_quantity
        
        elif order.time_in_force == TimeInForce.IOC:
            # Immediate Or Cancel: Khớp nhiều nhất có thể, hủy phần còn lại
            fill_quantity = min(order.remaining_quantity, available_volume)
            if fill_quantity < order.remaining_quantity:
                order.status = OrderStatus.CANCELLED
                order.cancelled_reason = "IOC: Partial fill, remaining cancelled"
        
        else:  # GTC or DAY
            # Khớp nhiều nhất có thể
            fill_quantity = min(order.remaining_quantity, available_volume)
        
        # Create fill
        fill = self._create_fill(order, bar, fill_price, fill_quantity)
        
        self.logger.info(f"✅ Market order {order.order_id} filled: {fill_quantity} @ {fill_price:.5f}")
        
        return [fill]
    
    def _match_limit_order(self, order: Order, bar: Dict) -> List[Fill]:
        """
        Khớp limit order khi giá thị trường chạm limit price
        
        BUY LIMIT: Khớp khi market price <= limit price
        SELL LIMIT: Khớp khi market price >= limit price
        """
        # Check if limit price is touched
        if order.is_buy:
            # BUY LIMIT: Chờ giá xuống <= limit
            if bar['low'] <= order.limit_price:
                # Price touched limit
                fill_price = order.limit_price  # Khớp tại limit price
                
                # Check volume
                available_volume = bar.get('tick_volume', 1000)
                fill_quantity = min(order.remaining_quantity, available_volume)
                
                fill = self._create_fill(order, bar, fill_price, fill_quantity)
                self.logger.info(f"✅ BUY LIMIT {order.order_id} filled: {fill_quantity} @ {fill_price:.5f}")
                
                return [fill]
        
        else:  # SELL
            # SELL LIMIT: Chờ giá lên >= limit
            if bar['high'] >= order.limit_price:
                fill_price = order.limit_price
                
                available_volume = bar.get('tick_volume', 1000)
                fill_quantity = min(order.remaining_quantity, available_volume)
                
                fill = self._create_fill(order, bar, fill_price, fill_quantity)
                self.logger.info(f"✅ SELL LIMIT {order.order_id} filled: {fill_quantity} @ {fill_price:.5f}")
                
                return [fill]
        
        return []
    
    def _match_stop_order(self, order: Order, bar: Dict) -> List[Fill]:
        """
        Stop order: Kích hoạt thành market order khi giá chạm stop
        
        BUY STOP: Kích hoạt khi giá >= stop (breakout lên)
        SELL STOP: Kích hoạt khi giá <= stop (breakdown xuống)
        """
        triggered = False
        
        if order.is_buy:
            # BUY STOP: Giá phải >= stop price
            if bar['high'] >= order.stop_price:
                triggered = True
        else:
            # SELL STOP: Giá phải <= stop price
            if bar['low'] <= order.stop_price:
                triggered = True
        
        if triggered:
            self.logger.info(f"🔔 STOP order {order.order_id} triggered at {order.stop_price:.5f}")
            
            # Convert to market order
            order.order_type = OrderType.MARKET
            return self._match_market_order(order, bar)
        
        return []
    
    def _match_stop_limit_order(self, order: Order, bar: Dict) -> List[Fill]:
        """
        Stop-Limit order: Kích hoạt thành limit order khi chạm stop
        
        2 bước:
        1. Chờ giá chạm stop price → Kích hoạt
        2. Sau khi kích hoạt → Trở thành limit order
        """
        # Check if stop is triggered
        triggered = False
        
        if order.is_buy:
            if bar['high'] >= order.stop_price:
                triggered = True
        else:
            if bar['low'] <= order.stop_price:
                triggered = True
        
        if triggered:
            self.logger.info(f"🔔 STOP-LIMIT order {order.order_id} triggered, converting to LIMIT")
            
            # Convert to limit order
            order.order_type = OrderType.LIMIT
            return self._match_limit_order(order, bar)
        
        return []
    
    def _create_fill(self, order: Order, bar: Dict, fill_price: float, fill_quantity: float) -> Fill:
        """
        Tạo fill record và cập nhật order
        """
        self.fill_counter += 1
        fill_id = f"FILL_{self.fill_counter:08d}"
        
        # Calculate commission (simplified)
        commission = fill_quantity * 7.0  # $7 per lot
        
        # Create fill
        fill = Fill(
            fill_id=fill_id,
            order_id=order.order_id,
            fill_time=bar.get('time', datetime.now()),
            fill_price=fill_price,
            fill_volume=fill_quantity,
            commission=commission,
            is_partial=(fill_quantity < order.remaining_quantity),
            remaining_volume=order.remaining_quantity - fill_quantity,
            market_price=bar['close'],
            bid=bar.get('bid', bar['close'] - 0.0001),
            ask=bar.get('ask', bar['close'] + 0.0001),
            volume=bar.get('tick_volume', 0)
        )
        
        # Update order
        order.fills.append(fill)
        order.filled_quantity += fill_quantity
        order.remaining_quantity -= fill_quantity
        
        # Update average fill price
        total_value = sum(f.fill_price * f.fill_volume for f in order.fills)
        order.avg_fill_price = total_value / order.filled_quantity
        
        # Update status
        if order.remaining_quantity <= 0:
            order.status = OrderStatus.FILLED
            self.logger.info(f"🎉 Order {order.order_id} fully filled at avg price {order.avg_fill_price:.5f}")
        else:
            order.status = OrderStatus.PARTIAL_FILLED
            self.logger.info(f"⏳ Order {order.order_id} partial filled: {order.fill_percentage:.1f}%")
        
        return fill
    
    def _validate_order(self, order: Order) -> Tuple[bool, Optional[str]]:
        """Validate order parameters"""
        
        # Check quantity
        if order.quantity <= 0:
            return False, "Invalid quantity"
        
        # Check limit price for LIMIT orders
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            if order.limit_price is None or order.limit_price <= 0:
                return False, "Invalid limit price"
        
        # Check stop price for STOP orders
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if order.stop_price is None or order.stop_price <= 0:
                return False, "Invalid stop price"
        
        # Check expiry for DAY orders
        if order.time_in_force == TimeInForce.DAY and order.expires_at is None:
            # Set expiry to end of day
            order.expires_at = datetime.now().replace(hour=23, minute=59, second=59)
        
        return True, None
    
    def _expire_orders(self, current_time: datetime):
        """Check and expire orders that have passed their expiry time"""
        
        for order in list(self.pending_orders.values()):
            if order.expires_at and current_time > order.expires_at:
                order.status = OrderStatus.EXPIRED
                self.logger.info(f"⏰ Order {order.order_id} expired")
                
                if order.status == OrderStatus.PARTIAL_FILLED:
                    # Partial fill before expiry
                    self.logger.info(f"   Filled {order.fill_percentage:.1f}% before expiry")
                
                self.cancelled_orders.append(order)
    
    def get_order_book(self) -> Dict[str, List[Order]]:
        """
        Get current order book
        
        Returns:
            {
                'pending': [...],
                'filled': [...],
                'cancelled': [...]
            }
        """
        return {
            'pending': list(self.pending_orders.values()),
            'filled': self.filled_orders,
            'cancelled': self.cancelled_orders
        }
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        
        # Check pending
        if order_id in self.pending_orders:
            return self.pending_orders[order_id]
        
        # Check filled
        for order in self.filled_orders:
            if order.order_id == order_id:
                return order
        
        # Check cancelled
        for order in self.cancelled_orders:
            if order.order_id == order_id:
                return order
        
        return None
    
    def get_statistics(self) -> Dict:
        """Get matching engine statistics"""
        
        total_orders = len(self.pending_orders) + len(self.filled_orders) + len(self.cancelled_orders)
        
        return {
            'total_orders': total_orders,
            'pending_orders': len(self.pending_orders),
            'filled_orders': len(self.filled_orders),
            'cancelled_orders': len(self.cancelled_orders),
            'fill_rate': (len(self.filled_orders) / total_orders * 100) if total_orders > 0 else 0,
            'total_fills': self.fill_counter,
            'partial_fills': sum(1 for o in self.filled_orders if len(o.fills) > 1)
        }


# Example usage
if __name__ == "__main__":
    """
    Test Order Matching Engine
    """
    logging.basicConfig(level=logging.INFO)
    
    engine = OrderMatchingEngine()
    
    # Submit BUY LIMIT order
    buy_limit = Order(
        order_id="ORD_001",
        symbol="EURUSD",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=1.0,
        limit_price=1.1000
    )
    
    success, error = engine.submit_order(buy_limit)
    print(f"Submit result: {success}")
    
    # Simulate market data
    bar1 = {
        'time': datetime.now(),
        'open': 1.1020,
        'high': 1.1025,
        'low': 1.1015,
        'close': 1.1018,
        'tick_volume': 500,
        'bid': 1.1017,
        'ask': 1.1019
    }
    
    fills = engine.process_market_data(bar1)
    print(f"Bar 1 fills: {len(fills)}")
    
    # Price drops to limit
    bar2 = {
        'time': datetime.now(),
        'open': 1.1018,
        'high': 1.1020,
        'low': 1.0998,  # Touch limit!
        'close': 1.1005,
        'tick_volume': 800,
        'bid': 1.1004,
        'ask': 1.1006
    }
    
    fills = engine.process_market_data(bar2)
    print(f"Bar 2 fills: {len(fills)}")
    
    if fills:
        fill = fills[0]
        print(f"Filled at: {fill.fill_price:.5f}, Quantity: {fill.fill_volume}")
    
    # Get statistics
    stats = engine.get_statistics()
    print(f"\nStatistics: {stats}")
